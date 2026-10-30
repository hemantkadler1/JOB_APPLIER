"""
Streamlit Web Dashboard for AI Daily Job Application Automation System.
Provides interactive KPIs, Approval Queue, Discovery Explorer,
Application Tracker, Profile Sandbox, and Daily Reports.
"""

import os
import sys
from pathlib import Path
from datetime import date
import streamlit as st
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.models import init_db
from database.repository import JobRepository
from scheduler.daily_job import DailyJobPipeline
from application.playwright_agent import PlaywrightApplicationAgent
from matching.matcher import JobMatcher
from config.candidate_profile import CANDIDATE_PROFILE
from config.settings import DEFAULT_RESUME_PATH, MIN_MATCH_SCORE

# Page configuration
st.set_page_config(
    page_title="AI Job Agent | Hemant Kadler",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-approved {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-pending {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-score {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()
repo = JobRepository()

# Sidebar: Candidate Profile & Controls
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    st.title("Hemant Kadler")
    st.caption("Associate Software Engineer (<1 yr exp)")
    
    st.markdown("---")
    st.markdown("**🎯 Target Roles:**\nJava Developer, Spring Boot, React.js, Full Stack, Software Engineer")
    st.markdown("**📍 Locations:**\nBengaluru, Remote - India, Anywhere in India")
    st.markdown("**💰 Target CTC:**\n₹6.0 – 10.0 LPA")
    st.markdown("**🛠️ Key Skills:**\nJava, Spring Boot, React, Next.js, REST APIs, Microservices, MySQL, Docker, Jenkins")

    st.markdown("---")
    st.markdown("### ⚙️ Automation Control")
    st.info("🕒 Daily Scheduler: **9:00 AM IST**")
    
    if st.button("⚡ Run Daily Discovery Now", type="primary", use_container_width=True):
        with st.spinner("Executing discovery across all 7 platforms and calculating AI match scores..."):
            pipeline = DailyJobPipeline()
            result = pipeline.run()
            st.success(f"Pipeline executed! Discovered: {result['total_discovered']}, Matched: {result['total_matched']}")
            st.rerun()

    st.markdown("---")
    if DEFAULT_RESUME_PATH.exists():
        st.success(f"📄 Active Resume:\n`{DEFAULT_RESUME_PATH.name}`")
    else:
        st.warning("Resume file not found.")

# Main Header
st.markdown('<div class="main-header">💼 AI Daily Job Application Automation Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Production-grade automated discovery, AI qualification matching, and human-in-the-loop application manager.</div>', unsafe_allow_html=True)

# Fetch aggregate metrics
stats = repo.get_system_stats()

# Metric KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label="🔍 Discovered Today", value=stats["discovered_today"], delta=f"Total: {stats['total_discovered']}")
with col2:
    st.metric(label="🎯 Matching (≥70%)", value=stats["matching_jobs"], delta="Qualified")
with col3:
    st.metric(label="⏳ Pending Approval", value=stats["pending_approvals"], delta="Requires Action", delta_color="inverse")
with col4:
    st.metric(label="🚀 Submitted", value=stats["submitted"], delta="Confirmed")
with col5:
    st.metric(label="🎉 Interviews / Active", value=stats["interviews"], delta="In Progress")

st.markdown("---")

# Main Navigation Tabs
tab_approval, tab_report, tab_discovery, tab_tracker, tab_sandbox, tab_analytics = st.tabs([
    "⏳ Applications Awaiting Approval",
    "📊 Daily Report & Top 10",
    "🔍 Job Discovery Explorer",
    "📋 Application Tracker",
    "👤 Profile & Matcher Sandbox",
    "📈 Analytics & Statistics"
])

# ---------------- TAB 1: APPLICATIONS AWAITING APPROVAL ----------------
with tab_approval:
    st.subheader(f"Applications Awaiting Your Approval ({stats['pending_approvals']})")
    st.caption("Review prepared application forms. Each application is strictly truthful and uses verified resume data. Click 'Approve & Submit' to proceed.")

    pending_apps = repo.get_applications(status="PENDING_APPROVAL")

    if not pending_apps:
        st.success("🎉 You have reviewed all pending applications! No pending items right now.")
    else:
        for app in pending_apps:
            with st.container():
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:18px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="badge-score">Match Score: {app['match_score']}%</span>
                            <span class="badge-pending" style="margin-left:8px;">{app['platform']}</span>
                            <h3 style="margin-top:8px; margin-bottom:4px;">{app['job_title']}</h3>
                            <p style="color:#4B5563; margin-bottom:6px;"><strong>Company:</strong> {app['company_name']} | <strong>Location:</strong> {app['job_location']} | <strong>Salary:</strong> {app['job_salary']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("📝 View Truthful Autofill Payload & Answers"):
                    payload = app.get("autofill_payload", {})
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.text_input("Full Name", value=payload.get("full_name", ""), disabled=True, key=f"fn_{app['id']}")
                        st.text_input("Email", value=payload.get("email", ""), disabled=True, key=f"em_{app['id']}")
                        st.text_input("Phone", value=payload.get("phone", ""), disabled=True, key=f"ph_{app['id']}")
                        st.text_input("Current Company", value=payload.get("current_company", ""), disabled=True, key=f"cc_{app['id']}")
                        st.text_input("Current Role", value=payload.get("current_job_title", ""), disabled=True, key=f"cr_{app['id']}")
                        st.text_input("Total Experience", value=f"{payload.get('total_experience_years', 0.8)} Years (< 1 yr)", disabled=True, key=f"te_{app['id']}")
                    with col_p2:
                        st.text_input("Expected CTC", value=payload.get("expected_ctc_lpa", "₹6-10 LPA"), disabled=True, key=f"exp_{app['id']}")
                        st.text_input("Notice Period", value=payload.get("notice_period", "Immediate"), disabled=True, key=f"np_{app['id']}")
                        st.text_input("Work Authorization", value=payload.get("work_authorization", "Citizen of India"), disabled=True, key=f"wa_{app['id']}")
                        st.text_input("Highest Education", value=payload.get("highest_qualification", "B.E. CSE (CGPA 8.58)"), disabled=True, key=f"he_{app['id']}")
                        st.text_input("Resume File", value=payload.get("resume_filename", "Hemant_Kadler_Resume.pdf"), disabled=True, key=f"rf_{app['id']}")

                    st.text_area("Truthful Cover Note", value=payload.get("cover_letter", ""), height=150, disabled=True, key=f"cl_{app['id']}")
                    st.markdown(f"🔗 **Direct Job URL:** [{app['job_url']}]({app['job_url']})")

                # Action Buttons
                btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 4])
                with btn_col1:
                    if st.button("✅ Approve & Submit", key=f"app_{app['id']}", type="primary"):
                        with st.spinner("Executing browser automation with submission verification..."):
                            agent = PlaywrightApplicationAgent()
                            sub_res = agent.submit_application(
                                application_url=app["job_url"],
                                payload=app["autofill_payload"],
                                is_approved=True
                            )
                            repo.update_application_status(
                                application_id=app["id"],
                                status="SUBMITTED",
                                notes=sub_res.get("notes"),
                                confirmation_id=sub_res.get("confirmation_id"),
                                confirmation_url=sub_res.get("confirmation_url"),
                                screenshot_path=sub_res.get("screenshot_path")
                            )
                            st.success(f"Application approved & submitted! Receipt ID: {sub_res.get('confirmation_id')}")
                            st.rerun()

                with btn_col2:
                    if st.button("❌ Reject Application", key=f"rej_{app['id']}"):
                        repo.update_application_status(
                            application_id=app["id"],
                            status="REJECTED_BY_USER",
                            notes="Declined by candidate during approval review"
                        )
                        st.info("Application rejected.")
                        st.rerun()

# ---------------- TAB 2: DAILY REPORT & TOP 10 ----------------
with tab_report:
    st.subheader("Daily Job Search Report")
    today_str = date.today().isoformat()
    daily_rep = repo.get_daily_report(today_str)

    if daily_rep and daily_rep.get("summary_markdown"):
        st.markdown(daily_rep["summary_markdown"])
        st.download_button(
            label="📥 Download Daily Report (Markdown)",
            data=daily_rep["summary_markdown"],
            file_name=f"daily_job_report_{today_str}.md",
            mime="text/markdown"
        )
    else:
        st.info("Today's automated report has not been generated yet. Click 'Run Daily Discovery Now' in the sidebar.")

# ---------------- TAB 3: JOB DISCOVERY EXPLORER ----------------
with tab_discovery:
    st.subheader("Discovered Job Postings")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        platform_filter = st.selectbox("Filter by Platform", ["All", "Naukri", "LinkedIn", "Indeed", "Wellfound", "Instahyre", "Cutshort", "CareerPages"])
    with col_f2:
        score_filter = st.slider("Minimum Match Score", min_value=0, max_value=100, value=MIN_MATCH_SCORE)
    with col_f3:
        status_filter = st.selectbox("Status Filter", ["All", "MATCHED", "REJECTED_LOW_SCORE"])

    p_arg = None if platform_filter == "All" else platform_filter
    s_arg = None if status_filter == "All" else status_filter

    jobs = repo.get_jobs(min_score=score_filter, platform=p_arg, status=s_arg, limit=100)

    st.write(f"Showing **{len(jobs)}** job listings:")
    
    for job in jobs:
        badge_color = "#DEF7EC" if job["match_score"] >= 70 else "#FDE8E8"
        text_color = "#03543F" if job["match_score"] >= 70 else "#9B1C1C"
        
        with st.container():
            st.markdown(f"""
            <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:14px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="margin:0;">{job['title']} — <span style="color:#4B5563;">{job['company_name']}</span></h4>
                        <p style="margin:4px 0; color:#6B7280; font-size:0.9rem;">
                            📍 {job['location']} | 💰 {job['salary_raw']} | 🌐 {job['platform']} | ⏱️ Exp: {job['min_experience_years']}-{job['max_experience_years']} yrs
                        </p>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:{badge_color}; color:{text_color}; padding:6px 12px; border-radius:8px; font-weight:700; font-size:1.1rem;">
                            {job['match_score']}%
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View Details & AI Score Breakdown for {job['title']}"):
                b = job.get("match_breakdown", {})
                b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
                b_col1.metric("Skills (40%)", f"{b.get('skills_score', 0)}%")
                b_col2.metric("Title (25%)", f"{b.get('title_score', 0)}%")
                b_col3.metric("Experience (20%)", f"{b.get('experience_score', 0)}%")
                b_col4.metric("Location (10%)", f"{b.get('location_score', 0)}%")
                b_col5.metric("Salary (5%)", f"{b.get('salary_score', 0)}%")

                st.markdown("**Matched Skills:** " + (", ".join(b.get("matched_skills", [])) or "None"))
                st.markdown("**Required Skills:** " + (", ".join(job.get("required_skills", [])) or "None"))
                st.markdown(f"**Job Description:**\n{job.get('description', '')}")
                st.markdown(f"🔗 **Listing URL:** [{job['url']}]({job['url']})")

# ---------------- TAB 4: APPLICATION TRACKER ----------------
with tab_tracker:
    st.subheader("Application Tracking & History")
    all_apps = repo.get_applications()

    if not all_apps:
        st.info("No applications prepared yet.")
    else:
        # Status distribution
        status_counts = pd.Series([a["status"] for a in all_apps]).value_counts()
        st.bar_chart(status_counts)

        for a in all_apps:
            col_t1, col_t2, col_t3 = st.columns([4, 2, 2])
            with col_t1:
                st.markdown(f"**{a['job_title']}** at **{a['company_name']}** (`{a['platform']}`)")
                st.caption(f"Applied/Prepared: {a['created_at']} | Match: {a['match_score']}%")
            with col_t2:
                current_st = a["status"]
                st.markdown(f"**Status:** `{current_st}`")
                if a.get("confirmation_id"):
                    st.caption(f"Receipt: `{a['confirmation_id']}`")
            with col_t3:
                new_st = st.selectbox(
                    "Update Status",
                    ["PENDING_APPROVAL", "SUBMITTED", "UNDER_REVIEW", "INTERVIEW_SCHEDULED", "REJECTED_BY_RECRUITER", "OFFER"],
                    index=["PENDING_APPROVAL", "SUBMITTED", "UNDER_REVIEW", "INTERVIEW_SCHEDULED", "REJECTED_BY_RECRUITER", "OFFER"].index(current_st) if current_st in ["PENDING_APPROVAL", "SUBMITTED", "UNDER_REVIEW", "INTERVIEW_SCHEDULED", "REJECTED_BY_RECRUITER", "OFFER"] else 0,
                    key=f"status_sel_{a['id']}"
                )
                if new_st != current_st:
                    if st.button("Save", key=f"save_st_{a['id']}"):
                        repo.update_application_status(
                            application_id=a["id"],
                            status=new_st,
                            recruiter_response=f"Status updated to {new_st} by candidate"
                        )
                        st.rerun()
            st.divider()

# ---------------- TAB 5: PROFILE & MATCHER SANDBOX ----------------
with tab_sandbox:
    st.subheader("Candidate Profile & AI Matcher Sandbox")
    st.write("Test how candidate profile matches against any custom job posting in real time:")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        test_title = st.text_input("Job Title", value="Junior Java / Spring Boot Developer")
        test_company = st.text_input("Company Name", value="Innovative Tech Solutions")
        test_location = st.text_input("Location", value="Bengaluru / Remote")
        test_min_exp = st.number_input("Min Experience (Years)", min_value=0.0, max_value=15.0, value=0.5, step=0.5)
        test_max_exp = st.number_input("Max Experience (Years)", min_value=0.0, max_value=15.0, value=2.0, step=0.5)
    with col_s2:
        test_skills = st.text_area("Required Skills (comma separated)", value="Java, Spring Boot, MySQL, REST APIs, Docker")
        test_desc = st.text_area("Job Description", value="Looking for an Associate Java Developer with Spring Boot experience to develop scalable backend microservices, REST APIs, and MySQL databases. Experience with React or Docker is a bonus. Freshers and candidates with 0-1 year experience welcome.", height=130)

    if st.button("🧪 Calculate AI Match Score", type="primary"):
        matcher = JobMatcher(CANDIDATE_PROFILE)
        test_job = {
            "title": test_title,
            "company_name": test_company,
            "location": test_location,
            "is_remote": "remote" in test_location.lower(),
            "min_experience_years": test_min_exp,
            "max_experience_years": test_max_exp,
            "required_skills": [s.strip() for s in test_skills.split(",") if s.strip()],
            "description": test_desc,
            "salary_raw": "₹7-9 LPA",
            "min_salary_lpa": 7.0,
            "max_salary_lpa": 9.0
        }
        res = matcher.evaluate(test_job)
        b = res["match_breakdown"]

        st.markdown(f"### Result: **{res['match_score']}%** — Status: `{res['status']}`")
        if res["match_score"] >= MIN_MATCH_SCORE:
            st.success("✅ Qualified Opportunity! Meets the 70% threshold.")
        else:
            st.warning("⚠️ Below 70% threshold. Filtered out.")

        col_sb1, col_sb2, col_sb3, col_sb4 = st.columns(4)
        col_sb1.metric("Skills Alignment", f"{b['skills_score']}%")
        col_sb2.metric("Title Alignment", f"{b['title_score']}%")
        col_sb3.metric("Experience Alignment", f"{b['experience_score']}%")
        col_sb4.metric("Location Alignment", f"{b['location_score']}%")

        st.markdown("**Matched Skills:** " + ", ".join(b["matched_skills"]))
        if b["missing_skills"]:
            st.markdown("**Missing Skills:** " + ", ".join(b["missing_skills"]))

# ---------------- TAB 6: ANALYTICS & STATISTICS ----------------
with tab_analytics:
    st.subheader("System Performance & Platform Analytics")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("#### Jobs by Platform")
        plat_data = stats.get("platform_stats", [])
        if plat_data:
            df_plat = pd.DataFrame(plat_data)
            st.dataframe(df_plat, use_container_width=True)
            st.bar_chart(df_plat.set_index("platform")["count"])
        else:
            st.info("No platform data yet.")

    with col_a2:
        st.markdown("#### Discovery Activity")
        trend_data = stats.get("daily_trend", [])
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            st.line_chart(df_trend.set_index("date")["count"])
        else:
            st.info("Trend data will populate over the next few days.")
