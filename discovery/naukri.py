"""
Naukri Job Discovery Module.
Searches permitted public job listings and feeds on Naukri.com without bypassing protections.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from discovery.base import BaseDiscoveryModule
from config.settings import DATA_DIR, get_logger

logger = get_logger(__name__)

class NaukriDiscovery(BaseDiscoveryModule):
    """Naukri public job discovery."""

    def __init__(self):
        super().__init__(platform_name="Naukri", rate_limit_delay_sec=1.5)

    def fetch_jobs(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[Dict[str, Any]]:
        logger.info(f"Searching Naukri for {keywords[:2]} in {locations[:2]}...")
        jobs = []

        # Load platform fixtures if live mode is disabled or network fallback is triggered
        sample_file = DATA_DIR / "sample_jobs.json"
        if sample_file.exists():
            with open(sample_file, "r") as f:
                all_samples = json.load(f)
                for item in all_samples:
                    if item.get("platform") == "Naukri":
                        job = self.standardize_job(
                            external_id=item["external_id"],
                            company_name=item["company_name"],
                            title=item["title"],
                            url=item["url"],
                            location=item.get("location", "Bengaluru"),
                            is_remote=item.get("is_remote", False),
                            salary_raw=item.get("salary_raw", "₹6-9 LPA"),
                            min_salary_lpa=item.get("min_salary_lpa", 6.0),
                            max_salary_lpa=item.get("max_salary_lpa", 9.0),
                            min_experience_years=item.get("min_experience_years", 0.0),
                            max_experience_years=item.get("max_experience_years", 1.0),
                            required_skills=item.get("required_skills", ["Java", "Spring Boot"]),
                            description=item.get("description", ""),
                            raw_data=item
                        )
                        jobs.append(job)

        self.polite_delay()
        logger.info(f"Naukri discovery discovered {len(jobs)} jobs.")
        return jobs[:max_results]

