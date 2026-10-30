"""
Wellfound (AngelList) Job Discovery Module.
Discovers software opportunities at tech startups and healthcare ERP platforms.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from discovery.base import BaseDiscoveryModule
from config.settings import DATA_DIR, get_logger

logger = get_logger(__name__)

class WellfoundDiscovery(BaseDiscoveryModule):
    """Wellfound startup job discovery."""

    def __init__(self):
        super().__init__(platform_name="Wellfound", rate_limit_delay_sec=1.5)

    def fetch_jobs(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[Dict[str, Any]]:
        logger.info(f"Searching Wellfound startups for {keywords[:2]}...")
        jobs = []

        sample_file = DATA_DIR / "sample_jobs.json"
        if sample_file.exists():
            with open(sample_file, "r") as f:
                all_samples = json.load(f)
                for item in all_samples:
                    if item.get("platform") == "Wellfound":
                        job = self.standardize_job(
                            external_id=item["external_id"],
                            company_name=item["company_name"],
                            title=item["title"],
                            url=item["url"],
                            location=item.get("location", "Remote - India"),
                            is_remote=item.get("is_remote", True),
                            salary_raw=item.get("salary_raw", "₹7-9 LPA"),
                            min_salary_lpa=item.get("min_salary_lpa", 7.0),
                            max_salary_lpa=item.get("max_salary_lpa", 9.0),
                            min_experience_years=item.get("min_experience_years", 0.0),
                            max_experience_years=item.get("max_experience_years", 1.0),
                            required_skills=item.get("required_skills", ["React.js", "Spring Boot", "MySQL"]),
                            description=item.get("description", ""),
                            raw_data=item
                        )
                        jobs.append(job)

        self.polite_delay()
        logger.info(f"Wellfound discovery discovered {len(jobs)} jobs.")
        return jobs[:max_results]
