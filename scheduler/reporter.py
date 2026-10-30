"""
Daily Report Generator.
Generates comprehensive Markdown summaries and analytical metrics for the candidate.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Any, List
from config.settings import REPORTS_DIR, get_logger

logger = get_logger(__name__)

class DailyReporter:
    """Formats and writes daily job search reports."""

    @staticmethod
    def generate_markdown_report(report_data: Dict[str, Any]) -> str:
        """Create clean GitHub-style Markdown report."""
        report_date = report_data.get("report_date", date.today().isoformat())
        total_discovered = report_data.get("total_discovered", 0)
        total_matched = report_data.get("total_matched", 0)
        total_prepared = report_data.get("total_prepared", 0)
        total_submitted = report_data.get("total_submitted", 0)
        pending_approvals = report_data.get("pending_approvals", 0)
        best_opps: List[Dict[str, Any]] = report_data.get("best_opportunities", [])
        errors: List[str] = report_data.get("errors", [])

        md = []
        md.append(f"# 📊 Daily Job Application Report — {report_date}")
        md.append("")
        md.append(f"**Candidate:** Hemant Manjunath Kadler  ")
        md.append(f"**Target Roles:** Java Developer | Spring Boot | React | Full Stack | Associate Software Engineer  ")
        md.append(f"**Generated At:** 9:00 AM IST  ")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 📈 Today's Pipeline Metrics")
        md.append("")
        md.append("| Metric | Count | Description |")
        md.append("| :--- | :--- | :--- |")
        md.append(f"| 🔍 **New Jobs Discovered** | `{total_discovered}` | Scanned across all 7 discovery channels |")
        md.append(f"| 🎯 **Matching Profile (≥70%)** | `{total_matched}` | Passed AI technical and experience matching |")
        md.append(f"| 📝 **Applications Prepared** | `{total_prepared}` | Truthful autofill responses generated |")
        md.append(f"| ⏳ **Pending Your Approval** | `{pending_approvals}` | Ready for review in Streamlit Dashboard |")
        md.append(f"| 🚀 **Applications Submitted** | `{total_submitted}` | Officially confirmed submissions |")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 🌟 Top 10 Opportunities for Review")
        md.append("")

        if not best_opps:
            md.append("> *No matching opportunities scored ≥70% today. Check back tomorrow.*")
        else:
            for i, opp in enumerate(best_opps[:10], 1):
                score = opp.get("match_score", 0)
                title = opp.get("title", "")
                company = opp.get("company_name", "")
                platform = opp.get("platform", "")
                location = opp.get("location", "India")
                salary = opp.get("salary_raw", "Not Disclosed")
                url = opp.get("url", "#")
                skills = ", ".join(opp.get("required_skills", [])[:5]) or "Tech Stack Aligned"

                md.append(f"### {i}. [{title}]({url})")
                md.append(f"- **Company:** {company} (`{platform}`)")
                md.append(f"- **Match Score:** `{score}%` 🎯")
                md.append(f"- **Location:** {location} | **Salary:** {salary}")
                md.append(f"- **Key Skills:** {skills}")
                md.append(f"- **Action:** [Review & Approve in Dashboard](http://localhost:8501)")
                md.append("")

        if errors:
            md.append("---")
            md.append("## ⚠️ Warnings & Tasks Requiring Attention")
            for err in errors:
                md.append(f"- {err}")
            md.append("")

        md.append("---")
        md.append("*AI Daily Job Application Automation System — Powered by Python & Streamlit*")
        return "\n".join(md)

    @classmethod
    def save_report(cls, report_data: Dict[str, Any]) -> Path:
        """Write report to reports directory."""
        report_date = report_data.get("report_date", date.today().isoformat())
        markdown_content = cls.generate_markdown_report(report_data)
        report_path = REPORTS_DIR / f"daily_report_{report_date}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"Daily report saved to {report_path}")
        return report_path

