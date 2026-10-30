"""
Unit tests for truthful Autofill Payload Generator.
Verifies strictly that no qualifications or experience are fabricated.
"""

from application.autofill_payload import AutofillPayloadBuilder
from config.candidate_profile import CANDIDATE_PROFILE

def test_autofill_payload_truthfulness():
    builder = AutofillPayloadBuilder(CANDIDATE_PROFILE)
    job = {
        "id": 99,
        "title": "Backend Java Developer",
        "company_name": "Acme Inc"
    }

    payload = builder.generate_payload(job)

    # Truth checks
    assert payload["full_name"] == "Hemant Manjunath Kadler"
    assert payload["email"] == "hemantkadler@gmail.com"
    assert payload["phone"] == "+91 9449447654"
    assert payload["current_company"] == "Skyllx Technologies Private Limited"
    assert payload["current_job_title"] == "Associate Software Engineer"
    assert payload["total_experience_years"] < 1.0  # Must reflect under 1 year
    assert "8.58" in payload["cgpa_or_percentage"]
    assert "Vidyavardhaka" in payload["institution"]
    assert payload["truthfulness_verified"] is True
    assert "HealthMatrix360" in payload["cover_letter"]

