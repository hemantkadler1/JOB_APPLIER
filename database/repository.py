"""
Data access layer (Repository Pattern) for the SQLite database.
Handles queries, updates, transactions, and aggregate analytics.
"""

import json
import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from database.connection import get_connection, get_db_cursor
from config.settings import get_logger

logger = get_logger(__name__)

class JobRepository:
    """Repository handling all database operations."""

    # ---------------- Candidates ----------------
    def upsert_candidate(self, candidate_data: Dict[str, Any]) -> int:
        """Insert or update candidate record and return its ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id FROM candidates WHERE email = ?", (candidate_data["email"],))
            existing = cursor.fetchone()
            if existing:
                cand_id = existing["id"]
                cursor.execute("""
                    UPDATE candidates
                    SET name = ?, phone = ?, location = ?, target_roles = ?, skills = ?,
                        experience_years = ?, min_salary_lpa = ?, max_salary_lpa = ?,
                        preferred_locations = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    candidate_data["name"],
                    candidate_data.get("phone"),
                    candidate_data.get("current_location"),
                    json.dumps(candidate_data.get("target_roles", [])),
                    json.dumps(candidate_data.get("skills", [])),
                    candidate_data.get("experience_years", 0.0),
                    candidate_data.get("min_salary_lpa", 6.0),
                    candidate_data.get("max_salary_lpa", 10.0),
                    json.dumps(candidate_data.get("preferred_locations", [])),
                    cand_id
                ))
                return cand_id
            else:
                cursor.execute("""
                    INSERT INTO candidates (
                        name, email, phone, location, target_roles, skills,
                        experience_years, min_salary_lpa, max_salary_lpa, preferred_locations
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    candidate_data["name"],
                    candidate_data["email"],
                    candidate_data.get("phone"),
                    candidate_data.get("current_location"),
                    json.dumps(candidate_data.get("target_roles", [])),
                    json.dumps(candidate_data.get("skills", [])),
                    candidate_data.get("experience_years", 0.0),
                    candidate_data.get("min_salary_lpa", 6.0),
                    candidate_data.get("max_salary_lpa", 10.0),
                    json.dumps(candidate_data.get("preferred_locations", []))
                ))
                return cursor.lastrowid

    def get_candidate(self) -> Optional[Dict[str, Any]]:
        """Fetch primary candidate details."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates ORDER BY id ASC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["target_roles"] = json.loads(data["target_roles"]) if data["target_roles"] else []
            data["skills"] = json.loads(data["skills"]) if data["skills"] else []
            data["preferred_locations"] = json.loads(data["preferred_locations"]) if data["preferred_locations"] else []
            return data
        finally:
            conn.close()

    # ---------------- Resumes ----------------
    def save_resume(self, candidate_id: int, filename: str, file_path: str,
                    parsed_text: str, skills_extracted: List[str], file_hash: Optional[str] = None) -> int:
        """Register parsed resume in DB."""
        with get_db_cursor() as cursor:
            cursor.execute("UPDATE resumes SET is_active = 0 WHERE candidate_id = ?", (candidate_id,))
            cursor.execute("""
                INSERT INTO resumes (candidate_id, filename, file_path, file_hash, parsed_text, skills_extracted, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                candidate_id,
                filename,
                file_path,
                file_hash,
                parsed_text,
                json.dumps(skills_extracted)
            ))
            return cursor.lastrowid

    def get_active_resume(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Fetch active resume for candidate."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE candidate_id = ? AND is_active = 1 LIMIT 1", (candidate_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["skills_extracted"] = json.loads(data["skills_extracted"]) if data["skills_extracted"] else []
            return data
        finally:
            conn.close()

    # ---------------- Companies ----------------
    def find_or_create_company(self, name: str, website: Optional[str] = None, career_page_url: Optional[str] = None) -> int:
        """Normalize company name and return existing or new company ID."""
        normalized = name.strip().lower()
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id FROM companies WHERE normalized_name = ?", (normalized,))
            existing = cursor.fetchone()
            if existing:
                return existing["id"]
            cursor.execute("""
                INSERT INTO companies (name, normalized_name, website, career_page_url)
                VALUES (?, ?, ?, ?)
            """, (name.strip(), normalized, website, career_page_url))
            return cursor.lastrowid

    # ---------------- Jobs ----------------
    def insert_job(self, job_dict: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Insert job. Detects duplicate by hash.
        Returns (job_id, is_duplicate).
        """
        dup_hash = job_dict.get("duplicate_hash")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if dup_hash:
                cursor.execute("SELECT id FROM jobs WHERE duplicate_hash = ?", (dup_hash,))
                existing = cursor.fetchone()
                if existing:
                    return (existing["id"], True)
        finally:
            conn.close()

        # Create company
        company_id = self.find_or_create_company(
            name=job_dict["company_name"],
            career_page_url=job_dict.get("url")
        )

        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobs (
                    external_job_id, platform, company_id, company_name, title,
                    location, is_remote, salary_raw, min_salary_lpa, max_salary_lpa,
                    min_experience_years, max_experience_years, required_skills,
                    description, url, raw_data, match_score, match_breakdown,
                    duplicate_hash, is_duplicate, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_dict.get("external_job_id"),
                job_dict["platform"],
                company_id,
                job_dict["company_name"],
                job_dict["title"],
                job_dict.get("location", "India"),
                1 if job_dict.get("is_remote") else 0,
                job_dict.get("salary_raw"),
                job_dict.get("min_salary_lpa"),
                job_dict.get("max_salary_lpa"),
                job_dict.get("min_experience_years", 0.0),
                job_dict.get("max_experience_years", 1.0),
                json.dumps(job_dict.get("required_skills", [])),
                job_dict.get("description", ""),
                job_dict["url"],
                json.dumps(job_dict.get("raw_data", {})),
                job_dict.get("match_score", 0.0),
                json.dumps(job_dict.get("match_breakdown", {})),
                dup_hash,
                0,
                job_dict.get("status", "DISCOVERED")
            ))
            return (cursor.lastrowid, False)

    def update_job_match(self, job_id: int, match_score: float, match_breakdown: Dict[str, Any], status: str) -> None:
        """Update job score and status."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE jobs
                SET match_score = ?, match_breakdown = ?, status = ?
                WHERE id = ?
            """, (match_score, json.dumps(match_breakdown), status, job_id))

    def get_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single job with all details."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._format_job_row(row)
        finally:
            conn.close()

    def get_jobs(self, min_score: Optional[float] = None, platform: Optional[str] = None,
                 status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Search and filter jobs with pagination."""
        query = "SELECT * FROM jobs WHERE 1=1"
        params: List[Any] = []

        if min_score is not None:
            query += " AND match_score >= ?"
            params.append(min_score)
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY match_score DESC, discovered_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [self._format_job_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def _format_job_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert job row to rich Python dictionary."""
        d = dict(row)
        d["required_skills"] = json.loads(d["required_skills"]) if d.get("required_skills") else []
        d["match_breakdown"] = json.loads(d["match_breakdown"]) if d.get("match_breakdown") else {}
        d["raw_data"] = json.loads(d["raw_data"]) if d.get("raw_data") else {}
        return d

    # ---------------- Applications ----------------
    def create_or_get_application(self, candidate_id: int, job_id: int, resume_id: Optional[int],
                                 autofill_payload: Dict[str, Any], status: str = "PENDING_APPROVAL") -> Tuple[int, bool]:
        """
        Create application in PENDING_APPROVAL status.
        Returns (application_id, is_new).
        """
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id FROM applications WHERE candidate_id = ? AND job_id = ?", (candidate_id, job_id))
            existing = cursor.fetchone()
            if existing:
                return (existing["id"], False)

            cursor.execute("""
                INSERT INTO applications (candidate_id, job_id, resume_id, status, autofill_payload)
                VALUES (?, ?, ?, ?, ?)
            """, (
                candidate_id,
                job_id,
                resume_id,
                status,
                json.dumps(autofill_payload)
            ))
            app_id = cursor.lastrowid

            # Add initial status entry
            cursor.execute("""
                INSERT INTO application_status (application_id, status, notes)
                VALUES (?, ?, 'Prepared for candidate approval')
            """, (app_id, status))

            return (app_id, True)

    def update_application_status(self, application_id: int, status: str, notes: Optional[str] = None,
                                  recruiter_response: Optional[str] = None, confirmation_id: Optional[str] = None,
                                  confirmation_url: Optional[str] = None, screenshot_path: Optional[str] = None) -> None:
        """Update application status, confirmation receipts, and append history."""
        with get_db_cursor() as cursor:
            update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            params: List[Any] = [status]

            if status == "SUBMITTED":
                update_fields.append("submitted_at = CURRENT_TIMESTAMP")
            if confirmation_id:
                update_fields.append("confirmation_id = ?")
                params.append(confirmation_id)
            if confirmation_url:
                update_fields.append("confirmation_url = ?")
                params.append(confirmation_url)
            if screenshot_path:
                update_fields.append("screenshot_path = ?")
                params.append(screenshot_path)
            if notes:
                update_fields.append("notes = ?")
                params.append(notes)

            params.append(application_id)
            cursor.execute(f"UPDATE applications SET {', '.join(update_fields)} WHERE id = ?", params)

            # Insert history record
            cursor.execute("""
                INSERT INTO application_status (application_id, status, recruiter_response, notes)
                VALUES (?, ?, ?, ?)
            """, (application_id, status, recruiter_response, notes or f"Status changed to {status}"))

    def get_applications(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch applications with joined job and candidate info."""
        query = """
            SELECT a.*, j.title as job_title, j.company_name, j.url as job_url,
                   j.location as job_location, j.salary_raw as job_salary,
                   j.match_score, j.platform, c.name as candidate_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN candidates c ON a.candidate_id = c.id
        """
        params: List[Any] = []
        if status:
            query += " WHERE a.status = ?"
            params.append(status)
        query += " ORDER BY j.match_score DESC, a.created_at DESC"

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            res = []
            for r in cursor.fetchall():
                d = dict(r)
                d["autofill_payload"] = json.loads(d["autofill_payload"]) if d.get("autofill_payload") else {}
                res.append(d)
            return res
        finally:
            conn.close()

    def get_application_history(self, application_id: int) -> List[Dict[str, Any]]:
        """Get status change timeline for application."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM application_status
                WHERE application_id = ?
                ORDER BY created_at ASC
            """, (application_id,))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------- Daily Reports ----------------
    def save_daily_report(self, report_data: Dict[str, Any]) -> int:
        """Upsert daily report for given report date."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO daily_reports (
                    report_date, total_discovered, total_matched, total_prepared,
                    total_submitted, pending_approvals, best_opportunities_json,
                    errors_json, summary_markdown
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(report_date) DO UPDATE SET
                    total_discovered = excluded.total_discovered,
                    total_matched = excluded.total_matched,
                    total_prepared = excluded.total_prepared,
                    total_submitted = excluded.total_submitted,
                    pending_approvals = excluded.pending_approvals,
                    best_opportunities_json = excluded.best_opportunities_json,
                    errors_json = excluded.errors_json,
                    summary_markdown = excluded.summary_markdown
            """, (
                report_data["report_date"],
                report_data.get("total_discovered", 0),
                report_data.get("total_matched", 0),
                report_data.get("total_prepared", 0),
                report_data.get("total_submitted", 0),
                report_data.get("pending_approvals", 0),
                json.dumps(report_data.get("best_opportunities", [])),
                json.dumps(report_data.get("errors", [])),
                report_data.get("summary_markdown", "")
            ))
            return cursor.lastrowid

    def get_daily_report(self, report_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch daily report by date (defaults to today)."""
        target_date = report_date or date.today().isoformat()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_reports WHERE report_date = ? LIMIT 1", (target_date,))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["best_opportunities"] = json.loads(d["best_opportunities_json"]) if d.get("best_opportunities_json") else []
            d["errors"] = json.loads(d["errors_json"]) if d.get("errors_json") else []
            return d
        finally:
            conn.close()

    # ---------------- System Statistics ----------------
    def get_system_stats(self) -> Dict[str, Any]:
        """Aggregate high-level system metrics for dashboard."""
        today_str = date.today().isoformat()
        seven_days_ago = (date.today() - timedelta(days=7)).isoformat()

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Discovered today
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE DATE(discovered_at) = ?", (today_str,))
            discovered_today = cursor.fetchone()[0]

            # Total discovered
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total_discovered = cursor.fetchone()[0]

            # Matching profile (>= 70)
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE match_score >= 70")
            matching_jobs = cursor.fetchone()[0]

            # Pending approvals
            cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'PENDING_APPROVAL'")
            pending_approvals = cursor.fetchone()[0]

            # Total submitted
            cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'SUBMITTED'")
            submitted = cursor.fetchone()[0]

            # Rejected jobs
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'REJECTED_LOW_SCORE'")
            rejected_jobs = cursor.fetchone()[0]

            # Interview opportunities
            cursor.execute("""
                SELECT COUNT(*) FROM applications
                WHERE status IN ('INTERVIEW_SCHEDULED', 'UNDER_REVIEW', 'OFFER')
            """)
            interviews = cursor.fetchone()[0]

            # Platform breakdown
            cursor.execute("""
                SELECT platform, COUNT(*) as count, AVG(match_score) as avg_score
                FROM jobs
                GROUP BY platform
            """)
            platform_stats = [dict(r) for r in cursor.fetchall()]

            # 7-day trend
            cursor.execute("""
                SELECT DATE(discovered_at) as date, COUNT(*) as count
                FROM jobs
                WHERE DATE(discovered_at) >= ?
                GROUP BY DATE(discovered_at)
                ORDER BY date ASC
            """, (seven_days_ago,))
            daily_trend = [dict(r) for r in cursor.fetchall()]

            return {
                "discovered_today": discovered_today,
                "total_discovered": total_discovered,
                "matching_jobs": matching_jobs,
                "pending_approvals": pending_approvals,
                "submitted": submitted,
                "rejected_jobs": rejected_jobs,
                "interviews": interviews,
                "platform_stats": platform_stats,
                "daily_trend": daily_trend
            }
        finally:
            conn.close()
