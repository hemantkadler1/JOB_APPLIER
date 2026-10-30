"""
Resume parsing module using PyPDF.
Extracts raw text, structured sections, and skills from candidate PDF resume.
"""

import hashlib
import re
from pathlib import Path
from typing import Dict, Any, List
import pypdf
from config.settings import get_logger

logger = get_logger(__name__)

# Common tech skills lexicon for extraction & normalization
KNOWN_SKILLS = [
    "java", "spring boot", "spring", "react.js", "react", "next.js", "nextjs",
    "javascript", "typescript", "rest apis", "rest api", "rest", "microservices",
    "microservices architecture", "mysql", "sql", "docker", "docker desktop",
    "jenkins", "ci/cd", "ci / cd", "android", "ios", "html", "css", "git", "github",
    "python", "junit", "hibernate", "jpa", "aws", "gcp", "google cloud", "linux"
]

class ResumeParser:
    """Parses PDF resumes into structured data."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = Path(pdf_path)

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of PDF file."""
        hasher = hashlib.sha256()
        with open(self.pdf_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def extract_text(self) -> str:
        """Extract full plain text from PDF pages."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Resume file not found at {self.pdf_path}")

        reader = pypdf.PdfReader(str(self.pdf_path))
        text_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_pages.append(page_text)
        
        full_text = "\n".join(text_pages).strip()
        logger.info(f"Extracted {len(full_text)} characters from {self.pdf_path.name}")
        return full_text

    def extract_skills(self, text: str) -> List[str]:
        """Detect technical skills present in resume text."""
        lowered = text.lower()
        found_skills = set()
        for skill in KNOWN_SKILLS:
            # Word boundary check or literal match
            pattern = r"(?:\b|_)" + re.escape(skill) + r"(?:\b|_)"
            if re.search(pattern, lowered):
                # Standardize display names
                if skill in ("react", "react.js"):
                    found_skills.add("React.js")
                elif skill in ("nextjs", "next.js"):
                    found_skills.add("Next.js")
                elif skill in ("spring", "spring boot"):
                    found_skills.add("Spring Boot")
                elif skill in ("rest", "rest api", "rest apis"):
                    found_skills.add("REST APIs")
                elif skill in ("microservices", "microservices architecture"):
                    found_skills.add("Microservices")
                elif skill in ("docker", "docker desktop"):
                    found_skills.add("Docker")
                elif skill in ("ci/cd", "ci / cd"):
                    found_skills.add("CI/CD")
                else:
                    found_skills.add(skill.capitalize())

        return sorted(list(found_skills))

    def parse(self) -> Dict[str, Any]:
        """Run full extraction pipeline."""
        raw_text = self.extract_text()
        file_hash = self.compute_hash()
        skills = self.extract_skills(raw_text)

        # Extract email and phone if possible
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
        phone_match = re.search(r"(\+91[\s\-]?)?[6-9]\d{9}", raw_text)

        return {
            "filename": self.pdf_path.name,
            "file_path": str(self.pdf_path.resolve()),
            "file_hash": file_hash,
            "parsed_text": raw_text,
            "skills_extracted": skills,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None
        }

