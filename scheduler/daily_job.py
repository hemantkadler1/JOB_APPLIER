"""
Daily Job Execution Pipeline and APScheduler Configuration.
Configured to execute every day at 9:00 AM IST (Asia/Kolkata).
Orchestrates:
1. Discover new jobs
2. Deduplicate listings
3. Calculate AI match scores
4. Prepare applications for jobs >= 70%
5. Save pending approvals to database
6. Generate daily Markdown report
7. Notify candidate
"""

import sys
import argparse
from pathlib import Path
from datetime import date
from typing import Dict, Any, List

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import (
    SCHEDULER_HOUR,
    SCHEDULER_MINUTE,
    SCHEDULER_TIMEZONE,
    MIN_MATCH_SCORE,
    DEFAULT_RESUME_PATH,
    get_logger
)
from config.candidate_profile import CANDIDATE_PROFILE
from database.models import init_db
from database.repository import JobRepository
from matching.resume_parser import ResumeParser
from matching.matcher import JobMatcher
from discovery.orchestrator import DiscoveryOrchestrator
from application.autofill_payload import AutofillPayloadBuilder
from scheduler.reporter import DailyReporter

logger = get_logger(__name__)

class DailyJobPipeline:
    """End-to-end daily job automation pipeline."""

    def __init__(self):
        init_db()
        self.repo = JobRepository()
        self.orchestrator = DiscoveryOrchestrator()
        
        # Ingest candidate profile into DB
        self.candidate_id = self.repo.upsert_candidate(CANDIDATE_PROFILE)
        
        # Ingest active resume if available
        self.resume_id = self._sync_resume()
        
        # Initialize AI Matcher and Payload Builder
        self.matcher = JobMatcher(CANDIDATE_PROFILE)
        self.payload_builder = AutofillPayloadBuilder(CANDIDATE_PROFILE, DEFAULT_RESUME_PATH)

    def _sync_resume(self) -> int:
        """Parse and store candidate resume in database."""
        if DEFAULT_RESUME_PATH.exists():
            try:
                parser = ResumeParser(DEFAULT_RESUME_PATH)
                parsed = parser.parse()
                resume_id = self.repo.save_resume(
                    candidate_id=self.candidate_id,
                    filename=parsed["filename"],
                    file_path=parsed["file_path"],
                    parsed_text=parsed["parsed_text"],
                    skills_extracted=parsed["skills_extracted"],
                    file_hash=parsed["file_hash"]
                )
                logger.info(f"Synchronized resume in DB (ID: {resume_id})")
                return resume_id
            except Exception as e:
                logger.error(f"Failed to parse resume: {e}")
        return 1

    def run(self) -> Dict[str, Any]:
        """Execute full daily job search and preparation sequence."""
        logger.info("=" * 60)
        logger.info(f"Starting Daily Job Search Automation Pipeline at {SCHEDULER_HOUR:02d}:{SCHEDULER_MINUTE:02d} IST")
        logger.info("=" * 60)

        errors: List[str] = []
        new_jobs_count = 0
        matched_jobs_count = 0
        prepared_apps_count = 0

        # Step 1: Discover new jobs across all 7 platforms
        keywords = ["Java Developer", "Spring Boot", "React.js", "Full Stack Developer", "Software Engineer"]
        locations = ["Bengaluru", "Remote", "India"]

        try:
            discovered_jobs = self.orchestrator.run_all(keywords=keywords, locations=locations)
        except Exception as e:
            err_msg = f"Error during job discovery: {e}"
            logger.error(err_msg)
            errors.append(err_msg)
            discovered_jobs = []

        # Step 2 & 3: Ingest, Deduplicate, and Calculate AI Match Scores
        for job_data in discovered_jobs:
            try:
                # Insert or detect duplicate
                job_id, is_duplicate = self.repo.insert_job(job_data)
                
                if is_duplicate:
                    logger.debug(f"Skipping duplicate job: {job_data['title']} at {job_data['company_name']}")
                    continue

                new_jobs_count += 1

                # Calculate AI Match Score
                eval_result = self.matcher.evaluate(job_data)
                score = eval_result["match_score"]
                breakdown = eval_result["match_breakdown"]
                status = eval_result["status"]

                self.repo.update_job_match(
                    job_id=job_id,
                    match_score=score,
                    match_breakdown=breakdown,
                    status=status
                )

                # Step 4 & 5: If score >= 70%, prepare truthful application payload
                if score >= MIN_MATCH_SCORE:
                    matched_jobs_count += 1
                    job_data["id"] = job_id
                    payload = self.payload_builder.generate_payload(job_data)

                    app_id, is_new_app = self.repo.create_or_get_application(
                        candidate_id=self.candidate_id,
                        job_id=job_id,
                        resume_id=self.resume_id,
                        autofill_payload=payload,
                        status="PENDING_APPROVAL"
                    )

                    if is_new_app:
                        prepared_apps_count += 1
                        logger.info(
                            f"Prepared application #{app_id} for {job_data['company_name']} - "
                            f"{job_data['title']} (Score: {score}%) [Awaiting User Approval]"
                        )

            except Exception as e:
                err_msg = f"Error processing job '{job_data.get('title')}': {e}"
                logger.error(err_msg)
                errors.append(err_msg)

        # Step 6: Query top opportunities for reporting
        best_jobs = self.repo.get_jobs(min_score=MIN_MATCH_SCORE, limit=10)
        pending_approvals = len(self.repo.get_applications(status="PENDING_APPROVAL"))
        submitted_apps = len(self.repo.get_applications(status="SUBMITTED"))

        # Step 7: Generate and save daily report
        report_data = {
            "report_date": date.today().isoformat(),
            "total_discovered": new_jobs_count,
            "total_matched": matched_jobs_count,
            "total_prepared": prepared_apps_count,
            "total_submitted": submitted_apps,
            "pending_approvals": pending_approvals,
            "best_opportunities": best_jobs,
            "errors": errors
        }

        # Generate markdown summary
        report_md = DailyReporter.generate_markdown_report(report_data)
        report_data["summary_markdown"] = report_md
        self.repo.save_daily_report(report_data)
        DailyReporter.save_report(report_data)

        # Step 8: Notify Candidate
        logger.info("\n" + "=" * 60)
        logger.info(f"DAILY PIPELINE COMPLETED")
        logger.info(f"Discovered: {new_jobs_count} | Matched (≥70%): {matched_jobs_count} | Prepared: {prepared_apps_count}")
        logger.info(f"Pending Approvals: {pending_approvals} (Review via Streamlit at http://localhost:8501)")
        logger.info("=" * 60)

        return report_data


def start_scheduler():
    """Start APScheduler daemon configured for 9:00 AM IST daily."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BlockingScheduler()
    pipeline = DailyJobPipeline()

    trigger = CronTrigger(
        hour=SCHEDULER_HOUR,
        minute=SCHEDULER_MINUTE,
        timezone=SCHEDULER_TIMEZONE
    )

    scheduler.add_job(
        pipeline.run,
        trigger=trigger,
        id="daily_job_search_pipeline",
        name="Daily 9:00 AM IST Job Search & Application Preparation",
        replace_existing=True
    )

    logger.info(
        f"APScheduler scheduled to run daily at {SCHEDULER_HOUR:02d}:{SCHEDULER_MINUTE:02d} "
        f"Timezone: {SCHEDULER_TIMEZONE}."
    )
    logger.info("Scheduler started. Press Ctrl+C to terminate.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler terminated by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Job Application Automation Agent")
    parser.add_argument("--run-now", action="store_true", help="Execute daily pipeline immediately")
    parser.add_argument("--schedule", action="store_true", help="Run APScheduler daemon for 9:00 AM IST")

    args = parser.parse_args()

    if args.run_now or not args.schedule:
        pipeline = DailyJobPipeline()
        pipeline.run()
    else:
        start_scheduler()
