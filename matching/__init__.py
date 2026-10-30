"""Matching package."""
from matching.resume_parser import ResumeParser
from matching.deduplicator import JobDeduplicator
from matching.matcher import JobMatcher

__all__ = ["ResumeParser", "JobDeduplicator", "JobMatcher"]

