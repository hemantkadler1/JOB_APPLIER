"""
Unit tests for AI Job Matcher.
"""

import pytest
from matching.matcher import JobMatcher
from config.candidate_profile import CANDIDATE_PROFILE
from config.settings import MIN_MATCH_SCORE

@pytest.fixture
def matcher():
    return JobMatcher(CANDIDATE_PROFILE)

def test_high_match_job(matcher):
    """A role matching Java, Spring Boot, React with < 1 year experience in Bengaluru must score >= 70%."""
    job = {
        "title": "Associate Software Engineer - Java & Spring Boot",
        "company_name": "Razorpay",
        "location": "Bengaluru",
        "is_remote": False,
        "min_experience_years": 0.0,
        "max_experience_years": 1.0,
        "salary_raw": "₹7-9 LPA",
        "min_salary_lpa": 7.0,
        "max_salary_lpa": 9.0,
        "required_skills": ["Java", "Spring Boot", "MySQL", "REST APIs", "Docker"],
        "description": "Looking for an Associate Software Engineer to build scalable microservices and REST APIs in Java and Spring Boot. Experience with MySQL and Docker."
    }

    result = matcher.evaluate(job)
    score = result["match_score"]
    status = result["status"]

    assert score >= MIN_MATCH_SCORE, f"Expected score >= {MIN_MATCH_SCORE}, got {score}"
    assert status == "MATCHED"
    assert result["match_breakdown"]["is_eligible"] is True
    assert "Java" in result["match_breakdown"]["matched_skills"]

def test_senior_or_irrelevant_job(matcher):
    """A 10+ year Senior Lead / ML Architect role must be rejected (< 70%)."""
    job = {
        "title": "Principal Architect - Python & Machine Learning",
        "company_name": "Legacy Corp",
        "location": "Mumbai",
        "is_remote": False,
        "min_experience_years": 10.0,
        "max_experience_years": 15.0,
        "salary_raw": "₹50 LPA",
        "min_salary_lpa": 50.0,
        "max_salary_lpa": 60.0,
        "required_skills": ["Python", "PyTorch", "Deep Learning", "Kubernetes"],
        "description": "Senior leadership position requiring 10+ years directing machine learning strategy."
    }

    result = matcher.evaluate(job)
    score = result["match_score"]
    status = result["status"]

    assert score < MIN_MATCH_SCORE, f"Expected score < {MIN_MATCH_SCORE}, got {score}"
    assert status == "REJECTED_LOW_SCORE"
    assert result["match_breakdown"]["is_eligible"] is False
