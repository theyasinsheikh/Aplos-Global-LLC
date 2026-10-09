import base64
import hashlib
import hmac
import os
import secrets
import smtplib
import asyncio
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest, urlopen
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from uuid import UUID
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from gridfs import AsyncGridFSBucket
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()

MAX_RESUME_BYTES = 5 * 1024 * 1024
VISITOR_HEARTBEAT_INTERVAL_SECONDS = 30
VISITOR_ACTIVE_WINDOW_SECONDS = 90
VISITOR_TTL_SECONDS = 120
SIGNUP_CODE_TTL_SECONDS = 600
SIGNUP_CODE_RESEND_SECONDS = 60
SIGNUP_CODE_MAX_ATTEMPTS = 5
AUTH_SESSION_SECRET = os.getenv("AUTH_SESSION_SECRET") or secrets.token_urlsafe(48)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI is required. Set it in backend/.env.")

    client = AsyncMongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command("ping")
        database = client[os.getenv("MONGODB_DATABASE", "aplos_global")]
        await database.subscribers.create_index("email", unique=True)
        await database.candidate_accounts.create_index("email", unique=True)
        await database.pending_candidate_signups.create_index("email", unique=True)
        await database.pending_candidate_signups.create_index("expires_at", expireAfterSeconds=0)
        await database.active_visitors.create_index("visitor_id", unique=True)
        await database.active_visitors.create_index(
            "last_seen",
            expireAfterSeconds=VISITOR_TTL_SECONDS,
        )
        app.state.mongo_client = client
        app.state.database = database
        app.state.resume_bucket = AsyncGridFSBucket(database, bucket_name="resumes")
        yield
    finally:
        await client.close()


app = FastAPI(
    title="Aplos Global API",
    description="Backend API for Aplos Global services.",
    version="1.0.0",
    lifespan=lifespan,
)

oauth = OAuth()
for provider, discovery_url in (
    ("google", "https://accounts.google.com/.well-known/openid-configuration"),
    ("apple", "https://appleid.apple.com/.well-known/openid-configuration"),
):
    client_id = os.getenv(f"{provider.upper()}_CLIENT_ID")
    client_secret = os.getenv(f"{provider.upper()}_CLIENT_SECRET")
    if client_id and client_secret:
        oauth.register(
            name=provider,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=discovery_url,
            client_kwargs={"scope": "openid email name" if provider == "apple" else "openid email profile"},
        )

app.add_middleware(
    SessionMiddleware,
    secret_key=AUTH_SESSION_SECRET,
    session_cookie="aplos_session",
    max_age=60 * 60 * 24 * 7,
    same_site="none",
    https_only=os.getenv("AUTH_COOKIE_SECURE", "true").lower() == "true",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/candidates/oauth/{provider}")
async def start_candidate_oauth(provider: str, request: Request):
    if provider not in {"google", "apple"}:
        raise HTTPException(status_code=404, detail="Unknown sign-in provider.")
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=503, detail=f"{provider.title()} sign-in is not configured.")
    if not os.getenv("AUTH_SESSION_SECRET"):
        raise HTTPException(status_code=503, detail="Set AUTH_SESSION_SECRET before enabling sign-in.")
    if os.getenv("AUTH_COOKIE_SECURE", "false").lower() != "true":
        raise HTTPException(status_code=503, detail="Enable secure auth cookies before enabling sign-in.")
    callback_url = os.getenv(
        f"{provider.upper()}_REDIRECT_URI",
        str(request.url_for("candidate_oauth_callback", provider=provider)),
    )
    extra_params = {"response_mode": "form_post"} if provider == "apple" else {}
    return await client.authorize_redirect(request, callback_url, **extra_params)


@app.get("/api/candidates/oauth/{provider}/callback", name="candidate_oauth_callback")
@app.post("/api/candidates/oauth/{provider}/callback")
async def candidate_oauth_callback(provider: str, request: Request):
    if provider not in {"google", "apple"}:
        raise HTTPException(status_code=404, detail="Unknown sign-in provider.")
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=503, detail=f"{provider.title()} sign-in is not configured.")
    try:
        token = await client.authorize_access_token(request)
        profile = token.get("userinfo") or await client.parse_id_token(request, token)
    except (OAuthError, ValueError) as error:
        raise HTTPException(status_code=400, detail="Could not verify the provider sign-in.") from error

    email = str(profile.get("email", "")).strip().lower()
    if not email or profile.get("email_verified") not in (True, "true"):
        raise HTTPException(status_code=400, detail="The provider did not return a verified email address.")
    account = await request.app.state.database.candidate_accounts.find_one_and_update(
        {"email": email},
        {"$addToSet": {"oauth_providers": provider}},
        return_document=True,
    )
    frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    if not account:
        return RedirectResponse(
            f"{frontend_url}/candidate-portal?oauth=signup-with-codes",
            status_code=303,
        )
    request.session.clear()
    request.session["candidate_id"] = str(account["_id"])
    return RedirectResponse(f"{frontend_url}/candidate-portal?login=success", status_code=303)


@app.get("/api/candidates/me")
async def get_candidate_session(request: Request):
    candidate_id = request.session.get("candidate_id")
    if not candidate_id or not ObjectId.is_valid(candidate_id):
        raise HTTPException(status_code=401, detail="Sign in required.")
    account = await request.app.state.database.candidate_accounts.find_one(
        {"_id": ObjectId(candidate_id)}, {"password_hash": 0}
    )
    if not account:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Sign in required.")
    return account


@app.post("/api/candidates/logout", status_code=204)
async def logout_candidate(request: Request) -> None:
    request.session.clear()


class SubscriptionRequest(BaseModel):
    email: EmailStr


class SubscriptionResponse(BaseModel):
    success: bool
    message: str


class CandidateSignupRequest(BaseModel):
    given_name: str = Field(min_length=1, max_length=80)
    surname: str = Field(min_length=1, max_length=80)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=32)
    nationality: str | None = Field(default=None, max_length=80)
    residence_country: str | None = Field(default=None, max_length=80)
    preferred_country: str | None = Field(default=None, max_length=80)
    passport_number: str = Field(min_length=4, max_length=32)
    visa_type: Literal["Student Visa", "Work Permit Visa", "Visit Visa"]
    password: str = Field(min_length=12, max_length=128)

    @field_validator("given_name", "surname")
    @classmethod
    def strip_candidate_name_parts(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name fields cannot be blank.")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_candidate_phone(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith("+"):
            raise ValueError("Phone number must include its country code, starting with +.")
        digits = normalized[1:].replace(" ", "").replace("-", "")
        if not digits.isdigit() or not 7 <= len(digits) <= 15:
            raise ValueError("Enter a valid phone number with country code.")
        return normalized

    @field_validator("nationality", "residence_country", "preferred_country")
    @classmethod
    def strip_candidate_country_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @field_validator("password")
    @classmethod
    def require_non_whitespace_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password cannot be blank.")
        return value

    @field_validator("passport_number")
    @classmethod
    def normalize_passport_number(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Passport number cannot be blank.")
        return normalized


class CandidateSignupVerificationRequest(CandidateSignupRequest):
    email_code: str = Field(pattern=r"^\d{6}$")
    phone_code: str = Field(pattern=r"^\d{6}$")


class CandidateSignupResponse(BaseModel):
    success: bool
    message: str


class CandidateLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class VisitorHeartbeatRequest(BaseModel):
    visitor_id: UUID


class LiveVisitorCountResponse(BaseModel):
    count: int
    active_within_seconds: int


class ContactInquiryRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    nationality: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=40)
    service: str = Field(min_length=2, max_length=100)
    message: str = Field(min_length=10, max_length=4000)

    @field_validator("first_name", "last_name", "service", "message")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("nationality", "phone")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ContactInquiryResponse(BaseModel):
    success: bool
    message: str


class JobApplicationRequest(BaseModel):
    job_title: str = Field(min_length=2, max_length=160)
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=40)
    nationality: str | None = Field(default=None, max_length=80)
    message: str = Field(min_length=10, max_length=3000)
    consent: bool

    @field_validator("job_title", "first_name", "last_name", "phone", "message")
    @classmethod
    def strip_required_application_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("nationality")
    @classmethod
    def strip_nationality(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @field_validator("consent")
    @classmethod
    def require_application_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Consent is required to submit an application.")
        return value


class JobApplicationResponse(BaseModel):
    success: bool
    message: str


async def store_pdf_upload(
    request: Request,
    upload: UploadFile,
    stored_filename: str,
) -> ObjectId:
    if not upload.filename or not upload.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload your CV as a PDF file.")

    content = await upload.read(MAX_RESUME_BYTES + 1)
    if len(content) > MAX_RESUME_BYTES:
        raise HTTPException(status_code=413, detail="CV file must be 5 MB or smaller.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    return await request.app.state.resume_bucket.upload_from_stream(
        stored_filename,
        content,
        metadata={"contentType": "application/pdf"},
    )


def hash_signup_code(destination: str, code: str) -> str:
    return hmac.new(
        AUTH_SESSION_SECRET.encode("utf-8"),
        f"{destination}:{code}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def send_signup_email_code(recipient: str, code: str) -> None:
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("SMTP_FROM")
    if not host or not sender:
        raise RuntimeError("Email code delivery is not configured.")
    message = EmailMessage()
    message["Subject"] = "Your Aplos Global verification code"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        f"Your Aplos Global email verification code is {code}. "
        f"It expires in 10 minutes. If you did not request this, ignore this email."
    )
    port = int(os.getenv("SMTP_PORT", "587"))
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=15) as server:
            username = os.getenv("SMTP_USER")
            if username:
                server.login(username, os.getenv("SMTP_PASSWORD", ""))
            server.send_message(message)
        return
    with smtplib.SMTP(host, port, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        username = os.getenv("SMTP_USER")
        if username:
            server.login(username, os.getenv("SMTP_PASSWORD", ""))
        server.send_message(message)


def send_signup_sms_code(phone: str, code: str) -> None:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sender = os.getenv("TWILIO_FROM")
    if not account_sid or not auth_token or not sender:
        raise RuntimeError("SMS code delivery is not configured.")
    clean_phone = phone.replace(" ", "").replace("-", "")
    endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    body = urlencode({
        "To": clean_phone,
        "From": sender,
        "Body": f"Your Aplos Global verification code is {code}. It expires in 10 minutes.",
    }).encode("utf-8")
    credentials = base64.b64encode(
        f"{account_sid}:{auth_token}".encode("utf-8")
    ).decode("ascii")
    request = UrlRequest(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        if response.status >= 400:
            raise RuntimeError("SMS provider rejected the verification message.")


@app.get("/api/health")
async def health(request: Request) -> dict[str, str]:
    await request.app.state.mongo_client.admin.command("ping")
    return {"status": "ok", "service": "aplos-global-backend", "database": "connected"}


@app.post("/api/visitors/heartbeat", status_code=204)
async def record_visitor_heartbeat(
    payload: VisitorHeartbeatRequest,
    request: Request,
) -> None:
    visitor_id = str(payload.visitor_id)
    last_seen = datetime.now(timezone.utc)
    try:
        await request.app.state.database.active_visitors.update_one(
            {"visitor_id": visitor_id},
            {
                "$set": {"last_seen": last_seen},
                "$setOnInsert": {"visitor_id": visitor_id},
            },
            upsert=True,
        )
    except DuplicateKeyError:
        await request.app.state.database.active_visitors.update_one(
            {"visitor_id": visitor_id},
            {"$set": {"last_seen": last_seen}},
        )


@app.get("/api/visitors/live", response_model=LiveVisitorCountResponse)
async def get_live_visitor_count(request: Request) -> LiveVisitorCountResponse:
    active_since = datetime.now(timezone.utc) - timedelta(
        seconds=VISITOR_ACTIVE_WINDOW_SECONDS
    )
    count = await request.app.state.database.active_visitors.count_documents(
        {"last_seen": {"$gte": active_since}}
    )
    return LiveVisitorCountResponse(
        count=count,
        active_within_seconds=VISITOR_ACTIVE_WINDOW_SECONDS,
    )


@app.post(
    "/api/subscribe",
    response_model=SubscriptionResponse,
    status_code=201,
)
async def subscribe(
    payload: SubscriptionRequest,
    request: Request,
) -> SubscriptionResponse:
    email = str(payload.email).strip().lower()
    try:
        await request.app.state.database.subscribers.update_one(
            {"email": email},
            {
                "$setOnInsert": {
                    "email": email,
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
    except DuplicateKeyError:
        # A concurrent request may insert the same address after the upsert check.
        pass

    return SubscriptionResponse(
        success=True,
        message="Subscription request saved.",
    )


@app.post(
    "/api/candidates/signup/send-codes",
    response_model=CandidateSignupResponse,
    status_code=200,
)
async def send_candidate_signup_codes(
    payload: CandidateSignupRequest,
    request: Request,
) -> CandidateSignupResponse:
    delivery_settings = (
        "SMTP_HOST", "SMTP_FROM", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM"
    )
    if any(not os.getenv(setting) for setting in delivery_settings):
        raise HTTPException(
            status_code=503,
            detail="Email and SMS verification are not configured. Set SMTP and Twilio credentials first.",
        )
    email = str(payload.email).strip().lower()
    phone = payload.phone.strip()
    if await request.app.state.database.candidate_accounts.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    pending_collection = request.app.state.database.pending_candidate_signups
    existing = await pending_collection.find_one({"email": email})
    now = datetime.now(timezone.utc)
    previous_send = existing.get("last_sent_at") if existing else None
    if previous_send and previous_send.tzinfo is None:
        previous_send = previous_send.replace(tzinfo=timezone.utc)
    if previous_send and (now - previous_send).total_seconds() < SIGNUP_CODE_RESEND_SECONDS:
        raise HTTPException(status_code=429, detail="Please wait one minute before requesting new codes.")

    email_code = f"{secrets.randbelow(1_000_000):06d}"
    phone_code = f"{secrets.randbelow(1_000_000):06d}"
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        payload.password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64
    )
    registration = payload.model_dump(exclude={"password"})
    registration["email"] = email
    registration["phone"] = phone
    registration["password_hash"] = f"scrypt$16384$8$1${salt.hex()}${password_hash.hex()}"
    pending = {
        "email": email,
        "phone": phone,
        "registration": registration,
        "email_code_hash": hash_signup_code(email, email_code),
        "phone_code_hash": hash_signup_code(phone, phone_code),
        "attempts": 0,
        "last_sent_at": now,
        "expires_at": now + timedelta(seconds=SIGNUP_CODE_TTL_SECONDS),
    }
    await pending_collection.replace_one({"email": email}, pending, upsert=True)
    try:
        await asyncio.gather(
            asyncio.to_thread(send_signup_email_code, email, email_code),
            asyncio.to_thread(send_signup_sms_code, phone, phone_code),
        )
    except Exception as error:
        await pending_collection.delete_one({"email": email})
        raise HTTPException(
            status_code=503,
            detail="Could not send verification codes. Check SMTP and Twilio settings, then try again.",
        ) from error

    return CandidateSignupResponse(
        success=True,
        message="Verification codes were sent to your email and phone. They expire in 10 minutes.",
    )


@app.post(
    "/api/candidates/signup",
    response_model=CandidateSignupResponse,
    status_code=201,
)
async def signup_candidate(
    payload: CandidateSignupVerificationRequest,
    request: Request,
) -> CandidateSignupResponse:
    email = str(payload.email).strip().lower()
    phone = payload.phone.strip()
    pending_collection = request.app.state.database.pending_candidate_signups
    pending = await pending_collection.find_one({"email": email, "phone": phone})
    now = datetime.now(timezone.utc)
    expires_at = pending.get("expires_at") if pending else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not pending or not expires_at or expires_at <= now:
        if pending:
            await pending_collection.delete_one({"_id": pending["_id"]})
        raise HTTPException(status_code=400, detail="Verification codes expired. Request new codes.")
    if pending["attempts"] >= SIGNUP_CODE_MAX_ATTEMPTS:
        await pending_collection.delete_one({"_id": pending["_id"]})
        raise HTTPException(status_code=429, detail="Too many incorrect codes. Request new codes.")
    email_verified = hmac.compare_digest(
        pending["email_code_hash"], hash_signup_code(email, payload.email_code)
    )
    phone_verified = hmac.compare_digest(
        pending["phone_code_hash"], hash_signup_code(phone, payload.phone_code)
    )
    if not email_verified or not phone_verified:
        await pending_collection.update_one({"_id": pending["_id"]}, {"$inc": {"attempts": 1}})
        raise HTTPException(status_code=400, detail="Email or phone verification code is incorrect.")

    registration = pending["registration"]
    try:
        await request.app.state.database.candidate_accounts.insert_one(
            {
                "name": f"{registration['given_name']} {registration['surname']}",
                "given_name": registration["given_name"],
                "surname": registration["surname"],
                "email": email,
                "email_verified": True,
                "phone": phone,
                "phone_verified": True,
                "nationality": registration["nationality"],
                "residence_country": registration["residence_country"],
                "preferred_country": registration["preferred_country"],
                "passport_number": registration["passport_number"],
                "visa_type": registration["visa_type"],
                "password_hash": registration["password_hash"],
                "created_at": now,
                "status": "active",
            }
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        ) from None
    await pending_collection.delete_one({"_id": pending["_id"]})

    return CandidateSignupResponse(
        success=True,
        message="Your candidate account has been created.",
    )


@app.post("/api/candidates/login")
async def login_candidate(payload: CandidateLoginRequest, request: Request):
    email = str(payload.email).strip().lower()
    account = await request.app.state.database.candidate_accounts.find_one({"email": email})
    stored_hash = account.get("password_hash") if account else None
    authenticated = False
    if stored_hash:
        try:
            algorithm, n, r, p, salt_hex, digest_hex = stored_hash.split("$")
            if algorithm == "scrypt":
                candidate_hash = hashlib.scrypt(
                    payload.password.encode("utf-8"),
                    salt=bytes.fromhex(salt_hex),
                    n=int(n),
                    r=int(r),
                    p=int(p),
                    dklen=len(bytes.fromhex(digest_hex)),
                )
                authenticated = hmac.compare_digest(candidate_hash.hex(), digest_hex)
        except (ValueError, TypeError):
            authenticated = False
    if not authenticated or not account or account.get("status") != "active":
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    request.session.clear()
    request.session["candidate_id"] = str(account["_id"])
    return {"success": True, "message": "Signed in successfully."}


@app.post(
    "/api/contact",
    response_model=ContactInquiryResponse,
    status_code=201,
)
async def create_contact_inquiry(
    request: Request,
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    service: Annotated[str, Form()],
    message: Annotated[str, Form()],
    nationality: Annotated[str | None, Form()] = None,
    phone: Annotated[str | None, Form()] = None,
    cv: Annotated[UploadFile | None, File(description="Optional PDF CV, up to 5 MB")] = None,
) -> ContactInquiryResponse:
    try:
        payload = ContactInquiryRequest.model_validate(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "service": service,
                "message": message,
                "nationality": nationality,
                "phone": phone,
            }
        )
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=error.errors(include_context=False),
        ) from error

    inquiry = payload.model_dump()
    inquiry["name"] = f"{payload.first_name} {payload.last_name}"
    inquiry["email"] = str(payload.email).strip().lower()
    inquiry["created_at"] = datetime.now(timezone.utc)
    inquiry["status"] = "new"
    cv_id = None
    if cv is not None and cv.filename:
        try:
            cv_id = await store_pdf_upload(request, cv, "contact-cv.pdf")
            inquiry["cv_id"] = cv_id
            inquiry["cv_filename"] = "contact-cv.pdf"
        finally:
            await cv.close()

    try:
        await request.app.state.database.contact_inquiries.insert_one(inquiry)
    except Exception:
        if cv_id is not None:
            await request.app.state.resume_bucket.delete(cv_id)
        raise

    return ContactInquiryResponse(
        success=True,
        message="Your inquiry has been received. Our team will contact you soon.",
    )


@app.post(
    "/api/apply",
    response_model=JobApplicationResponse,
    status_code=201,
)
async def create_job_application(
    request: Request,
    job_title: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    message: Annotated[str, Form()],
    consent: Annotated[bool, Form()],
    nationality: Annotated[str | None, Form()] = None,
    resume: Annotated[UploadFile | None, File(description="Optional PDF CV, up to 5 MB")] = None,
) -> JobApplicationResponse:
    try:
        payload = JobApplicationRequest.model_validate(
            {
                "job_title": job_title,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "message": message,
                "consent": consent,
                "nationality": nationality,
            }
        )
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=error.errors(include_context=False),
        ) from error

    application = payload.model_dump()
    application["name"] = f"{payload.first_name} {payload.last_name}"
    application["email"] = str(payload.email).strip().lower()
    submitted_at = datetime.now(timezone.utc)
    application["created_at"] = submitted_at
    application["consent_given_at"] = submitted_at
    application["status"] = "new"

    resume_id = None
    if resume is not None and resume.filename:
        try:
            resume_id = await store_pdf_upload(request, resume, "resume.pdf")
            application["resume_id"] = resume_id
            application["resume_filename"] = "resume.pdf"
        finally:
            await resume.close()

    try:
        await request.app.state.database.job_applications.insert_one(application)
    except Exception:
        if resume_id is not None:
            await request.app.state.resume_bucket.delete(resume_id)
        raise

    return JobApplicationResponse(
        success=True,
        message="Your application has been received.",
    )
