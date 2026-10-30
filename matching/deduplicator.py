"""
Job deduplication and normalization engine.
Prevents duplicate applications across different platforms and reposted listings.
"""

import hashlib
import re
from typing import Dict, Any

class JobDeduplicator:
    """Computes canonical fingerprint for job postings."""

    @staticmethod
    def normalize_company(company: str) -> str:
        """Strip legal suffixes and special characters from company name."""
        if not company:
            return "unknown"
        comp = company.lower().strip()
        # Remove common corporate suffixes
        comp = re.sub(r"\b(pvt|ltd|limited|inc|incorporated|technologies|solutions|corp|corporation|llc|services)\b\.?", "", comp)
        comp = re.sub(r"[^\w\s]", "", comp)
        return " ".join(comp.split())

    @staticmethod
    def normalize_title(title: str) -> str:
        """Standardize job title, removing urgency banners and locations."""
        if not title:
            return "unknown"
        t = title.lower().strip()
        # Remove common recruitment tags
        t = re.sub(r"\[.*?\]|\(.*?\)", "", t)
        t = re.sub(r"\b(urgent|immediate|hiring|walk-in|fresher|opening|wanted)\b", "", t)
        t = re.sub(r"[^\w\s]", "", t)
        return " ".join(t.split())

    @staticmethod
    def normalize_location(location: str, is_remote: bool = False) -> str:
        """Map locations to canonical regions."""
        if is_remote or not location:
            return "remote"
        loc = location.lower()
        if "bengaluru" in loc or "bangalore" in loc:
            return "bengaluru"
        elif "mysore" in loc:
            return "mysore"
        elif "remote" in loc or "work from home" in loc:
            return "remote"
        elif "hyderabad" in loc:
            return "hyderabad"
        elif "pune" in loc:
            return "pune"
        elif "delhi" in loc or "noida" in loc or "gurgaon" in loc or "gurugram" in loc:
            return "ncr"
        elif "mumbai" in loc:
            return "mumbai"
        elif "chennai" in loc:
            return "chennai"
        elif "india" in loc:
            return "india"
        return "other"

    @classmethod
    def compute_hash(cls, title: str, company: str, location: str = "", is_remote: bool = False) -> str:
        """Generate SHA-256 fingerprint for deduplication."""
        norm_t = cls.normalize_title(title)
        norm_c = cls.normalize_company(company)
        norm_l = cls.normalize_location(location, is_remote)
        raw_key = f"{norm_t}::{norm_c}::{norm_l}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

