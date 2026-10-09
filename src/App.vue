<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'

const navItems = ref([
  { label: 'Home', active: true },
  { label: 'About', active: false },
  { label: 'Services', active: false },
  { label: 'Offices', active: false },
  { label: 'Career', active: false },
  { label: 'Contact', active: false }
])

const mobileOpen = ref(false)
const isFindJobsPage = ref(window.location.pathname === '/find-jobs')
const isAboutPage = ref(window.location.pathname === '/about' || window.location.pathname === '/about.html')
const isCandidatePortalPage = ref(window.location.pathname === '/candidate-portal')
const isEmployerPortalPage = ref(window.location.pathname === '/employer-portal')

const jobs = ref([
  {
    id: 'bakery-technician',
    title: 'Bakery Production Technician',
    industry: 'Food Production',
    location: 'Leeds, United Kingdom',
    country: 'United Kingdom',
    type: 'Full-time',
    salary: 'Discussed during hiring',
    posted: 'Example listing',
    description: 'Support daily bakery production, equipment checks, and quality standards in a team-focused environment.'
  },
  {
    id: 'warehouse-associate',
    title: 'Warehouse Associate',
    industry: 'Logistics & Warehousing',
    location: 'Bristol, United Kingdom',
    country: 'United Kingdom',
    type: 'Full-time',
    salary: 'Discussed during hiring',
    posted: 'Example listing',
    description: 'Help receive, organize, and prepare goods for dispatch while following workplace safety procedures.'
  },
  {
    id: 'hotel-housekeeping',
    title: 'Hotel Housekeeping Team Member',
    industry: 'Hospitality',
    location: 'Dubai, United Arab Emirates',
    country: 'United Arab Emirates',
    type: 'Full-time',
    salary: 'Discussed during hiring',
    posted: 'Example listing',
    description: 'Help maintain clean and welcoming guest spaces as part of a supportive hotel operations team.'
  },
  {
    id: 'care-assistant',
    title: 'Care Assistant',
    industry: 'Healthcare & Social Care',
    location: 'Lisbon, Portugal',
    country: 'Portugal',
    type: 'Full-time',
    salary: 'Discussed during hiring',
    posted: 'Example listing',
    description: 'Provide respectful day-to-day support to clients and help maintain a safe, comfortable care environment.'
  },
  {
    id: 'construction-helper',
    title: 'Construction Site Assistant',
    industry: 'Construction',
    location: 'Sofia, Bulgaria',
    country: 'Bulgaria',
    type: 'Full-time',
    salary: 'Discussed during hiring',
    posted: 'Example listing',
    description: 'Assist skilled tradespeople with site preparation, materials handling, and general project tasks.'
  },
  {
    id: 'production-operator',
    title: 'Light Manufacturing Operator',
    industry: 'Manufacturing',
    location: 'Dhaka, Bangladesh',
    country: 'Bangladesh',
    type: 'Full-time',
    salary: 'Discussed during hiring',
    posted: 'Example listing',
    description: 'Support production-line work, basic quality checks, and an organized, safety-conscious workplace.'
  }
])

const jobFilters = ref({ keyword: '', country: '', industry: '' })
const appliedJobFilters = ref({ keyword: '', country: '', industry: '' })
const jobsToShow = ref(4)
const filteredJobs = computed(() => {
  const keyword = appliedJobFilters.value.keyword.trim().toLowerCase()
  return jobs.value.filter((job) => {
    const matchesKeyword = !keyword
      || `${job.title} ${job.industry} ${job.location} ${job.description}`.toLowerCase().includes(keyword)
    const matchesCountry = !appliedJobFilters.value.country
      || job.country === appliedJobFilters.value.country
    const matchesIndustry = !appliedJobFilters.value.industry
      || job.industry === appliedJobFilters.value.industry
    return matchesKeyword && matchesCountry && matchesIndustry
  })
})
const visibleJobs = computed(() => filteredJobs.value.slice(0, jobsToShow.value))

const selectedJob = ref(null)
const jobApplication = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  nationality: '',
  message: '',
  consent: false
})
const resumeInput = ref(null)
const selectedResume = ref(null)
const resumeError = ref('')
const applicationSubmitting = ref(false)
const applicationSubmitted = ref(false)
const applicationError = ref('')

const heroStats = ref([
  { num: '8,500', suffix: '+', lbl: 'Workers integrated' },
  { num: '30', suffix: '+', lbl: 'Partner countries' },
  { num: '100', suffix: '%', lbl: 'Compliance focused' }
])

const markets = ref([
  { name: 'Europe', count: 14, orange: false },
  { name: 'Middle East', count: 3, orange: true },
  { name: 'Asia', count: 6, orange: false },
  { name: 'South Asia', count: 3, orange: true },
  { name: 'Africa & Americas', count: 6, orange: false }
])

const activeCountries = ref([
  'China', 'India', 'Pakistan', 'Philippines', 'Vietnam', 'Türkiye', 'Saudi Arabia', 'UAE',
  'Cameroon', 'Ethiopia', 'Nigeria', 'Sudan', 'Brazil', 'Cuba', 'Dominican Republic',
  'Albania', 'Italy', 'Kosovo', 'Slovenia', 'Poland', 'Slovakia', 'Montenegro', 'Austria',
  'Denmark', 'France', 'Germany', 'Ireland', 'Netherlands', 'Portugal',
  'Australia', 'Canada', 'New Zealand'
])

const comingCountries = ref([
  'Bahrain', 'Belarus', 'Czech Republic', 'Finland', 'Hungary', 'Japan', 'Malta',
  'Norway', 'Russia', 'Serbia', 'Sweden', 'Ukraine', 'UK'
])

const services = ref([
  {
    icon: 'fas fa-passport',
    title: 'Migration & Legal Services',
    desc: 'Clear pathways for study, work, visits, and family — with full compliance and documentation support.'
  },
  {
    icon: 'fas fa-home',
    title: 'Relocation & Settlement',
    desc: 'Settle faster with guidance grounded in local realities — from housing to integration support.'
  },
  {
    icon: 'fas fa-users',
    title: 'Recruitment & Employment',
    desc: 'Save time hiring through targeted workforce planning, sourcing, and placement services.'
  },
  {
    icon: 'fas fa-graduation-cap',
    title: 'Career & Education Support',
    desc: 'Build sustainable career growth through education, upskilling, and structured pathways.'
  }
])

const values = ref([
  {
    icon: 'fas fa-project-diagram',
    title: 'End-to-end operational control',
    desc: 'Full oversight from sourcing to integration — no gaps, no surprises.'
  },
  {
    icon: 'fas fa-user-check',
    title: 'Candidate readiness as a standard',
    desc: 'Prepared, vetted, and job-ready workers for every placement.'
  },
  {
    icon: 'fas fa-balance-scale',
    title: 'Professional integrity and compliance',
    desc: 'Verified data, ethical recruitment, and full legal compliance.'
  }
])

const regions = ref(['Europe', 'Middle East', 'Asia', 'South Asia'])
const activeRegion = ref('Europe')

const offices = ref([
  { region: 'Europe', country: 'Portugal', address: 'Contact our team for Portugal office details.', phone: '', email: 'contact@aplosglobal.com' },
  { region: 'Europe', country: 'Moldova', address: '10 Iuri Gagarin Blvd., MD-2001, Chisinau, Moldova', phone: '+37 367 115 511', email: 'contact.moldova@aplosglobal.com' },
  { region: 'Europe', country: 'Bulgaria', address: 'Office No. 4, 2nd Floor, Nikolaevska Street 12, Town of Ruse, Bulgaria', phone: '+359 89 491 2256', email: 'contact.bulgaria@aplosglobal.com' },
  { region: 'Europe', country: 'Spain', address: 'Avenida de Aragón, no. 30, El Pla del Real, 46021, Valencia', phone: '+40 768 114 754', email: 'contact.spain@aplosglobal.com' },
  { region: 'Europe', country: 'Cyprus', address: 'Michalacopoulou Street, no. 26, Nicosia, Cyprus', phone: '+40 768 114 754', email: 'contact.cyprus@aplosglobal.com' },
  { region: 'Europe', country: 'Greece', address: 'Kifisias Avenue no. 125, Athens, Greece', phone: '+40 768 114 754', email: 'contact.greece@aplosglobal.com' },
  { region: 'Europe', country: 'Croatia', address: 'Kneza Mislava Street, no. 10, Zagreb, Croatia', phone: '+40 768 114 754', email: 'contact.croatia@aplosglobal.com' },

  { region: 'Middle East', country: 'Saudi Arabia', address: '3645 Al hawi street, Al Aqeed District, Riyadh', phone: '+966 56 405 3621', email: 'contact.saudiarabia@aplosglobal.com' },
  { region: 'Middle East', country: 'United Arab Emirates', address: 'Deira Twin Towers - 1st Floor Office F19, Baniyas Rd, Deira, Dubai, UAE', phone: '+971 55 601 8213', email: 'contact.dubai@aplosglobal.com' },
  { region: 'Middle East', country: 'Türkiye (Ankara)', address: 'Ahi Evran OSB Mah. A.S.O. Blv. ASO 1 Organize Sanayi Bölgesi No: 1, Sincan / ANKARA', phone: '+90 505 907 38 56', email: 'contact.turkey@aplosglobal.com' },

  { region: 'Asia', country: 'South Korea', address: 'Bongeunsa-ro 4-gil, no. 24, Gangnam District, Seoul, South Korea', phone: '+82 10-3978-5058', email: 'contact.southkorea@aplosglobal.com' },
  { region: 'Asia', country: 'Sri Lanka', address: '59 Edward lane, Colombo 3, Sri Lanka', phone: '', email: 'contact.srilanka@aplosglobal.com' },
  { region: 'Asia', country: 'Türkiye', address: 'Kizilay, Ziya Gökalp, 06420 Ankara, Türkiye', phone: '+40 768 114 754', email: 'contact.turkey@aplosglobal.com' },

  { region: 'South Asia', country: 'Bangladesh', address: 'House 115, Road 7, Mohakhali DOHS, Dhaka 1212, Bangladesh', phone: '+880 1401 134806', email: 'contact.bangladesh@aplosglobal.com' },
  { region: 'South Asia', country: 'Nepal', address: 'Dhapasi-8 Street, House no. 300, floor 1, Tokha Municipality, Kathmandu, Nepal', phone: '+977 971 201 2463', email: 'contact.nepal@aplosglobal.com' },
  { region: 'South Asia', country: 'Sri Lanka', address: '59 Edward lane, Colombo 3, Sri Lanka', phone: '+947 06161 656', email: 'contact.srilanka@aplosglobal.com' }
])

const filteredOffices = computed(() => offices.value.filter((o) => o.region === activeRegion.value))

const press = ref([
  {
    source: 'Dubai.News',
    title: 'Aplos Global contributes to global economic growth through overseas employment'
  },
  {
    source: 'Daily News Work',
    title: 'No one wants to get their hands dirty anymore — and Asian workers are quietly keeping the Western world running'
  }
])

const email = ref('')
const subscribed = ref(false)
const subscribeError = ref('')
const subscribing = ref(false)
const contactForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  nationality: '',
  phone: '',
  service: '',
  message: ''
})
const contactSubmitting = ref(false)
const contactSubmitted = ref(false)
const contactError = ref('')
const contactCvInput = ref(null)
const contactCv = ref(null)
const contactCvError = ref('')
const candidateSignup = ref({ givenName: '', surname: '', email: '', phone: '', nationality: '', residenceCountry: '', preferredCountry: '', passportNumber: '', visaType: '', password: '', confirmPassword: '' })
const candidateSignupSubmitting = ref(false)
const candidateSignupSuccess = ref('')
const candidateSignupError = ref('')
const candidateVerificationSent = ref(false)
const candidateVerificationCodes = ref({ email: '', phone: '' })
const candidateSession = ref(null)
const candidateSessionError = ref('')
const candidateOAuthNotice = ref('')
const candidateAuthMode = ref('signup')
const candidateLogin = ref({ email: '', password: '' })
const candidateLoginSubmitting = ref(false)
const candidateLoginError = ref('')
const employerLogin = ref({ email: '', password: '' })
const employerLoginSubmitting = ref(false)
const employerLoginError = ref('')

const loginEmployer = async () => {
  employerLoginError.value = ''
  employerLoginSubmitting.value = true
  try {
    const response = await fetch('/api/employers/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(employerLogin.value)
    })
    const result = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(result.detail || 'Employer sign-in is not available yet.')
    window.location.href = '/employer-dashboard'
  } catch (error) {
    employerLoginError.value = error instanceof Error ? error.message : 'Could not connect to the employer sign-in service.'
  } finally {
    employerLoginSubmitting.value = false
  }
}

const loadCandidateSession = async () => {
  try {
    const response = await fetch('/api/candidates/me', { credentials: 'include' })
    if (!response.ok) return
    candidateSession.value = await response.json()
  } catch {
    candidateSessionError.value = 'Could not check your sign-in status.'
  }
}

const logoutCandidate = async () => {
  await fetch('/api/candidates/logout', { method: 'POST', credentials: 'include' })
  candidateSession.value = null
  candidateAuthMode.value = 'login'
}

const loginCandidate = async () => {
  candidateLoginError.value = ''
  candidateLoginSubmitting.value = true
  try {
    const response = await fetch('/api/candidates/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(candidateLogin.value)
    })
    const result = await response.json()
    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((issue) => issue.msg).join(', ')
        : result.detail
      throw new Error(detail || 'Sign-in failed. Please try again.')
    }
    candidateLogin.value = { email: '', password: '' }
    await loadCandidateSession()
  } catch (error) {
    candidateLoginError.value = error instanceof Error
      ? error.message
      : 'Could not connect to the sign-in service. Please try again.'
  } finally {
    candidateLoginSubmitting.value = false
  }
}
let visitorHeartbeatTimer
let visitorHeartbeatInFlight = false

const subscribe = async () => {
  subscribeError.value = ''
  subscribed.value = false
  subscribing.value = true

  try {
    const response = await fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })
    const result = await response.json()

    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((issue) => issue.msg).join(', ')
        : result.detail
      throw new Error(detail || result.message || 'Subscription request failed.')
    }

    subscribed.value = true
    email.value = ''
    setTimeout(() => {
      subscribed.value = false
    }, 4000)
  } catch (error) {
    subscribeError.value = error instanceof Error
      ? error.message
      : 'Could not connect to the subscription service. Please try again.'
  } finally {
    subscribing.value = false
  }
}

const sendContactInquiry = async () => {
  contactError.value = ''
  contactSubmitted.value = false
  if (contactCvError.value) return
  contactSubmitting.value = true

  try {
    const formData = new FormData()
    for (const [key, value] of Object.entries(contactForm.value)) {
      formData.append(key, value)
    }
    if (contactCv.value) formData.append('cv', contactCv.value)

    const response = await fetch('/api/contact', {
      method: 'POST',
      body: formData
    })
    const result = await response.json()

    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((issue) => issue.msg).join(', ')
        : result.detail
      throw new Error(detail || result.message || 'Your inquiry could not be sent.')
    }

    contactSubmitted.value = true
    contactForm.value = {
      first_name: '',
      last_name: '',
      email: '',
      nationality: '',
      phone: '',
      service: '',
      message: ''
    }
    contactCv.value = null
    if (contactCvInput.value) contactCvInput.value.value = ''
  } catch (error) {
    contactError.value = error instanceof Error
      ? error.message
      : 'Could not connect to our contact service. Please try again.'
  } finally {
    contactSubmitting.value = false
  }
}

const selectContactCv = (event) => {
  const file = event.target.files?.[0] ?? null
  contactCvError.value = ''
  contactCv.value = null

  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf') || (file.type && file.type !== 'application/pdf')) {
    contactCvError.value = 'Please choose a PDF file.'
    event.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    contactCvError.value = 'The PDF must be 5 MB or smaller.'
    event.target.value = ''
    return
  }

  contactCv.value = file
}

const signupCandidate = async () => {
  candidateSignupError.value = ''
  candidateSignupSuccess.value = ''
  if (candidateSignup.value.password !== candidateSignup.value.confirmPassword) {
    candidateSignupError.value = 'Passwords do not match.'
    return
  }

  candidateSignupSubmitting.value = true
  try {
    const signupPayload = {
      given_name: candidateSignup.value.givenName,
      surname: candidateSignup.value.surname,
      email: candidateSignup.value.email,
      phone: candidateSignup.value.phone,
      nationality: candidateSignup.value.nationality,
      residence_country: candidateSignup.value.residenceCountry,
      preferred_country: candidateSignup.value.preferredCountry,
      passport_number: candidateSignup.value.passportNumber,
      visa_type: candidateSignup.value.visaType,
      password: candidateSignup.value.password
    }
    const response = await fetch(candidateVerificationSent.value
      ? '/api/candidates/signup'
      : '/api/candidates/signup/send-codes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(candidateVerificationSent.value
        ? { ...signupPayload, email_code: candidateVerificationCodes.value.email, phone_code: candidateVerificationCodes.value.phone }
        : signupPayload)
    })
    const result = await response.json()
    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((issue) => issue.msg).join(', ')
        : result.detail
      throw new Error(detail || 'Your account could not be created.')
    }

    if (!candidateVerificationSent.value) {
      candidateVerificationSent.value = true
      candidateSignupSuccess.value = result.message || 'Verification codes sent.'
      return
    }
    candidateSignupSuccess.value = result.message || 'Your account has been created.'
    candidateSignup.value = { givenName: '', surname: '', email: '', phone: '', nationality: '', residenceCountry: '', preferredCountry: '', passportNumber: '', visaType: '', password: '', confirmPassword: '' }
    candidateVerificationCodes.value = { email: '', phone: '' }
    candidateVerificationSent.value = false
  } catch (error) {
    candidateSignupError.value = error instanceof Error
      ? error.message
      : 'Could not connect to the signup service. Please try again.'
  } finally {
    candidateSignupSubmitting.value = false
  }
}

const sendVisitorHeartbeat = async (visitorId) => {
  if (visitorHeartbeatInFlight || document.visibilityState !== 'visible') return
  visitorHeartbeatInFlight = true

  try {
    const response = await fetch('/api/visitors/heartbeat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ visitor_id: visitorId })
    })
    if (!response.ok) {
      throw new Error(`Visitor heartbeat failed with status ${response.status}.`)
    }
  } catch (error) {
    console.error('Could not update live visitor status.', error)
  } finally {
    visitorHeartbeatInFlight = false
  }
}

let handleVisitorVisibilityChange

onMounted(() => {
  if (window.location.pathname === '/candidate-portal') {
    const query = new URLSearchParams(window.location.search)
    if (query.get('oauth') === 'signup-with-codes') {
      candidateOAuthNotice.value = 'New accounts must verify both email and phone. Use the Sign up form below to receive verification codes.'
      window.history.replaceState({}, '', '/candidate-portal')
    } else if (query.get('login') === 'success') {
      window.history.replaceState({}, '', '/candidate-portal')
    }
    void loadCandidateSession()
  }
  const storageKey = 'aplos-visitor-id'
  let visitorId = sessionStorage.getItem(storageKey)
  if (!visitorId) {
    visitorId = crypto.randomUUID()
    sessionStorage.setItem(storageKey, visitorId)
  }

  handleVisitorVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      void sendVisitorHeartbeat(visitorId)
    }
  }

  void sendVisitorHeartbeat(visitorId)
  visitorHeartbeatTimer = window.setInterval(
    () => void sendVisitorHeartbeat(visitorId),
    30_000
  )
  document.addEventListener('visibilitychange', handleVisitorVisibilityChange)

  if (window.location.pathname === '/offices') {
    void nextTick(() => {
      document.getElementById('offices')?.scrollIntoView()
    })
  }
})

onUnmounted(() => {
  window.clearInterval(visitorHeartbeatTimer)
  if (handleVisitorVisibilityChange) {
    document.removeEventListener('visibilitychange', handleVisitorVisibilityChange)
  }
})

const applyJobFilters = () => {
  appliedJobFilters.value = { ...jobFilters.value }
  jobsToShow.value = 4
}

const resetJobFilters = () => {
  jobFilters.value = { keyword: '', country: '', industry: '' }
  appliedJobFilters.value = { keyword: '', country: '', industry: '' }
  jobsToShow.value = 4
}

const openApplication = (job) => {
  selectedJob.value = job
  applicationSubmitted.value = false
  applicationError.value = ''
  jobApplication.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    nationality: '',
    message: '',
    consent: false
  }
  selectedResume.value = null
  resumeError.value = ''
  if (resumeInput.value) resumeInput.value.value = ''
}

const closeApplication = () => {
  if (applicationSubmitting.value) return
  selectedJob.value = null
  applicationError.value = ''
}

const submitApplication = async () => {
  if (!selectedJob.value) return
  if (resumeError.value) return

  applicationError.value = ''
  applicationSubmitted.value = false
  applicationSubmitting.value = true

  try {
    const formData = new FormData()
    formData.append('job_title', selectedJob.value.title)
    formData.append('first_name', jobApplication.value.first_name)
    formData.append('last_name', jobApplication.value.last_name)
    formData.append('email', jobApplication.value.email)
    formData.append('phone', jobApplication.value.phone)
    formData.append('nationality', jobApplication.value.nationality)
    formData.append('message', jobApplication.value.message)
    formData.append('consent', String(jobApplication.value.consent))
    if (selectedResume.value) formData.append('resume', selectedResume.value)

    const response = await fetch('/api/apply', {
      method: 'POST',
      body: formData
    })
    const result = await response.json()

    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((issue) => issue.msg).join(', ')
        : result.detail
      throw new Error(detail || result.message || 'Your application could not be sent.')
    }

    applicationSubmitted.value = true
    jobApplication.value = {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      nationality: '',
      message: '',
      consent: false
    }
    selectedResume.value = null
    if (resumeInput.value) resumeInput.value.value = ''
  } catch (error) {
    applicationError.value = error instanceof Error
      ? error.message
      : 'Could not connect to the application service. Please try again.'
  } finally {
    applicationSubmitting.value = false
  }
}

const selectResume = (event) => {
  const file = event.target.files?.[0] ?? null
  resumeError.value = ''
  selectedResume.value = null

  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf') || (file.type && file.type !== 'application/pdf')) {
    resumeError.value = 'Please choose a PDF file.'
    event.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    resumeError.value = 'The PDF must be 5 MB or smaller.'
    event.target.value = ''
    return
  }

  selectedResume.value = file
}
</script>

<template>
  <div v-if="isEmployerPortalPage" class="candidate-portal-page employer-portal-page">
    <div class="topbar">
      <div class="container topbar-inner">
        <div class="topbar-left">
          <span><i class="fas fa-phone"></i> <a href="tel:+971566682098">+971 56 668 2098</a></span>
          <span><i class="fas fa-envelope"></i> contact@aplosglobal.com</span>
        </div>
        <div class="topbar-right"><a href="/"><i class="fas fa-house"></i> Home</a></div>
      </div>
    </div>
    <header class="site-header">
      <div class="container header-main">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy"><span class="brand-name">Aplos Global</span><span class="brand-tag">Workforce Infrastructure</span></span>
        </a>
        <a href="/candidate-portal" class="btn btn-ghost">Candidate Portal</a>
      </div>
    </header>
    <main class="candidate-portal-main">
      <section class="candidate-signup-card">
        <span class="label">Employer Portal</span>
        <h1>Welcome back</h1>
        <p class="candidate-signup-intro">Sign in to manage your workforce requests, vacancies, and placements.</p>
        <form class="candidate-signup-form" @submit.prevent="loginEmployer">
          <label class="form-field"><span>Work email</span><input v-model.trim="employerLogin.email" type="email" autocomplete="username" placeholder="you@company.com" required></label>
          <label class="form-field"><span>Password</span><input v-model="employerLogin.password" type="password" autocomplete="current-password" placeholder="Enter your password" required></label>
          <button class="btn btn-primary candidate-signup-submit" type="submit" :disabled="employerLoginSubmitting"><i :class="employerLoginSubmitting ? 'fas fa-spinner fa-spin' : 'fas fa-right-to-bracket'" aria-hidden="true"></i> {{ employerLoginSubmitting ? 'Signing in...' : 'Log in' }}</button>
          <p v-if="employerLoginError" class="contact-feedback contact-failure" role="alert">{{ employerLoginError }}</p>
        </form>
        <p class="candidate-signup-intro">Need an employer account? <a href="/#contact">Contact our team</a> to get started.</p>
      </section>
    </main>
  </div>
  <div v-else-if="isCandidatePortalPage" class="candidate-portal-page">
    <div class="topbar">
      <div class="container topbar-inner">
        <div class="topbar-left">
          <span><i class="fas fa-phone"></i> <a href="tel:+971566682098">+971 56 668 2098</a></span>
          <span><i class="fas fa-envelope"></i> contact@aplosglobal.com</span>
        </div>
        <div class="topbar-right">
          <a href="/"><i class="fas fa-house"></i> Home</a>
        </div>
      </div>
    </div>
    <header class="site-header">
      <div class="container header-main">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>
        <a href="/find-jobs" class="btn btn-ghost">Find Jobs</a>
      </div>
    </header>
    <main class="candidate-portal-main">
      <section class="candidate-signup-card">
        <span class="label">Candidate Portal</span>
        <h1>{{ candidateAuthMode === 'signup' ? 'Create your account' : 'Welcome back' }}</h1>
        <p class="candidate-signup-intro">
          {{ candidateAuthMode === 'signup' ? 'Sign up to start your international career journey with Aplos Global.' : 'Sign in to continue to your Aplos Global candidate account.' }}
        </p>
        <p v-if="candidateOAuthNotice" class="candidate-oauth-notice" role="status">{{ candidateOAuthNotice }}</p>
        <div v-if="!candidateSession" class="candidate-auth-switch" role="tablist" aria-label="Candidate account access">
          <button type="button" role="tab" :aria-selected="candidateAuthMode === 'login'" :class="{ active: candidateAuthMode === 'login' }" @click="candidateAuthMode = 'login'; candidateSignupError = ''; candidateLoginError = ''">Log in</button>
          <button type="button" role="tab" :aria-selected="candidateAuthMode === 'signup'" :class="{ active: candidateAuthMode === 'signup' }" @click="candidateAuthMode = 'signup'; candidateSignupError = ''; candidateLoginError = ''">Sign up</button>
        </div>
        <div v-if="!candidateSession && candidateAuthMode === 'signup' && !candidateVerificationSent" class="candidate-verification-info">
          <i class="fas fa-shield-halved" aria-hidden="true"></i>
          <span>Signup requires one code sent to your email and another sent to your phone. Complete the form, then choose <strong>Send verification codes</strong>.</span>
        </div>
        <div v-if="candidateSession" class="candidate-session-card" role="status">
          <p>Signed in as <strong>{{ candidateSession.name || candidateSession.email }}</strong>.</p>
          <button class="btn btn-ghost" type="button" @click="logoutCandidate">Sign out</button>
        </div>
        <p v-if="candidateSessionError" class="contact-feedback contact-failure" role="alert">{{ candidateSessionError }}</p>
        <div v-if="!candidateSession" class="candidate-social-auth" aria-label="Sign in or sign up with a social account">
          <a class="candidate-social-button" href="/api/candidates/oauth/google" aria-label="Continue with Google">
            <svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#4285F4" d="M43.6 24.5c0-1.4-.1-2.8-.4-4.1H24v7.8h11c-.5 2.5-1.9 4.7-4 6.1v5h6.5c3.8-3.5 6.1-8.6 6.1-14.8Z"/><path fill="#34A853" d="M24 44c5.5 0 10.1-1.8 13.5-4.8l-6.5-5c-1.8 1.2-4.1 2-7 2-5.3 0-9.8-3.6-11.4-8.4H5.9v5.2A20 20 0 0 0 24 44Z"/><path fill="#FBBC05" d="M12.6 27.8a12 12 0 0 1 0-7.6V15H5.9a20 20 0 0 0 0 17.9l6.7-5.1Z"/><path fill="#EA4335" d="M24 11.8c3 0 5.7 1 7.8 3.1l5.8-5.8C34.1 5.8 29.5 4 24 4A20 20 0 0 0 5.9 15l6.7 5.2c1.6-4.8 6.1-8.4 11.4-8.4Z"/></svg>
            <span>Continue with Google</span>
          </a>
          <a class="candidate-social-button" href="/api/candidates/oauth/apple" aria-label="Continue with Apple">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.37 12.23c.02 2.24 1.96 2.98 1.98 2.99-.02.05-.31 1.08-1.02 2.14-.62.92-1.27 1.83-2.29 1.85-1 .02-1.32-.6-2.47-.6-1.15 0-1.51.58-2.45.62-.98.04-1.72-.99-2.34-1.9-1.27-1.84-2.24-5.2-.93-7.47.65-1.13 1.82-1.84 3.09-1.86.96-.02 1.87.65 2.46.65.59 0 1.69-.8 2.85-.68.49.02 1.87.2 2.76 1.5-.07.04-1.65.97-1.64 2.76ZM14.5 6.76c.52-.63.87-1.5.77-2.37-.75.03-1.65.5-2.19 1.13-.48.56-.9 1.45-.79 2.3.84.06 1.69-.43 2.21-1.06Z"/></svg>
            <span>Continue with Apple</span>
          </a>
        </div>
        <div v-if="!candidateSession" class="candidate-auth-divider"><span>or continue with email</span></div>
        <form v-if="!candidateSession && candidateAuthMode === 'login'" class="candidate-signup-form" @submit.prevent="loginCandidate">
          <label class="form-field">
            <span>Email</span>
            <input v-model.trim="candidateLogin.email" name="login-email" type="email" autocomplete="email" required>
          </label>
          <label class="form-field">
            <span>Password</span>
            <input v-model="candidateLogin.password" name="login-password" type="password" autocomplete="current-password" required>
          </label>
          <button class="btn btn-primary candidate-signup-submit" type="submit" :disabled="candidateLoginSubmitting">
            <i :class="candidateLoginSubmitting ? 'fas fa-spinner fa-spin' : 'fas fa-right-to-bracket'" aria-hidden="true"></i>
            {{ candidateLoginSubmitting ? 'Signing in...' : 'Log in' }}
          </button>
          <p v-if="candidateLoginError" class="contact-feedback contact-failure" role="alert">{{ candidateLoginError }}</p>
        </form>
        <form v-if="!candidateSession && candidateAuthMode === 'signup'" class="candidate-signup-form" @submit.prevent="signupCandidate">
          <label class="form-field">
            <span>Surname <span class="required-mark">*</span></span>
            <input
              v-model.trim="candidateSignup.surname"
              name="surname"
              type="text"
              autocomplete="family-name"
              maxlength="80"
              placeholder="Your surname"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <label class="form-field">
            <span>Given name <span class="required-mark">*</span></span>
            <input
              v-model.trim="candidateSignup.givenName"
              name="given-name"
              type="text"
              autocomplete="given-name"
              maxlength="80"
              placeholder="Your given name"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <label class="form-field">
            <span>Email <span class="required-mark">*</span></span>
            <input
              v-model.trim="candidateSignup.email"
              name="email"
              type="email"
              autocomplete="email"
              maxlength="254"
              placeholder="you@gmail.com"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <label class="form-field">
            <span>Phone number (with country code) <span class="required-mark">*</span></span>
            <input
              v-model.trim="candidateSignup.phone"
              name="phone"
              type="tel"
              autocomplete="tel"
              maxlength="32"
              placeholder="+880 1XXX-XXXXXX"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <label class="form-field">
            <span>Nationality</span>
            <input
              v-model.trim="candidateSignup.nationality"
              name="nationality"
              type="text"
              autocomplete="country-name"
              maxlength="80"
              placeholder="e.g. Bangladeshi"
              :readonly="candidateVerificationSent"
            >
          </label>
          <label class="form-field">
            <span>Residence country (optional)</span>
            <input
              v-model.trim="candidateSignup.residenceCountry"
              name="residence-country"
              type="text"
              autocomplete="country-name"
              maxlength="80"
              placeholder="Country where you currently live"
              :readonly="candidateVerificationSent"
            >
          </label>
          <label class="form-field">
            <span>Preferred destination country</span>
            <input
              v-model.trim="candidateSignup.preferredCountry"
              name="preferred-country"
              type="text"
              autocomplete="country-name"
              maxlength="80"
              placeholder="Which country would you like to work in?"
              :readonly="candidateVerificationSent"
            >
          </label>
          <label class="form-field">
            <span>Passport number <span class="required-mark">*</span></span>
            <input
              v-model.trim="candidateSignup.passportNumber"
              name="passport-number"
              type="text"
              autocomplete="off"
              minlength="4"
              maxlength="32"
              placeholder="Enter your passport number"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <div v-if="candidateVerificationSent" class="candidate-code-fields form-field-full">
            <p>Enter the 6-digit codes sent to your email and phone. Codes expire in 10 minutes.</p>
            <label class="form-field">
              <span>Email verification code <span class="required-mark">*</span></span>
              <input v-model.trim="candidateVerificationCodes.email" name="email-code" type="text" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" placeholder="6-digit code" required>
            </label>
            <label class="form-field">
              <span>Phone verification code <span class="required-mark">*</span></span>
              <input v-model.trim="candidateVerificationCodes.phone" name="phone-code" type="text" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" placeholder="6-digit code" required>
            </label>
            <button class="candidate-change-contact" type="button" @click="candidateVerificationSent = false; candidateVerificationCodes = { email: '', phone: '' }; candidateSignupSuccess = ''">Edit signup details</button>
          </div>
          <label class="form-field">
            <span>Visa type <span class="required-mark">*</span></span>
            <select v-model="candidateSignup.visaType" name="visa-type" :disabled="candidateVerificationSent" required>
              <option disabled value="">Select a visa type</option>
              <option value="Student Visa">Student Visa</option>
              <option value="Work Permit Visa">Work Permit Visa</option>
              <option value="Visit Visa">Visit Visa</option>
            </select>
          </label>
          <label class="form-field">
            <span>Password <span class="required-mark">*</span></span>
            <input
              v-model="candidateSignup.password"
              name="new-password"
              type="password"
              autocomplete="new-password"
              minlength="12"
              maxlength="128"
              placeholder="At least 12 characters"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <label class="form-field">
            <span>Confirm password <span class="required-mark">*</span></span>
            <input
              v-model="candidateSignup.confirmPassword"
              name="confirm-password"
              type="password"
              autocomplete="new-password"
              minlength="12"
              maxlength="128"
              placeholder="Re-enter your password"
              :readonly="candidateVerificationSent"
              required
            >
          </label>
          <p class="candidate-password-note">Use at least 12 characters. Your password is stored as a secure hash.</p>
          <button class="btn btn-primary candidate-signup-submit" type="submit" :disabled="candidateSignupSubmitting">
            <i :class="candidateSignupSubmitting ? 'fas fa-spinner fa-spin' : 'fas fa-user-plus'" aria-hidden="true"></i>
            {{ candidateSignupSubmitting ? (candidateVerificationSent ? 'Verifying...' : 'Sending codes...') : (candidateVerificationSent ? 'Verify codes and create account' : 'Send verification codes') }}
          </button>
          <p v-if="candidateSignupSuccess" class="contact-feedback contact-success" role="status">
            <i class="fas fa-check-circle" aria-hidden="true"></i> {{ candidateSignupSuccess }}
          </p>
          <p v-if="candidateSignupError" class="contact-feedback contact-failure" role="alert">
            {{ candidateSignupError }}
          </p>
        </form>
      </section>
    </main>
    <footer class="jobs-footer">
      <div class="container jobs-footer-inner">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>
        <span>© 2026 Aplos Global LLC. All rights reserved.</span>
      </div>
    </footer>
    <a class="whatsapp-float" href="https://wa.me/8801760818130" target="_blank" rel="noopener noreferrer" aria-label="Chat with Aplos Global on WhatsApp">
      <i class="fab fa-whatsapp" aria-hidden="true"></i>
    </a>
    <a class="messenger-float" href="https://m.me/aplosglobaltravelsllc" target="_blank" rel="noopener noreferrer" aria-label="Message Aplos Global on Messenger">
      <i class="fab fa-facebook-messenger" aria-hidden="true"></i>
    </a>
  </div>
  <div v-else-if="isAboutPage" class="about-page-shell">
    <div class="topbar">
      <div class="container topbar-inner">
        <div class="topbar-left">
          <span><i class="fas fa-phone"></i> <a href="tel:+971566682098">+971-566682098</a></span>
          <span><i class="fas fa-envelope"></i> contact@aplosglobal.com</span>
        </div>
        <div class="topbar-right">
          <a href="/#contact"><i class="fas fa-comments"></i> Contact us</a>
        </div>
      </div>
    </div>

    <header class="site-header">
      <div class="container header-main">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>
        <nav class="about-nav">
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about" class="active">About</a></li>
            <li><a href="/#services">Services</a></li>
            <li><a href="/offices">Offices</a></li>
            <li><a href="/find-jobs">Career</a></li>
            <li><a href="/#contact">Contact</a></li>
          </ul>
        </nav>
      </div>
    </header>

    <main class="about-main">
      <section class="about-hero">
        <div class="container about-hero-inner">
          <div class="about-hero-copy">
            <span class="jobs-kicker"><i class="fas fa-globe"></i> Built around people and possibility</span>
            <h1>Connecting talent and opportunity <em>across borders.</em></h1>
            <p>
              Aplos Global builds practical workforce pathways—bringing employers,
              international talent, and local support together with care and accountability.
            </p>
            <div class="about-hero-actions">
              <a href="#our-story" class="btn btn-orange">Our story <i class="fas fa-arrow-down"></i></a>
              <a href="/#contact" class="btn btn-outline-white">Talk to our team</a>
            </div>
            <div class="jobs-trust-line">
              <span><i class="fas fa-scale-balanced"></i> Compliance-minded</span>
              <span><i class="fas fa-people-group"></i> People-first support</span>
            </div>
          </div>
          <div class="about-hero-art" aria-hidden="true">
            <img class="about-hero-image" src="/images/about/global-workforce.svg" alt="">
            <div class="about-hero-card">
              <i class="fas fa-handshake"></i>
              <span><strong>One connected journey</strong><small>From preparation to integration</small></span>
            </div>
          </div>
        </div>
      </section>

      <section id="our-story" class="about-story-section">
        <div class="container about-story-grid">
          <img
            class="about-story-image"
            src="/images/about/people-and-opportunity.svg"
            alt="Illustration of people connected across an international career journey"
          >
          <div class="about-story-copy">
            <span class="label">Who we are</span>
            <h2>Workforce mobility, thoughtfully connected.</h2>
            <p>
              International recruitment is more than matching a role with a candidate.
              It takes clear planning, careful preparation, responsible processes, and
              real support as people settle into a new workplace and community.
            </p>
            <p>
              Aplos Global brings these steps together for employers and individuals.
              We connect sourcing, recruitment, migration support, relocation, and
              integration into a coordinated workforce journey—guided by local context
              and a commitment to professional integrity.
            </p>
            <a href="/find-jobs" class="link-arrow">Explore career opportunities <i class="fas fa-arrow-right"></i></a>
          </div>
        </div>
      </section>

      <section class="about-purpose-section">
        <div class="container">
          <div class="section-head about-purpose-heading">
            <div>
              <span class="label">Our purpose</span>
              <h2>Clear direction. Shared progress.</h2>
              <p>We aim to make international workforce journeys more coordinated, responsible, and supportive.</p>
            </div>
          </div>
          <div class="about-purpose-grid">
            <article class="purpose-card purpose-mission">
              <img class="purpose-illustration" src="/images/about/mission.svg" alt="">
              <span class="purpose-kicker">What guides us</span>
              <h3>Our Mission</h3>
              <p>
                To connect employers with prepared international talent and support
                individuals through each step of their career journey—with clear
                processes, local understanding, and respect.
              </p>
            </article>
            <article class="purpose-card purpose-vision">
              <img class="purpose-illustration" src="/images/about/vision.svg" alt="">
              <span class="purpose-kicker">Where we are going</span>
              <h3>Our Vision</h3>
              <p>
                To help shape a more connected world of work, where cross-border
                mobility is approached with professionalism, transparency, and
                opportunity for people and organizations alike.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section class="about-values-section">
        <div class="container">
          <div class="section-head">
            <div>
              <span class="label">How we work</span>
              <h2>Principles behind every placement.</h2>
              <p>Trust is built through consistent actions at every stage of the workforce journey.</p>
            </div>
          </div>
          <div class="about-values-grid">
            <article v-for="(value, index) in values" :key="value.title" class="about-value-card">
              <span class="about-value-number">0{{ index + 1 }}</span>
              <span class="about-value-icon"><i :class="value.icon" aria-hidden="true"></i></span>
              <h3>{{ value.title }}</h3>
              <p>{{ value.desc }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="about-services-section">
        <div class="container">
          <div class="section-head">
            <div>
              <span class="label">What we do</span>
              <h2>Support across the journey.</h2>
              <p>Connected services help employers plan and help individuals move forward with greater clarity.</p>
            </div>
            <a href="/#contact" class="link-arrow">Discuss your needs <i class="fas fa-arrow-right"></i></a>
          </div>
          <div class="about-services-grid">
            <article v-for="service in services" :key="service.title" class="about-service-card">
              <span class="about-service-icon"><i :class="service.icon" aria-hidden="true"></i></span>
              <h3>{{ service.title }}</h3>
              <p>{{ service.desc }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="about-network-section">
        <div class="container about-network-inner">
          <div>
            <span class="label">Our network</span>
            <h2>Local understanding.<br>International perspective.</h2>
            <p>
              Our international office network helps connect people and employers
              with context-aware support across regions.
            </p>
          </div>
          <div class="about-network-stat-grid">
            <div class="about-network-stat">
              <strong>30<span>+</span></strong>
              <span>Partner countries</span>
            </div>
            <div class="about-network-stat">
              <strong>8,500<span>+</span></strong>
              <span>Workers integrated worldwide</span>
            </div>
            <a href="/#contact" class="about-network-link">Ask about our network <i class="fas fa-arrow-right"></i></a>
          </div>
        </div>
      </section>

      <section class="about-cta-section">
        <div class="container about-cta-inner">
          <div>
            <span class="label">Let’s work together</span>
            <h2>Looking for talent or your next opportunity?</h2>
            <p>Tell us what you are looking for and our team will help you find the right next step.</p>
          </div>
          <div class="about-cta-actions">
            <a href="/#contact" class="btn btn-orange">Contact our team <i class="fas fa-arrow-right"></i></a>
            <a href="/find-jobs" class="btn btn-outline-white">Find a job</a>
          </div>
        </div>
      </section>
    </main>

    <footer class="jobs-footer">
      <div class="container jobs-footer-inner">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>
        <span>© 2026 Aplos Global LLC. All rights reserved.</span>
        <a href="/#contact">Contact our team <i class="fas fa-arrow-right"></i></a>
      </div>
    </footer>
    <a class="whatsapp-float" href="https://wa.me/8801760818130" target="_blank" rel="noopener noreferrer" aria-label="Chat with Aplos Global on WhatsApp">
      <i class="fab fa-whatsapp" aria-hidden="true"></i>
    </a>
    <a class="messenger-float" href="https://m.me/aplosglobaltravelsllc" target="_blank" rel="noopener noreferrer" aria-label="Message Aplos Global on Messenger">
      <i class="fab fa-facebook-messenger" aria-hidden="true"></i>
    </a>
  </div>

  <div v-else-if="isFindJobsPage" class="jobs-page-shell">
    <div class="topbar">
      <div class="container topbar-inner">
        <div class="topbar-left">
          <span><i class="fas fa-phone"></i> <a href="tel:+971566682098">+971-566682098</a></span>
          <span><i class="fas fa-envelope"></i> contact@aplosglobal.com</span>
        </div>
        <div class="topbar-right">
          <a href="/#contact"><i class="fas fa-comments"></i> Contact us</a>
        </div>
      </div>
    </div>

    <header class="site-header">
      <div class="container header-main">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>
        <nav class="jobs-nav">
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/#services">Services</a></li>
            <li><a href="/offices">Offices</a></li>
            <li><a href="#jobs" class="active">Career</a></li>
            <li><a href="/#contact">Contact</a></li>
          </ul>
        </nav>
        <a href="/#contact" class="btn btn-primary jobs-header-cta">Talk to our team</a>
      </div>
    </header>

    <main class="jobs-main">
      <section class="jobs-hero">
        <div class="container jobs-hero-inner">
          <div class="jobs-hero-copy">
            <span class="jobs-kicker"><i class="fas fa-compass"></i> Your next step starts here</span>
            <h1>Find work that <em>moves you forward.</em></h1>
            <p>Explore international career opportunities and take the next step with support from our workforce team.</p>
            <a href="#jobs" class="btn btn-orange">Explore opportunities <i class="fas fa-arrow-down"></i></a>
            <div class="jobs-trust-line">
              <span><i class="fas fa-globe"></i> Opportunities across borders</span>
              <span><i class="fas fa-handshake"></i> Support through your journey</span>
            </div>
          </div>
          <div class="jobs-hero-art" aria-hidden="true">
            <div class="hero-orbit orbit-one"></div>
            <div class="hero-orbit orbit-two"></div>
            <div class="hero-globe"><i class="fas fa-earth-europe"></i></div>
            <div class="hero-float-card">
              <i class="fas fa-briefcase"></i>
              <span><strong>Global careers</strong><small>Local guidance</small></span>
            </div>
          </div>
        </div>
      </section>

      <section id="jobs" class="jobs-content-section">
        <div class="container">
          <div class="jobs-section-heading">
            <div>
              <span class="label">Job board</span>
              <h2>Explore opportunities</h2>
              <p>Search by role, destination, or industry to find a position that fits your experience.</p>
            </div>
            <a href="/#contact" class="link-arrow">Need help? Contact us <i class="fas fa-arrow-right"></i></a>
          </div>

          <form class="job-filter-panel" @submit.prevent="applyJobFilters">
            <div class="filter-panel-heading">
              <span><i class="fas fa-sliders"></i> Refine your search</span>
              <button class="reset-filters" type="button" @click="resetJobFilters">Reset filters</button>
            </div>
            <div class="job-filter-controls">
              <label class="job-filter-field keyword-filter">
                <span>Job title or keyword</span>
                <div class="filter-input-wrap">
                  <i class="fas fa-search" aria-hidden="true"></i>
                  <input v-model.trim="jobFilters.keyword" type="search" placeholder="e.g. warehouse, care assistant">
                </div>
              </label>
              <label class="job-filter-field">
                <span>Country</span>
                <select v-model="jobFilters.country">
                  <option value="">All countries</option>
                  <option v-for="country in [...new Set(jobs.map((job) => job.country))]" :key="country" :value="country">
                    {{ country }}
                  </option>
                </select>
              </label>
              <label class="job-filter-field">
                <span>Industry</span>
                <select v-model="jobFilters.industry">
                  <option value="">All industries</option>
                  <option v-for="industry in [...new Set(jobs.map((job) => job.industry))]" :key="industry" :value="industry">
                    {{ industry }}
                  </option>
                </select>
              </label>
              <button class="btn btn-primary filter-submit" type="submit">
                Search jobs <i class="fas fa-arrow-right"></i>
              </button>
            </div>
          </form>

          <div class="job-results-heading">
            <div>
              <h3>Available roles <span>{{ filteredJobs.length }}</span></h3>
              <p>Browse the opportunities that match your search.</p>
            </div>
            <span class="sample-data-note"><i class="fas fa-circle-info"></i> Example listings — replace with verified openings before publishing.</span>
          </div>

          <div v-if="visibleJobs.length" class="job-results-list">
            <article v-for="job in visibleJobs" :key="job.id" class="job-card">
              <div class="job-card-main">
                <div class="job-card-topline">
                  <span class="job-industry">{{ job.industry }}</span>
                  <span class="job-posted"><i class="far fa-clock"></i> {{ job.posted }}</span>
                </div>
                <h3>{{ job.title }}</h3>
                <p class="job-description">{{ job.description }}</p>
                <div class="job-meta">
                  <span><i class="fas fa-location-dot"></i> {{ job.location }}</span>
                  <span><i class="fas fa-briefcase"></i> {{ job.type }}</span>
                  <span><i class="fas fa-money-bill-wave"></i> {{ job.salary }}</span>
                </div>
              </div>
              <div class="job-card-action">
                <span class="example-badge">Sample role</span>
                <button type="button" class="btn btn-primary" @click="openApplication(job)">
                  Apply now <i class="fas fa-arrow-right"></i>
                </button>
              </div>
            </article>
          </div>

          <div v-else class="jobs-empty-state">
            <span><i class="fas fa-magnifying-glass"></i></span>
            <h3>No matching opportunities</h3>
            <p>Try a different keyword or reset your filters to see all roles.</p>
            <button type="button" class="btn btn-ghost" @click="resetJobFilters">Reset search</button>
          </div>

          <div v-if="visibleJobs.length < filteredJobs.length" class="load-more-wrap">
            <button type="button" class="btn btn-ghost load-more-button" @click="jobsToShow += 4">
              Show more opportunities <i class="fas fa-plus"></i>
            </button>
          </div>

          <div class="jobs-note">
            <i class="fas fa-shield-heart"></i>
            <p><strong>Recruitment should be transparent.</strong> Aplos Global does not charge candidates recruitment fees. Verify every opportunity with our team before sharing personal documents or making travel arrangements.</p>
          </div>
        </div>
      </section>
    </main>

    <footer class="jobs-footer">
      <div class="container jobs-footer-inner">
        <a href="/" class="brand" aria-label="Aplos Global home">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>
        <span>© 2026 Aplos Global LLC. All rights reserved.</span>
        <a href="/#contact">Contact our team <i class="fas fa-arrow-right"></i></a>
      </div>
    </footer>
    <a class="whatsapp-float" href="https://wa.me/8801760818130" target="_blank" rel="noopener noreferrer" aria-label="Chat with Aplos Global on WhatsApp">
      <i class="fab fa-whatsapp" aria-hidden="true"></i>
    </a>
    <a class="messenger-float" href="https://m.me/aplosglobaltravelsllc" target="_blank" rel="noopener noreferrer" aria-label="Message Aplos Global on Messenger">
      <i class="fab fa-facebook-messenger" aria-hidden="true"></i>
    </a>

    <div v-if="selectedJob" class="application-overlay" @click.self="closeApplication" @keydown.esc="closeApplication">
      <section class="application-dialog" role="dialog" aria-modal="true" aria-labelledby="application-title">
        <button type="button" class="application-close" aria-label="Close application form" @click="closeApplication">
          <i class="fas fa-times"></i>
        </button>
        <template v-if="!applicationSubmitted">
          <span class="label">Job application</span>
          <h2 id="application-title">Apply for {{ selectedJob.title }}</h2>
          <p class="application-intro">Share your contact details and our team will follow up about this sample role.</p>
          <form class="application-form" @submit.prevent="submitApplication">
            <label class="form-field">
              <span>First name <span class="required-mark">*</span></span>
              <input v-model.trim="jobApplication.first_name" name="applicant-first-name" type="text" autocomplete="given-name" minlength="1" maxlength="60" required>
            </label>
            <label class="form-field">
              <span>Last name <span class="required-mark">*</span></span>
              <input v-model.trim="jobApplication.last_name" name="applicant-last-name" type="text" autocomplete="family-name" minlength="1" maxlength="60" required>
            </label>
            <label class="form-field">
              <span>Email <span class="required-mark">*</span></span>
              <input v-model.trim="jobApplication.email" name="applicant-email" type="email" autocomplete="email" maxlength="254" required>
            </label>
            <label class="form-field">
              <span>Phone <span class="required-mark">*</span></span>
              <input v-model.trim="jobApplication.phone" name="applicant-phone" type="tel" autocomplete="tel" maxlength="40" required>
            </label>
            <label class="form-field">
              <span>Nationality</span>
              <input v-model.trim="jobApplication.nationality" name="applicant-nationality" type="text" maxlength="80">
            </label>
            <div class="form-field form-field-full">
              <span>Upload CV <span class="optional-mark">(optional, PDF up to 5 MB)</span></span>
              <input
                ref="resumeInput"
                class="resume-file-input"
                name="resume"
                type="file"
                accept=".pdf,application/pdf"
                aria-label="Upload CV as PDF"
                @change="selectResume"
              >
              <p v-if="selectedResume" class="selected-resume" role="status">
                <i class="fas fa-file-pdf" aria-hidden="true"></i>
                {{ selectedResume.name }}
              </p>
              <p v-if="resumeError" class="resume-error" role="alert">{{ resumeError }}</p>
            </div>
            <label class="form-field form-field-full">
              <span>Message <span class="required-mark">*</span></span>
              <textarea v-model.trim="jobApplication.message" name="applicant-message" rows="4" minlength="10" maxlength="3000" placeholder="Tell us briefly about your experience and availability." required></textarea>
            </label>
            <label class="application-consent">
              <input v-model="jobApplication.consent" type="checkbox" name="consent" required>
              <span>I agree that Aplos Global may store my application details and optional CV to review this application.</span>
            </label>
            <p class="application-privacy">Your details and any CV you upload will be stored in Aplos Global’s recruitment database for application review.</p>
            <button type="submit" class="btn btn-primary application-submit" :disabled="applicationSubmitting">
              <i :class="applicationSubmitting ? 'fas fa-spinner fa-spin' : 'fas fa-paper-plane'" aria-hidden="true"></i>
              {{ applicationSubmitting ? 'Sending...' : 'Send application' }}
            </button>
            <p v-if="applicationError" class="contact-feedback contact-failure" role="alert">{{ applicationError }}</p>
          </form>
        </template>
        <div v-else class="application-confirmation" role="status">
          <span class="confirmation-icon"><i class="fas fa-check"></i></span>
          <h2 id="application-title">Application received</h2>
          <p>Thank you for your interest. The Aplos Global team will follow up using the contact details you provided.</p>
          <button type="button" class="btn btn-primary" @click="closeApplication">Done</button>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="page-shell">
    <div class="topbar">
      <div class="container topbar-inner">
        <div class="topbar-left">
          <span><i class="fas fa-phone"></i> +971 56 668 2098</span>
          <span><i class="fas fa-envelope"></i> contact@aplosglobal.com</span>
        </div>
        <div class="topbar-right">
          <a href="#"><i class="fas fa-globe"></i> EN</a>
          <a href="/candidate-portal"><i class="fas fa-user"></i> Candidate Portal</a>
          <a href="/employer-portal"><i class="fas fa-briefcase"></i> Employer Portal</a>
        </div>
      </div>
    </div>

    <header class="site-header">
      <div class="container header-main">
        <a href="#" class="brand">
          <span class="brand-mark">A</span>
          <span class="brand-copy">
            <span class="brand-name">Aplos Global</span>
            <span class="brand-tag">Workforce Infrastructure</span>
          </span>
        </a>

        <nav :class="{ 'nav-open': mobileOpen }">
          <ul>
            <li v-for="item in navItems" :key="item.label">
              <a
                :href="item.label === 'Home' ? '/' : item.label === 'About' ? '/about' : item.label === 'Services' ? '/#services' : item.label === 'Offices' ? '/offices' : item.label === 'Career' ? '/find-jobs' : item.label === 'Contact' ? '/#contact' : '#'"
                :class="{ active: item.active }"
                @click="mobileOpen = false"
              >
                {{ item.label }}
              </a>
            </li>
          </ul>
        </nav>

        <div class="header-actions">
          <a href="/find-jobs" class="btn btn-ghost">Find Jobs</a>
          <a href="#contact" class="btn btn-primary">Hire Talent</a>
          <button class="mobile-toggle" @click="mobileOpen = !mobileOpen" aria-label="Toggle menu">
            <i :class="mobileOpen ? 'fas fa-times' : 'fas fa-bars'" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <div class="eyebrow"><i class="fas fa-globe-americas"></i> Think Global, Act Local</div>
            <h1>We are a global <em>workforce infrastructure</em> company.</h1>
            <p class="lead">
              Aplos Global LLC provides end-to-end workforce solutions for employers and supports individuals build sustainable careers across the world. We structure cross-border workforce systems for governments and corporations.
            </p>
            <div class="hero-actions">
              <a href="/find-jobs" class="btn btn-orange">Explore Opportunities <i class="fas fa-arrow-right"></i></a>
              <a href="#contact" class="btn btn-outline-white">Partner With Us</a>
            </div>
            <div class="hero-stats">
              <div class="stat" v-for="item in heroStats" :key="item.lbl">
                <div class="num">{{ item.num }}<span v-if="item.suffix">{{ item.suffix }}</span></div>
                <div class="lbl">{{ item.lbl }}</div>
              </div>
            </div>
          </div>

          <div class="hero-panel">
            <div class="network-card">
              <h3><i class="fas fa-network-wired"></i> Active Operations</h3>
              <p class="card-sub">Supply, demand & mixed markets across the globe</p>

              <div class="market-row" v-for="market in markets" :key="market.name">
                <span class="market-name">
                  <span class="flag-dot" :class="{ orange: market.orange }"></span>
                  {{ market.name }}
                </span>
                <span class="count">{{ market.count }} <small>markets</small></span>
              </div>

              <div class="network-footer">
                <span class="label">Expanding to 14 new countries</span>
                <a href="#" class="btn btn-teal">View Network <i class="fas fa-arrow-right"></i></a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="partners-section">
        <div class="container">
          <div class="section-head">
            <div>
              <span class="label">Global Footprint</span>
              <h2>Our Partner Countries</h2>
              <p>Aplos Global LLC maintains active operations across supply, demand, and mixed markets — enabling strategic mobility and scalable international workforce solutions.</p>
            </div>
            <a href="/offices" class="link-arrow">View All Offices <i class="fas fa-arrow-right"></i></a>
          </div>

          <div class="country-pills">
            <span class="country-pill" v-for="country in activeCountries" :key="country">
              <i class="fas fa-check-circle"></i> {{ country }}
            </span>
          </div>

          <div class="coming-block">
            <div class="section-head compact">
              <div>
                <span class="label accent">Coming Soon</span>
                <h2>Expanding Our Global Presence</h2>
                <p>We're growing beyond borders — bringing expertise closer to the markets and communities we serve.</p>
              </div>
            </div>
            <div class="country-pills">
              <span class="country-pill coming" v-for="country in comingCountries" :key="country">
                <i class="fas fa-clock"></i> {{ country }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section id="services" class="services-section">
        <div class="container">
          <div class="section-head">
            <div>
              <span class="label">What We Do</span>
              <h2>Integrated group services</h2>
              <p>An end-to-end recruitment model covering sourcing, compliance, placement, and integration — supported by robust talent infrastructure.</p>
            </div>
            <a href="#" class="link-arrow">All Services <i class="fas fa-arrow-right"></i></a>
          </div>

          <div class="services-grid">
            <article class="service-card" v-for="item in services" :key="item.title">
              <div class="service-icon"><i :class="item.icon"></i></div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
              <a href="#" class="learn-more">Learn More <i class="fas fa-arrow-right"></i></a>
            </article>
          </div>
        </div>
      </section>

      <section class="values-section">
        <div class="container values-grid">
          <div class="values-content">
            <span class="label">Our Core Values</span>
            <h2>Built on <em>trust</em>, compliance, and operational excellence.</h2>
            <p>
              Aplos Global LLC is a migration-specialized organization with global reach and local execution. Since our founding, we've expanded across Europe, the Middle East, and Asia — building a robust talent infrastructure.
            </p>

            <div v-for="value in values" :key="value.title" class="value-item">
              <div class="value-icon"><i :class="value.icon"></i></div>
              <div>
                <h4>{{ value.title }}</h4>
                <p>{{ value.desc }}</p>
              </div>
            </div>
          </div>

          <div class="impact-stack">
            <div class="impact-stat">
              <div class="big-num">8,500<span>+</span></div>
              <div class="desc">Foreign workers successfully integrated worldwide</div>
            </div>
            <div class="impact-stat orange">
              <div class="big-num">30<span>+</span></div>
              <div class="desc">Partner countries across supply & demand markets</div>
            </div>
          </div>
        </div>
      </section>

      <section id="offices" class="offices-section">
        <div class="container">
          <div class="section-head">
            <div>
              <span class="label">Global Network</span>
              <h2>Our International Offices</h2>
              <p>Explore our global network — reach out to the office nearest you for localized support and solutions.</p>
            </div>
          </div>

          <div class="region-tabs">
            <button
              v-for="region in regions"
              :key="region"
              class="region-tab"
              :class="{ active: activeRegion === region }"
              @click="activeRegion = region"
            >
              {{ region }}
            </button>
          </div>

          <div class="office-grid">
            <article class="office-card" v-for="(office, index) in filteredOffices" :key="activeRegion + index">
              <span class="office-tag">{{ office.region }}</span>
              <h3><i class="fas fa-map-pin"></i> {{ office.country }}</h3>
              <div class="address">{{ office.address }}</div>
              <div class="contact-line" v-if="office.phone">
                <i class="fas fa-phone"></i>
                <a :href="'tel:' + office.phone">{{ office.phone }}</a>
              </div>
              <div class="contact-line" v-if="office.email">
                <i class="fas fa-envelope"></i>
                <a :href="'mailto:' + office.email">{{ office.email }}</a>
              </div>
              <a href="#" class="directions">Get directions <i class="fas fa-arrow-right"></i></a>
            </article>
          </div>
        </div>
      </section>

      <section class="press-section">
        <div class="container">
          <div class="section-head">
            <div>
              <span class="label">In the News</span>
              <h2>Latest press articles</h2>
              <p>Aplos Global LLC in the media — global economic stories, workforce insights, and international mobility coverage.</p>
            </div>
          </div>

          <div class="press-grid">
            <article class="press-card" v-for="article in press" :key="article.title">
              <span class="press-source">{{ article.source }}</span>
              <h3>{{ article.title }}</h3>
              <a href="#" class="read-more">Read Article <i class="fas fa-arrow-right"></i></a>
            </article>
          </div>
        </div>
      </section>

      <section id="contact" class="contact-section">
        <div class="container contact-grid">
          <div class="contact-copy">
            <span class="label">Get in touch</span>
            <h2>Let’s build your global workforce together.</h2>
            <p>
              Tell us what you need. Our team will review your inquiry and get back to you.
            </p>
            <div class="contact-detail">
              <i class="fas fa-envelope" aria-hidden="true"></i>
              <a href="mailto:contact@aplosglobal.com">contact@aplosglobal.com</a>
            </div>
            <div class="contact-detail">
              <i class="fas fa-phone" aria-hidden="true"></i>
              <a href="tel:+971566682098">+971 56 668 2098</a>
            </div>
          </div>

          <form class="contact-form" @submit.prevent="sendContactInquiry">
            <div class="contact-fields">
              <label class="form-field">
                <span>First name <span class="required-mark">*</span></span>
                <input
                  v-model.trim="contactForm.first_name"
                  name="first_name"
                  type="text"
                  autocomplete="given-name"
                  minlength="1"
                  maxlength="60"
                  placeholder="Your first name"
                  required
                >
              </label>
              <label class="form-field">
                <span>Last name <span class="required-mark">*</span></span>
                <input
                  v-model.trim="contactForm.last_name"
                  name="last_name"
                  type="text"
                  autocomplete="family-name"
                  minlength="1"
                  maxlength="60"
                  placeholder="Your last name"
                  required
                >
              </label>
              <label class="form-field">
                <span>Email <span class="required-mark">*</span></span>
                <input
                  v-model.trim="contactForm.email"
                  name="email"
                  type="email"
                  autocomplete="email"
                  maxlength="254"
                  placeholder="you@gmail.com"
                  required
                >
              </label>
              <label class="form-field">
                <span>Nationality</span>
                <input
                  v-model.trim="contactForm.nationality"
                  name="nationality"
                  type="text"
                  autocomplete="country-name"
                  maxlength="80"
                  placeholder="e.g. Bangladeshi"
                >
              </label>
              <label class="form-field">
                <span>Phone (include country code)</span>
                <input
                  v-model.trim="contactForm.phone"
                  name="phone"
                  type="tel"
                  autocomplete="tel"
                  maxlength="40"
                  placeholder="+971 50 123 4567"
                >
              </label>
              <label class="form-field form-field-full">
                <span>How can we help? <span class="required-mark">*</span></span>
                <select v-model="contactForm.service" name="service" required>
                  <option disabled value="">Choose a service</option>
                  <option v-for="item in services" :key="item.title" :value="item.title">
                    {{ item.title }}
                  </option>
                  <option value="Student Visa">Student Visa</option>
                  <option value="Employer Solutions">Employer Solutions</option>
                  <option value="Other">Other inquiry</option>
                </select>
              </label>
              <label class="form-field form-field-full">
                <span>Your message <span class="required-mark">*</span></span>
                <textarea
                  v-model.trim="contactForm.message"
                  name="message"
                  rows="5"
                  minlength="10"
                  maxlength="4000"
                  placeholder="Share a few details about your workforce needs..."
                  required
                ></textarea>
              </label>
              <div class="form-field form-field-full">
                <span>Upload CV <span class="optional-mark">(optional, PDF up to 5 MB)</span></span>
                <input
                  ref="contactCvInput"
                  class="resume-file-input"
                  name="cv"
                  type="file"
                  accept=".pdf,application/pdf"
                  aria-label="Upload CV as PDF"
                  @change="selectContactCv"
                >
                <p v-if="contactCv" class="selected-resume" role="status">
                  <i class="fas fa-file-pdf" aria-hidden="true"></i>
                  {{ contactCv.name }}
                </p>
                <p v-if="contactCvError" class="resume-error" role="alert">{{ contactCvError }}</p>
                <p class="contact-cv-privacy">Your CV will be stored securely with your inquiry for our team to review.</p>
              </div>
            </div>

            <button class="btn btn-primary contact-submit" type="submit" :disabled="contactSubmitting">
              <i
                :class="contactSubmitting ? 'fas fa-spinner fa-spin' : 'fas fa-paper-plane'"
                aria-hidden="true"
              ></i>
              {{ contactSubmitting ? 'Sending...' : 'Send inquiry' }}
            </button>
            <p v-if="contactSubmitted" class="contact-feedback contact-success" role="status">
              <i class="fas fa-check-circle" aria-hidden="true"></i>
              Your inquiry was sent successfully. Our team will be in touch.
            </p>
            <p v-if="contactError" class="contact-feedback contact-failure" role="alert">
              {{ contactError }}
            </p>
          </form>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container footer-grid">
        <div class="footer-brand">
          <a href="#" class="brand footer-brand-link">
            <span class="brand-mark">A</span>
            <span class="brand-copy">
              <span class="brand-name">Aplos Global</span>
              <span class="brand-tag">Workforce Infrastructure</span>
            </span>
          </a>
          <p>We create high-impact workforce systems for governments, employers, and international talent communities.</p>
          <div class="socials">
            <a href="#"><i class="fab fa-linkedin-in"></i></a>
            <a href="#"><i class="fab fa-instagram"></i></a>
            <a href="#"><i class="fab fa-facebook-f"></i></a>
            <a href="#"><i class="fab fa-youtube"></i></a>
          </div>
        </div>

        <div class="footer-col">
          <h4>Company</h4>
          <ul>
            <li v-for="link in ['About', 'Our Offices', 'Careers', 'Press & Media', 'Contact']" :key="link">
              <a href="#">{{ link }}</a>
            </li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Services</h4>
          <ul>
            <li v-for="link in ['Migration & Legal', 'Relocation & Settlement', 'Recruitment & Employment', 'Career & Education', 'Employer Solutions']" :key="link">
              <a href="#">{{ link }}</a>
            </li>
          </ul>
        </div>

        <div class="footer-col footer-news">
          <h4>Stay Updated</h4>
          <p>Get the latest job opportunities, market insights, and Aplos Global news delivered to your inbox.</p>
          <form class="newsletter-form" @submit.prevent="subscribe">
            <input v-model="email" type="email" placeholder="Your email address" required>
            <button type="submit" aria-label="Subscribe" :disabled="subscribing">
              <i :class="subscribing ? 'fas fa-spinner fa-spin' : 'fas fa-paper-plane'" aria-hidden="true"></i>
            </button>
          </form>
          <p v-if="subscribed" class="subscribe-note">
            <i class="fas fa-check-circle"></i> Thanks! You're subscribed.
          </p>
          <p v-if="subscribeError" class="subscribe-error" role="alert">{{ subscribeError }}</p>
        </div>
      </div>

      <div class="container footer-bottom">
        <div>© 2026 Aplos Global LLC. All rights reserved.</div>
        <div class="legal-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Cookie Policy</a>
          <a href="#">Compliance</a>
        </div>
      </div>
    </footer>
    <a class="whatsapp-float" href="https://wa.me/8801760818130" target="_blank" rel="noopener noreferrer" aria-label="Chat with Aplos Global on WhatsApp">
      <i class="fab fa-whatsapp" aria-hidden="true"></i>
    </a>
    <a class="messenger-float" href="https://m.me/aplosglobaltravelsllc" target="_blank" rel="noopener noreferrer" aria-label="Message Aplos Global on Messenger">
      <i class="fab fa-facebook-messenger" aria-hidden="true"></i>
    </a>
  </div>
</template>
