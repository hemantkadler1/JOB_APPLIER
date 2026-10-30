"""
AI Job Matching Engine.
Evaluates candidate resume against job postings with multi-criteria weighted scoring:
- Skills Match (40%)
- Title / Role Match (25%)
- Experience Match (20%)
- Location Match (10%)
- Salary Match (5%)
Filters out jobs scoring below MIN_MATCH_SCORE (70%).
"""

import re
from typing import Dict, Any, List, Tuple
from config.settings import MIN_MATCH_SCORE, get_logger

logger = get_logger(__name__)

class JobMatcher:
    """Calculates match score between candidate profile and a job listing."""

    def __init__(self, candidate_profile: Dict[str, Any]):
        self.profile = candidate_profile
        self.target_roles = [r.lower() for r in candidate_profile.get("target_roles", [])]
        self.candidate_skills = {s.lower(): s for s in candidate_profile.get("skills", [])}
        self.cand_exp = candidate_profile.get("experience_years", 0.8)
        self.min_salary = candidate_profile.get("min_salary_lpa", 6.0)
        self.max_salary = candidate_profile.get("max_salary_lpa", 10.0)
        self.preferred_locations = [loc.lower() for loc in candidate_profile.get("preferred_locations", [])]

    def calculate_title_score(self, job_title: str) -> float:
        """Score title alignment with target roles (0 - 100)."""
        if not job_title:
            return 20.0
        jt = job_title.lower()

        # Direct target role match
        for role in self.target_roles:
            if role in jt:
                return 100.0

        # Partial keyword matches
        score = 0.0
        if "java" in jt:
            score += 35.0
        if "spring" in jt or "springboot" in jt:
            score += 25.0
        if "react" in jt or "frontend" in jt or "front-end" in jt:
            score += 25.0
        if "backend" in jt or "back-end" in jt:
            score += 30.0
        if "full stack" in jt or "fullstack" in jt:
            score += 35.0
        if "software engineer" in jt or "software developer" in jt or "sde" in jt:
            score += 30.0
        if "associate" in jt or "junior" in jt or "trainee" in jt or "entry" in jt:
            score += 15.0

        # Penalties for unrelated or senior roles
        if any(term in jt for term in ["lead", "principal", "architect", "manager", "director", "vp", "head"]):
            score = max(5.0, score - 50.0)
        if any(term in jt for term in ["qa", "testing", "devops engineer", "data scientist", "sales", "hr", "content"]):
            score = min(score, 25.0)

        return min(100.0, max(0.0, score))

    def calculate_skills_score(self, job_skills: List[str], description: str) -> Tuple[float, List[str], List[str]]:
        """Score technical skills match against candidate skill set."""
        job_text = description.lower()
        extracted_job_skills = set(s.lower() for s in job_skills)

        # Detect skills from description text as well
        for s_low in self.candidate_skills:
            pattern = r"(?:\b|_)" + re.escape(s_low) + r"(?:\b|_)"
            if re.search(pattern, job_text):
                extracted_job_skills.add(s_low)

        if not extracted_job_skills:
            # Check for general tech terms
            tech_hits = 0
            for s_low in ["java", "spring", "react", "javascript", "sql", "api"]:
                if s_low in job_text:
                    tech_hits += 1
            score = min(100.0, tech_hits * 18.0)
            return (score, ["General Software Engineering"], [])

        matched = []
        missing = []
        for s_low in extracted_job_skills:
            if s_low in self.candidate_skills:
                matched.append(self.candidate_skills[s_low])
            else:
                missing.append(s_low.title())

        # Give extra weight if core competencies (Java, Spring Boot, React) match
        core_boost = 0.0
        matched_str = " ".join(matched).lower()
        if "java" in matched_str:
            core_boost += 15.0
        if "spring" in matched_str:
            core_boost += 15.0
        if "react" in matched_str:
            core_boost += 10.0
        if "rest" in matched_str or "api" in matched_str:
            core_boost += 5.0
        if "microservices" in matched_str:
            core_boost += 5.0

        ratio = len(matched) / max(1, len(extracted_job_skills))
        base_score = ratio * 70.0
        total_score = min(100.0, base_score + core_boost)

        return (total_score, sorted(matched), sorted(missing[:6]))

    def calculate_experience_score(self, min_exp: float, max_exp: float, description: str) -> float:
        """
        Score experience level.
        Hemant has under 1 year of experience (Associate Software Engineer).
        """
        # Look for explicit years in description if not provided in metadata
        desc_lower = description.lower()
        if min_exp == 0.0 and max_exp == 1.0:
            exp_match = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?|yrs)", desc_lower)
            if exp_match:
                min_exp = float(exp_match.group(1))
                max_exp = float(exp_match.group(2))
            else:
                single_exp = re.search(r"(\d+)\+?\s*(?:years?|yrs)", desc_lower)
                if single_exp:
                    min_exp = float(single_exp.group(1))
                    max_exp = min_exp + 2.0

        # Fresher / Entry / Associate indicator
        if any(w in desc_lower for w in ["fresher", "entry level", "college graduate", "0-1 year", "0 to 1 year"]):
            return 100.0

        if min_exp <= 1.0:
            return 100.0
        elif min_exp <= 2.0:
            return 85.0
        elif min_exp <= 3.0:
            return 50.0
        elif min_exp <= 5.0:
            return 15.0
        else:
            # Over 5 years (Senior, Lead, Architect) - strongly penalize
            return 0.0

    def calculate_location_score(self, location: str, is_remote: bool) -> float:
        """Score location alignment (Bengaluru, Remote, India)."""
        if is_remote:
            return 100.0

        if not location:
            return 80.0  # Assumed default India

        loc = location.lower()
        if any(p in loc for p in ["bengaluru", "bangalore"]):
            return 100.0
        if any(p in loc for p in ["remote", "work from home", "wfh", "anywhere in india", "pan india"]):
            return 100.0
        if "mysore" in loc:
            return 100.0
        if any(p in loc for p in ["hyderabad", "pune", "delhi", "noida", "gurgaon", "mumbai", "chennai", "india"]):
            return 85.0

        # Check for non-India location
        foreign_locations = ["usa", "united states", "london", "uk", "singapore", "germany", "dubai", "canada"]
        if any(f in loc for f in foreign_locations):
            return 10.0

        return 75.0

    def calculate_salary_score(self, min_sal: float, max_sal: float, salary_raw: str) -> float:
        """Score salary alignment (Target: ₹6-10 LPA)."""
        if not salary_raw or salary_raw.lower() in ("not disclosed", "competitive", "best in industry", "as per market"):
            return 85.0  # Standard neutral

        # If range is within or overlaps candidate's target ₹6-10 LPA
        if min_sal and min_sal >= 5.0:
            if min_sal >= 6.0 and min_sal <= 12.0:
                return 100.0
            if min_sal > 12.0:
                return 75.0  # High salary, likely senior
            return 80.0

        if max_sal and max_sal < 4.0:
            return 40.0  # Very low salary (< 4 LPA)

        return 85.0

    def evaluate(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete evaluation of a job posting.
        Returns match_score (0-100), breakdown, and eligibility status.
        """
        title = job.get("title", "")
        description = job.get("description", "")
        skills = job.get("required_skills", [])
        min_exp = float(job.get("min_experience_years") or 0.0)
        max_exp = float(job.get("max_experience_years") or 1.0)
        location = job.get("location", "")
        is_remote = bool(job.get("is_remote", False))
        min_sal = float(job.get("min_salary_lpa") or 0.0)
        max_sal = float(job.get("max_salary_lpa") or 0.0)
        salary_raw = job.get("salary_raw", "")

        # Compute component scores
        title_score = self.calculate_title_score(title)
        skills_score, matched_skills, missing_skills = self.calculate_skills_score(skills, description)
        exp_score = self.calculate_experience_score(min_exp, max_exp, description)
        loc_score = self.calculate_location_score(location, is_remote)
        sal_score = self.calculate_salary_score(min_sal, max_sal, salary_raw)

        # Weighted composite score
        # Skills: 40%, Title: 25%, Experience: 20%, Location: 10%, Salary: 5%
        weighted_score = (
            (skills_score * 0.40) +
            (title_score * 0.25) +
            (exp_score * 0.20) +
            (loc_score * 0.10) +
            (sal_score * 0.05)
        )
        final_score = round(min(100.0, max(0.0, weighted_score)), 1)

        is_eligible = final_score >= MIN_MATCH_SCORE
        status = "MATCHED" if is_eligible else "REJECTED_LOW_SCORE"

        # Summary bullets for user explanation
        reasons = []
        if title_score >= 80:
            reasons.append(f"Strong role match with target '{title}'")
        if skills_score >= 70:
            reasons.append(f"Matched core skills: {', '.join(matched_skills[:4])}")
        if exp_score >= 80:
            reasons.append("Experience requirement matches candidate profile (<1 year)")
        elif exp_score <= 30:
            reasons.append("Requires senior experience (>3-5 years)")
        if loc_score >= 90:
            reasons.append(f"Location aligns with preferences ({location or 'Remote'})")

        breakdown = {
            "final_score": final_score,
            "title_score": round(title_score, 1),
            "skills_score": round(skills_score, 1),
            "experience_score": round(exp_score, 1),
            "location_score": round(loc_score, 1),
            "salary_score": round(sal_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "is_eligible": is_eligible,
            "reasons": reasons
        }

        return {
            "match_score": final_score,
            "match_breakdown": breakdown,
            "status": status
        }
