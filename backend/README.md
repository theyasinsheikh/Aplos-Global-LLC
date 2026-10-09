# Aplos Global FastAPI backend

The backend uses FastAPI and MongoDB. Newsletter subscriptions are saved in the
`subscribers` collection, with a unique index on normalized email addresses.
Candidate accounts are stored separately with a unique normalized email index;
passwords are stored only as salted scrypt hashes.
Visible browser sessions send a heartbeat every 30 seconds. The API counts a
visitor as active for 90 seconds after the last heartbeat; visitor identifiers
are random session IDs and expire from MongoDB after 120 seconds.

## Run on Windows

From the `backend` directory, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `MONGO_URI` in `.env` to your MongoDB connection string. The example points
to MongoDB running locally on the default port. Start your local MongoDB server
before starting the API. If the MongoDB Windows service is unavailable, you can
run an installed `mongod.exe` using a project-local data directory:

```powershell
New-Item -ItemType Directory -Force .mongodb | Out-Null
& 'C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe' --dbpath .mongodb --bind_ip 127.0.0.1 --port 27017
```

Keep that terminal open. In another terminal, start the API:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 4000
```

## Endpoints

- `GET /api/health` checks API and MongoDB connectivity.
- `POST /api/visitors/heartbeat` records a visible browser session heartbeat.
  The request body is `{"visitor_id":"<UUID>"}`.
- `GET /api/visitors/live` returns the number of visitors active in the last
  90 seconds. It returns a count only, not visitor identifiers or personal
  details.
- `POST /api/subscribe` accepts `{"email":"person@example.com"}` and saves the
  address to MongoDB. Repeated submissions are safe and do not create duplicate
  records.
- `POST /api/candidates/signup` accepts a candidate's given name, surname,
  email, phone number with country code, password (12–128 characters), optional
  nationality, residence country, and preferred destination country, and one
  visa type (`Student Visa`, `Work Permit Visa`, or `Visit Visa`). It creates an
  account in `candidate_accounts`. Passwords are scrypt-hashed before storage;
  duplicate email addresses return HTTP 409.
- `POST /api/contact` accepts contact details and saves new inquiries to the
  `contact_inquiries` collection.
- `POST /api/apply` accepts a candidate's contact details, consent, and an
  optional PDF CV (maximum 5 MB). Applications are stored in `job_applications`;
  uploaded CV files are stored in the MongoDB GridFS `resumes` bucket.
- `GET /docs` opens the interactive API documentation.

The frontend currently displays clearly marked sample job listings. Replace
these with verified vacancies before publishing. The application form requires
candidate consent before submission.

## Google and Apple sign-in

Install the updated backend requirements and copy the OAuth settings from
`.env.example` into `.env`. Generate a long random `AUTH_SESSION_SECRET`, set
`AUTH_COOKIE_SECURE=true`, and set `FRONTEND_BASE_URL` to the deployed site.
Register these callback URLs with each provider:

- `https://YOUR_API_HOST/api/candidates/oauth/google/callback`
- `https://YOUR_API_HOST/api/candidates/oauth/apple/callback`

Set the matching client IDs and secrets in `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`, `APPLE_CLIENT_ID`, and `APPLE_CLIENT_SECRET`. Apple
client secrets are JWTs generated from the Sign in with Apple key, team ID, and
key ID in the Apple Developer account. Apple web sign-in requires an HTTPS
domain registered with Apple; localhost is not accepted as its return URL.
Keep provider secrets and the session secret server-side only.

The backend starts provider sign-in at `/api/candidates/oauth/google` or
`/api/candidates/oauth/apple`; it verifies the provider ID token, creates or
signs in a candidate account using the verified email, and sets an HTTP-only
signed session cookie. `GET /api/candidates/me` returns the current account,
and `POST /api/candidates/logout` clears the session.

## Candidate email and phone verification

Candidate signup sends separate six-digit codes through SMTP email and Twilio
SMS. Both codes must be entered within 10 minutes before an account is created.
Codes can be requested once per minute and expire after five incorrect attempts.
Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`,
`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM` in `backend/.env`.
The API refuses signup if either delivery service is not configured or cannot
send its code.
