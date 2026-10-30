"""
Database schema definitions and table initializations.
Implements the 7 required tables with foreign keys and performance indexes.
"""

from database.connection import get_db_cursor
from config.settings import get_logger

logger = get_logger(__name__)

SCHEMA_SQL = """
-- 1. Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    location TEXT,
    target_roles TEXT,          -- JSON list of strings
    skills TEXT,                -- JSON list of strings
    experience_years REAL DEFAULT 0.0,
    min_salary_lpa REAL DEFAULT 6.0,
    max_salary_lpa REAL DEFAULT 10.0,
    preferred_locations TEXT,   -- JSON list of strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT,
    parsed_text TEXT,
    skills_extracted TEXT,      -- JSON list
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- 3. Companies table
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    normalized_name TEXT UNIQUE NOT NULL,
    website TEXT,
    career_page_url TEXT,
    industry TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_job_id TEXT,
    platform TEXT NOT NULL,          -- Naukri, LinkedIn, Indeed, Wellfound, Instahyre, Cutshort, CareerPages
    company_id INTEGER,
    company_name TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    is_remote INTEGER DEFAULT 0,
    salary_raw TEXT,
    min_salary_lpa REAL,
    max_salary_lpa REAL,
    min_experience_years REAL DEFAULT 0.0,
    max_experience_years REAL DEFAULT 1.0,
    required_skills TEXT,           -- JSON list
    description TEXT,
    url TEXT NOT NULL,
    raw_data TEXT,                  -- JSON string of original payload
    match_score REAL DEFAULT 0.0,   -- 0 - 100
    match_breakdown TEXT,           -- JSON breakdown
    duplicate_hash TEXT UNIQUE,     -- SHA256 of normalized (title, company, location)
    is_duplicate INTEGER DEFAULT 0,
    duplicate_of_id INTEGER,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'DISCOVERED', -- DISCOVERED, MATCHED, REJECTED_LOW_SCORE, DUPLICATE
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL,
    FOREIGN KEY (duplicate_of_id) REFERENCES jobs(id) ON DELETE SET NULL
);

-- 5. Applications table
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    resume_id INTEGER,
    status TEXT NOT NULL DEFAULT 'PREPARED', -- PREPARED, PENDING_APPROVAL, APPROVED, REJECTED_BY_USER, SUBMITTED, FAILED
    autofill_payload TEXT,                  -- JSON filled form answers
    cover_letter TEXT,
    notes TEXT,
    submitted_at TIMESTAMP,
    confirmation_id TEXT,
    confirmation_url TEXT,
    screenshot_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL,
    CONSTRAINT unique_job_candidate_application UNIQUE (candidate_id, job_id)
);

-- 6. Application status history & recruiter interaction
CREATE TABLE IF NOT EXISTS application_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    status TEXT NOT NULL, -- PREPARED, PENDING_APPROVAL, APPROVED, SUBMITTED, UNDER_REVIEW, INTERVIEW_SCHEDULED, REJECTED, OFFER
    recruiter_response TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- 7. Daily reports table
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE UNIQUE NOT NULL,
    total_discovered INTEGER DEFAULT 0,
    total_matched INTEGER DEFAULT 0,
    total_prepared INTEGER DEFAULT 0,
    total_submitted INTEGER DEFAULT 0,
    pending_approvals INTEGER DEFAULT 0,
    best_opportunities_json TEXT,  -- JSON list of top 10
    errors_json TEXT,              -- JSON list of errors
    summary_markdown TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for lightning-fast queries
CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform);
CREATE INDEX IF NOT EXISTS idx_jobs_match_score ON jobs(match_score);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_discovered_at ON jobs(discovered_at);
CREATE INDEX IF NOT EXISTS idx_jobs_dup_hash ON jobs(duplicate_hash);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_app_status_app_id ON application_status(application_id);
"""

def init_db() -> None:
    """Initialize all database tables and indexes."""
    with get_db_cursor() as cursor:
        cursor.executescript(SCHEMA_SQL)
    logger.info("Database schema initialized successfully.")

if __name__ == "__main__":
    init_db()

