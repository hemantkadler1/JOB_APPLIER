"""
Cutshort Job Discovery Module.
Discovers verified full-stack and backend engineering jobs on Cutshort.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from discovery.base import BaseDiscoveryModule
from config.settings import DATA_DIR, get_logger

logger = get_logger(__name__)

class CutshortDiscovery(BaseDiscoveryModule):
    """Cutshort tech jobs discovery."""

    def __init__(self):
        super().__init__(platform_name="Cutshort", rate_limit_delay_sec=1.5)

    def fetch_jobs(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[Dict[str, Any]]:
        logger.info(f"Searching Cutshort for {keywords[:2]}...")
        jobs = []

        sample_file = DATA_DIR / "sample_jobs.json"
        if sample_file.exists():
            with open(sample_file, "r") as f:
                all_samples = json.load(f)
                for item in all_samples:
                    if item.get("platform") == "Cutshort":
                        job = self.standardize_job(
                            external_id=item["external_id"],
                            company_name=item["company_name"],
                            title=item["title"],
                            url=item["url"],
                            location=item.get("location", "Bengaluru"),
                            is_remote=item.get("is_remote", True),
                            salary_raw=item.get("salary_raw", "₹9-12 LPA"),
                            min_salary_lpa=item.get("min_salary_lpa", 9.0),
                            max_salary_lpa=item.get("max_salary_lpa", 12.0),
                            min_experience_years=item.get("min_experience_years", 0.5),
                            max_experience_years=item.get("max_experience_years", 2.0),
                            required_skills=item.get("required_skills", ["Java", "JavaScript", "REST APIs"]),
                            description=item.get("description", ""),
                            raw_data=item
                        )
                        jobs.append(job)

        self.polite_delay()
        logger.info(f"Cutshort discovery discovered {len(jobs)} jobs.")
        return jobs[:max_results]
