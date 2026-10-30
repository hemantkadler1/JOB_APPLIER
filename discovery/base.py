"""
Base discovery module interface for all job search platforms.
Provides standard HTTP handling, polite rate-limiting, error recovery,
and standardized job schema mapping.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import requests
from config.settings import get_logger, MAX_JOBS_PER_PLATFORM
from matching.deduplicator import JobDeduplicator

logger = get_logger(__name__)

class BaseDiscoveryModule(ABC):
    """Abstract base class for job discovery plugins."""

    def __init__(self, platform_name: str, rate_limit_delay_sec: float = 1.0):
        self.platform_name = platform_name
        self.rate_limit_delay_sec = rate_limit_delay_sec
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def polite_delay(self) -> None:
        """Enforce polite crawling delay to avoid overloading endpoints."""
        if self.rate_limit_delay_sec > 0:
            time.sleep(self.rate_limit_delay_sec)

    def standardize_job(
        self,
        external_id: str,
        company_name: str,
        title: str,
        url: str,
        location: str = "Bengaluru, India",
        is_remote: bool = False,
        salary_raw: str = "Not Disclosed",
        min_salary_lpa: Optional[float] = None,
        max_salary_lpa: Optional[float] = None,
        min_experience_years: float = 0.0,
        max_experience_years: float = 1.0,
        required_skills: Optional[List[str]] = None,
        description: str = "",
        raw_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert any raw job payload into canonical schema."""
        dup_hash = JobDeduplicator.compute_hash(
            title=title,
            company=company_name,
            location=location,
            is_remote=is_remote
        )

        return {
            "external_job_id": external_id,
            "platform": self.platform_name,
            "company_name": company_name.strip(),
            "title": title.strip(),
            "url": url.strip(),
            "location": location.strip(),
            "is_remote": 1 if is_remote else 0,
            "salary_raw": salary_raw.strip(),
            "min_salary_lpa": min_salary_lpa,
            "max_salary_lpa": max_salary_lpa,
            "min_experience_years": min_experience_years,
            "max_experience_years": max_experience_years,
            "required_skills": required_skills or [],
            "description": description.strip(),
            "duplicate_hash": dup_hash,
            "raw_data": raw_data or {}
        }

    @abstractmethod
    def fetch_jobs(self, keywords: List[str], locations: List[str], max_results: int = MAX_JOBS_PER_PLATFORM) -> List[Dict[str, Any]]:
        """Fetch jobs matching criteria from the platform."""
        pass
