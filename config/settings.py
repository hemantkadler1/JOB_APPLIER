"""
System settings and configuration loader.
Reads environment variables with fallback defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = DATA_DIR / "resumes"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
for path in [DATA_DIR, RESUMES_DIR, REPORTS_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Load .env file
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# Configuration values
APP_ENV = os.getenv("APP_ENV", "development")
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "candidate_jobs.db")))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH

MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "70"))
EXP_MAX_YEARS_TOLERANCE = float(os.getenv("EXP_MAX_YEARS_TOLERANCE", "2.0"))
MIN_SALARY_LPA = float(os.getenv("MIN_SALARY_LPA", "6.0"))
MAX_SALARY_LPA = float(os.getenv("MAX_SALARY_LPA", "10.0"))

SCHEDULER_HOUR = int(os.getenv("SCHEDULER_HOUR", "9"))
SCHEDULER_MINUTE = int(os.getenv("SCHEDULER_MINUTE", "0"))
SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Kolkata")

DISCOVERY_MOCK_FALLBACK = os.getenv("DISCOVERY_MOCK_FALLBACK", "true").lower() in ("true", "1", "yes")
MAX_JOBS_PER_PLATFORM = int(os.getenv("MAX_JOBS_PER_PLATFORM", "25"))

PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() in ("true", "1", "yes")
PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))
DRY_RUN_APPLICATIONS = os.getenv("DRY_RUN_APPLICATIONS", "true").lower() in ("true", "1", "yes")

NOTIFY_CONSOLE = os.getenv("NOTIFY_CONSOLE", "true").lower() in ("true", "1", "yes")
NOTIFY_FILE = os.getenv("NOTIFY_FILE", "true").lower() in ("true", "1", "yes")

DEFAULT_RESUME_PATH = RESUMES_DIR / "Hemant_Kadler_Resume.pdf"

# Configure logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "job_agent.log", encoding="utf-8")
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Return a logger instance with configured handlers."""
    return logging.getLogger(name)

