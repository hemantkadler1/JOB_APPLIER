# 💼 AI Daily Job Application Automation System

A production-quality, ethical, and intelligent Daily Job Application Agent built specifically for **Hemant Manjunath Kadler**.

Designed to automatically discover software development jobs across India, score them using multi-criteria AI matching against Hemant's verified resume, prepare truthful application forms, and provide a human-in-the-loop Streamlit approval dashboard.

---

## 🎯 1. Candidate Profile

- **Candidate:** Hemant Manjunath Kadler
- **Current Role:** Associate Software Engineer at Skyllx Technologies Private Limited (Healthcare ERPs: *HealthMatrix360*, *IVFCareX*, *DentoCareX*)
- **Experience:** Under 1 year of professional experience (< 1 year)
- **Education:** B.E. in Computer Science Engineering — Vidyavardhaka College of Engineering, Mysore (CGPA: 8.58)
- **Core Skills:** Java, Spring Boot, React.js, Next.js, JavaScript, REST APIs, Microservices, MySQL, Docker, Jenkins, CI/CD, Android & iOS Development
- **Expected Salary:** ₹6–10 LPA
- **Preferred Locations:** Bengaluru, Remote – India, Anywhere in India
- **Target Roles:**
  - Java Developer
  - Spring Boot Developer
  - Software Engineer
  - Backend Developer
  - Full Stack Developer
  - React Developer
  - Associate Software Engineer
  - Application Developer

---

## 🏗️ 2. Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │            7 Discovery Channels              │
                      │  Naukri | LinkedIn | Indeed | Wellfound       │
                      │  Instahyre | Cutshort | Career Pages         │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │      Deduplication & Canonicalizer           │
                      │   SHA-256 (Normalized Title + Company + Loc) │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │           AI Job Matching Engine             │
                      │   Skills (40%) | Title (25%) | Exp (20%)     │
                      │   Location (10%) | Salary (5%)               │
                      │   Threshold: Score >= 70%                    │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Truthful Application Payload Builder       │
                      │   - Verified Resume Data (No Hallucinations)  │
                      │   - Status: PENDING_APPROVAL                  │
                      └──────────────────────┬───────────────────────┘
                                             │
                        ┌────────────────────┴───────────────────┐
                        ▼                                        ▼
             ┌─────────────────────┐                 ┌──────────────────────┐
             │ SQLite Storage (WAL)│                 │  Daily 9:00 AM IST   │
             │   7 Relational      │                 │  APScheduler Runner  │
             │      Tables         │                 │  & Markdown Reports  │
             └──────────┬──────────┘                 └──────────────────────┘
                        │
                        ▼
             ┌──────────────────────────────────────────────────┐
             │         Streamlit Interactive Dashboard          │
             │  - KPIs & Funnel Metrics                         │
             │  - Human Approval Queue (Approve / Reject)       │
             │  - Job Discovery Explorer                        │
             │  - Application Tracker & Interview Opportunities │
             │  - Live AI Matcher Sandbox                       │
             └──────────────────────────────────────────────────┘
```

---

## 🗄️ 3. Database Schema

Stored persistently in `candidate_jobs.db` (SQLite with WAL mode and foreign keys enabled):

1. **`candidates`**: Personal contact, career parameters, target roles, verified skills, salary preferences.
2. **`resumes`**: Ingested resume files, SHA-256 fingerprint, parsed text, and extracted tech skills.
3. **`companies`**: Normalized company directory and career URLs.
4. **`jobs`**: Normalized job listings, salary bands, experience limits, duplicate hashes, match scores, and status (`MATCHED`, `REJECTED_LOW_SCORE`, `DUPLICATE`).
5. **`applications`**: Application records linked to jobs and candidate, truthful autofill payload, submission receipts, screenshot paths, and statuses (`PREPARED`, `PENDING_APPROVAL`, `SUBMITTED`, `REJECTED_BY_USER`).
6. **`application_status`**: Audit trail of status transitions, recruiter responses, and interview updates.
7. **`daily_reports`**: Daily metrics snapshot, Top 10 opportunities JSON, and rendered Markdown reports.

---

## 🤖 4. AI Matching Engine Formula

Every job posting is evaluated against Hemant's profile with a 0–100 score:

$$\text{Final Score} = (\text{Skills} \times 0.40) + (\text{Title} \times 0.25) + (\text{Experience} \times 0.20) + (\text{Location} \times 0.10) + (\text{Salary} \times 0.05)$$

- **Skills Match (40%):** Weighted overlap with Java, Spring Boot, React, Next.js, Microservices, REST APIs, and MySQL.
- **Title Match (25%):** Alignment with target roles (Associate Software Engineer, Java Developer, Full Stack).
- **Experience Match (20%):** Specifically tuned for < 1 year experience:
  - 0–1 year / Freshers: **100%**
  - 1–2 years: **85%**
  - 2–3 years: **50%**
  - > 3 years: **10%** (Senior roles filtered out)
- **Location Match (10%):** Bengaluru (100%), Remote – India (100%), Anywhere in India (85%).
- **Salary Match (5%):** ₹6–10 LPA target alignment.
- **Threshold:** Jobs scoring `< 70%` are automatically rejected.

---

## 🛡️ 5. Ethical Guidelines & Human Approval Guard

1. **Strict Truthfulness:** The application payload builder draws exclusively from verified experience at Skyllx Technologies, education at Vidyavardhaka College of Engineering, and actual technical competencies. It **never** fabricates experience, qualifications, CTC, or work authorization.
2. **Human-in-the-Loop:** All eligible applications enter `PENDING_APPROVAL` status. Submissions are only triggered after the candidate clicks **Approve & Submit** in the dashboard.
3. **No Hallucinated Submissions:** The Playwright engine requires confirmed HTTP responses, confirmation reference IDs, and verification receipts before marking an application as `SUBMITTED`.
4. **Permitted Feeds & Scraping Compliance:** Respects robots.txt, applies polite rate-limiting delays (1.0–1.5s), and never bypasses CAPTCHAs or platform security walls.

---

## 🚀 6. Getting Started

### Prerequisites
- macOS / Linux / Windows
- Python 3.9+

### Installation

```bash
# 1. Clone or navigate to the project directory
cd /Users/Admin/.gemini/antigravity/scratch/ai_job_agent

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Verify packages
pip install -r requirements.txt
```

### Running the System

#### A. Launch the Streamlit Interactive Dashboard
```bash
streamlit run dashboard/app.py
```
Open **`http://localhost:8501`** in your browser to:
- Review jobs awaiting your approval in the **Approval Queue**.
- Click **Approve & Submit** or **Reject**.
- Explore discovered jobs and AI score breakdowns.
- Track applications and log recruiter responses / interviews.
- Test any job description in the **AI Matcher Sandbox**.

#### B. Run Daily Discovery Pipeline Immediately
```bash
python scheduler/daily_job.py --run-now
```

#### C. Run the 9:00 AM IST APScheduler Background Daemon
```bash
python scheduler/daily_job.py --schedule
```

#### D. Run the Test Suite
```bash
pytest -v
```

---

## 📁 7. Project Structure

```
ai_job_agent/
├── .env                  # Runtime settings and thresholds
├── .env.example          # Environment template
├── candidate_jobs.db     # Persistent SQLite database
├── requirements.txt      # Dependency specification
├── README.md             # Documentation
│
├── config/
│   ├── settings.py           # Paths, logger, and configuration loader
│   └── candidate_profile.py  # Structured candidate profile & verified resume data
│
├── data/
│   ├── resumes/              # Hemant_Kadler_Resume.pdf
│   └── sample_jobs.json      # Offline test fixtures across all 7 platforms
│
├── database/
│   ├── connection.py         # SQLite connection & WAL mode manager
│   ├── models.py             # Schema definition (7 tables)
│   └── repository.py         # CRUD operations and reporting queries
│
├── discovery/
│   ├── base.py               # Abstract base discovery interface
│   ├── naukri.py             # Naukri module
│   ├── linkedin.py           # LinkedIn module
│   ├── indeed.py             # Indeed module
│   ├── wellfound.py          # Wellfound startup module
│   ├── instahyre.py          # Instahyre tech module
│   ├── cutshort.py           # Cutshort fullstack module
│   ├── career_pages.py       # Official company career pages module
│   └── orchestrator.py       # Multi-platform runner
│
├── matching/
│   ├── resume_parser.py      # PDF text and skill extractor
│   ├── deduplicator.py       # Canonical string normalizer & SHA-256 hasher
│   └── matcher.py            # AI weighted matching engine
│
├── application/
│   ├── autofill_payload.py   # Truthful form response generator
│   └── playwright_agent.py   # Permitted browser automation & receipt verifier
│
├── scheduler/
│   ├── daily_job.py          # 9:00 AM IST APScheduler pipeline
│   └── reporter.py           # Markdown & JSON daily report generator
│
├── dashboard/
│   └── app.py                # Streamlit Web UI
│
├── reports/                  # Daily markdown reports and audit screenshots
└── tests/                    # 10 comprehensive unit tests
```

---

## 🧪 8. Test Verification

Run all unit tests:
```bash
./.venv/bin/pytest -v
```

All 10 unit tests pass:
- `test_autofill_payload_truthfulness` ✅
- `test_database_initialization` ✅
- `test_upsert_candidate` ✅
- `test_insert_job_and_deduplication` ✅
- `test_company_normalization` ✅
- `test_title_normalization` ✅
- `test_duplicate_hash_consistency` ✅
- `test_discovery_orchestrator` ✅
- `test_high_match_job` ✅
- `test_senior_or_irrelevant_job` ✅
