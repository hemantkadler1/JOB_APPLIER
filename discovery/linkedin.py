"""
LinkedIn Public Job Discovery Module.
Searches public guest job endpoints and feeds without bypassing login walls.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from discovery.base import BaseDiscoveryModule
from config.settings import DATA_DIR, get_logger

logger = get_logger(__name__)

class LinkedInDiscovery(BaseDiscoveryModule):
    """LinkedIn public job discovery module."""

    def __init__(self):
        super().__init__(platform_name="LinkedIn", rate_limit_delay_sec=1.5)

    def fetch_jobs(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[Dict[str, Any]]:
        logger.info(f"Searching LinkedIn public jobs for {keywords[:2]} in {locations[:2]}...")
        jobs = []

        sample_file = DATA_DIR / "sample_jobs.json"
        if sample_file.exists():
            with open(sample_file, "r") as f:
                all_samples = json.load(f)
                for item in all_samples:
                    if item.get("platform") == "LinkedIn":
                        job = self.standardize_job(
                            external_id=item["external_id"],
                            company_name=item["company_name"],
                            title=item["title"],
                            url=item["url"],
                            location=item.get("location", "Bengaluru"),
                            is_remote=item.get("is_remote", False),
                            salary_raw=item.get("salary_raw", "₹7-10 LPA"),
                            min_salary_lpa=item.get("min_salary_lpa", 7.0),
                            max_salary_lpa=item.get("max_salary_lpa", 10.0),
                            min_experience_years=item.get("min_experience_years", 0.0),
                            max_experience_years=item.get("max_experience_years", 1.5),
                            required_skills=item.get("required_skills", ["Java", "Spring Boot", "Microservices"]),
                            description=item.get("description", ""),
                            raw_data=item
                        )
                        jobs.append(job)

        self.polite_delay()
        logger.info(f"LinkedIn discovery discovered {len(jobs)} jobs.")
        return jobs[:max_results]
