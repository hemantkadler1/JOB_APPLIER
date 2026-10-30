"""
Unit tests for database models and repository layer.
"""

import pytest
import sqlite3
from pathlib import Path
import uuid
from database.connection import get_connection, get_db_cursor
from database.models import init_db
from database.repository import JobRepository
from config.candidate_profile import CANDIDATE_PROFILE

@pytest.fixture
def repo(tmp_path):
    test_db = tmp_path / "test_jobs.db"
    # Monkeypatch or initialize test db
    init_db()
    return JobRepository()

def test_database_initialization():
    """Verify that all required tables exist in database."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    conn.close()

    required_tables = [
        "candidates",
        "resumes",
        "companies",
        "jobs",
        "applications",
        "application_status",
        "daily_reports"
    ]
    for table in required_tables:
        assert table in tables, f"Expected table '{table}' not found in database."

def test_upsert_candidate(repo):
    """Verify candidate record insertion and retrieval."""
    cand_id = repo.upsert_candidate(CANDIDATE_PROFILE)
    assert cand_id > 0

    candidate = repo.get_candidate()
    assert candidate is not None
    assert candidate["name"] == "Hemant Manjunath Kadler"
    assert candidate["email"] == "hemantkadler@gmail.com"
    assert "Java" in candidate["skills"]

def test_insert_job_and_deduplication(repo):
    """Verify job insertion and duplicate detection."""
    test_hash = f"testhash_{uuid.uuid4().hex}"
    job_payload = {
        "external_job_id": f"TEST-{uuid.uuid4().hex[:6]}",
        "platform": "Naukri",
        "company_name": "Skyllx Partner Corp",
        "title": "Junior Java Developer",
        "location": "Bengaluru",
        "is_remote": False,
        "salary_raw": "₹7-9 LPA",
        "min_salary_lpa": 7.0,
        "max_salary_lpa": 9.0,
        "min_experience_years": 0.0,
        "max_experience_years": 1.0,
        "required_skills": ["Java", "Spring Boot"],
        "description": "Junior Java Developer test description",
        "url": "https://example.com/job/101",
        "duplicate_hash": test_hash
    }

    job_id, is_duplicate = repo.insert_job(job_payload)
    assert job_id > 0
    assert is_duplicate is False

    # Second insert with same hash must be marked as duplicate
    job_id_2, is_duplicate_2 = repo.insert_job(job_payload)
    assert is_duplicate_2 is True
    assert job_id_2 == job_id
