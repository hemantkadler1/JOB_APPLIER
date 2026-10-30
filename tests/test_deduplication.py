"""
Unit tests for Job Deduplication and String Canonicalization.
"""

from matching.deduplicator import JobDeduplicator

def test_company_normalization():
    norm1 = JobDeduplicator.normalize_company("Google India Private Limited")
    norm2 = JobDeduplicator.normalize_company("Google LLC")
    assert norm1 == "google india" or "google" in norm1
    assert "google" in norm2

def test_title_normalization():
    norm1 = JobDeduplicator.normalize_title("[URGENT HIRING] Java Developer - Immediate Opening")
    norm2 = JobDeduplicator.normalize_title("Java Developer")
    assert norm1 == "java developer"
    assert norm2 == "java developer"

def test_duplicate_hash_consistency():
    hash1 = JobDeduplicator.compute_hash(
        title="Associate Software Engineer",
        company="Razorpay Technologies Pvt Ltd",
        location="Bengaluru, Karnataka"
    )
    hash2 = JobDeduplicator.compute_hash(
        title="[Hiring] Associate Software Engineer",
        company="Razorpay",
        location="Bengaluru"
    )
    assert hash1 == hash2, "Expected matching canonical hash for identical postings with formatting variations."

