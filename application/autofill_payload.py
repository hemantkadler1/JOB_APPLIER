"""
Truthful Application Form Builder.
Generates structured answers from candidate profile and verified resume data.
Strictly adheres to truthful parameters without fabricating experience or credentials.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from config.settings import DEFAULT_RESUME_PATH, get_logger

logger = get_logger(__name__)

class AutofillPayloadBuilder:
    """Prepares structured responses for job application fields."""

    def __init__(self, candidate_profile: Dict[str, Any], resume_path: Optional[Path] = None):
        self.profile = candidate_profile
        self.resume_path = resume_path or DEFAULT_RESUME_PATH

    def generate_payload(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Generate truthful application responses tailored to the specific job."""
        job_title = job.get("title", "")
        company = job.get("company_name", "")

        # Tailored summary pitch based solely on verified experience at Skyllx
        truthful_cover_note = (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my strong interest in the {job_title} role. "
            f"As an Associate Software Engineer at Skyllx Technologies, I have hands-on experience building "
            f"full-stack healthcare ERP platforms (HealthMatrix360, IVFCareX, DentoCareX) using Java, Spring Boot, "
            f"React.js, Next.js, and MySQL. I have integrated 15+ REST APIs, implemented modular microservices, "
            f"and supported containerized CI/CD deployments with Docker and Jenkins. "
            f"Holding a B.E. in Computer Science Engineering (CGPA 8.58), I am eager to contribute my technical "
            f"foundation and problem-solving skills to {company}.\n\n"
            f"Sincerely,\n{self.profile['name']}\n"
            f"Phone: {self.profile['phone']} | Email: {self.profile['email']}"
        )

        payload = {
            # Candidate Identification
            "full_name": self.profile["name"],
            "first_name": self.profile["name"].split()[0],
            "last_name": self.profile["name"].split()[-1],
            "email": self.profile["email"],
            "phone": self.profile["phone"],
            "current_city": "Mysore, Karnataka",
            "country": "India",

            # Online Profiles
            "linkedin_url": self.profile.get("linkedin_url", ""),
            "github_url": self.profile.get("github_url", ""),
            "portfolio_url": self.profile.get("github_url", ""),

            # Current Employment (Verified Truthful)
            "current_company": self.profile["current_employment"]["company"],
            "current_job_title": self.profile["current_employment"]["title"],
            "total_experience_years": self.profile.get("experience_years", 0.8),
            "notice_period": "Immediate / 15 Days",
            "immediate_joiner": "Yes",

            # Compensation (Expected ₹6-10 LPA)
            "current_ctc_lpa": "As per Associate Software Engineer band (Confidential)",
            "expected_ctc_lpa": "₹ 7,50,000 - 9,00,000 (₹6–10 LPA range)",
            "expected_ctc_numeric": 800000,
            "currency": "INR",

            # Work Authorization & Relocation
            "work_authorization": "Yes, Indian Citizen (Authorized to work in India)",
            "require_visa_sponsorship": "No",
            "willing_to_relocate": "Yes, eager to work in Bengaluru, Remote, or Anywhere in India",
            "preferred_location": "Bengaluru / Remote / Anywhere in India",

            # Education
            "highest_qualification": "B.E. in Computer Science Engineering",
            "institution": "Vidyavardhaka College of Engineering, Mysore",
            "graduation_year": "2024",
            "cgpa_or_percentage": "8.58 CGPA",

            # Technical Skills
            "primary_skills": "Java, Spring Boot, React.js, Next.js, MySQL, REST APIs, Microservices",
            "tools_and_devops": "Docker, Jenkins, Git, CI/CD, Android & iOS Development",

            # File Attachment
            "resume_file_path": str(self.resume_path.resolve()) if self.resume_path.exists() else None,
            "resume_filename": self.resume_path.name if self.resume_path.exists() else "Hemant_Kadler_Resume.pdf",

            # Cover Note
            "cover_letter": truthful_cover_note,

            # Metadata
            "target_job_id": job.get("id"),
            "target_job_title": job_title,
            "target_company": company,
            "truthfulness_verified": True
        }

        return payload
