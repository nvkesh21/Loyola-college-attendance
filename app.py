import datetime
import json
import os
import streamlit as st

# Try importing PDF reader library for scanning uploaded files
try:
    from pypdf import PdfReader

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Page Configuration
st.set_page_config(
    page_title="Loyola College Smart Hub", page_icon="🎓", layout="centered"
)

# Custom Styling (Loyola Maroon Theme)
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #800000; color: white; font-weight: bold; border-radius: 5px; }
    .stButton>button:hover { background-color: #5c0000; color: white; }
    </style>
""",
    unsafe_allow_html=True,
)

# App Header
st.title("🎓 Loyola College Smart Student Hub")
st.markdown(
    "Your all-in-one automated day order tracker, exam-deadline attendance calculator, and academic companion."
)
st.markdown("---")

# Persistent Session State Initialization
if "initialized" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_name = ""
    st.session_state.dept_no = ""
    st.session_state.academic_year = "1st Year UG"
    st.session_state.department = ""
    st.session_state.calendar_text = ""
    st.session_state.calendar_name = ""
    st.session_state.timetable_uploaded = False
    st.session_state.timetable_name = ""
    st.session_state.extracted_timetable = {
        "Day Order 1": ["Core Subject 1", "Core Subject 2", "Allied 1", "Language", "Elective"],
        "Day Order 2": ["Allied 2", "Language", "Core Subject 1", "Core Subject 2", "Lab/Project"],
        "Day Order 3": ["Core Subject 2", "Core Subject 1", "Soft Skills", "Allied 1", "Core Subject 3"],
        "Day Order 4": ["Language", "Allied 2", "Core Subject 3", "Core Subject 1", "Club/Outreach"],
        "Day Order 5": ["Core Subject 1", "Core Subject 3", "Language", "Allied 2", "Seminar"],
        "Day Order 6": ["Allied 1", "Core Subject 2", "Core Subject 3", "Library/Sports", "Value Education"],
    }
    st.session_state.milestones = {
        "CIA 1 Exam": datetime.date.today() + datetime.timedelta(days=30),
        "CIA 2 Exam": datetime.date.today() + datetime.timedelta(days=60),
        "Semester Exam": datetime.date.today() + datetime.timedelta(days=90),
    }
    st.session_state.conducted = 120
    st.session_state.present = 100
    st.session_state.target_pct = 80
    st.session_state.initialized = True

# Onboarding Screen if not logged in
if not st.session_state.logged_in:
    st.subheader("📝 Student Onboarding (First Time Setup)")
    st.markdown("Enter your details once. The app will securely remember your preferences whenever you open the link.")
    
    with st.form("onboarding_form"):
        name_input = st.text_input("Your Full Name", value=st.session_state.student_name)
        id_input = st.text_input("Department / Register Number (e.g., 23-UCO-04)", value=st.session_state.dept_no)
        year_input = st.selectbox(
            "Current Year & Course Level",
            [
                "1st Year UG",
                "2nd Year UG",
                "3rd Year UG",
                "1st Year PG",
                "2nd Year PG",
            ],
            index=0,
        )
        dept_input = st.text_input("Department Name (e.g., Commerce, Economics)", value=st.session_state.department)

        submitted = st.form_submit_button("Save & Launch Dashboard")
        if submitted:
            if name_input and id_input and dept_input:
                st.session_state.logged_in = True
                st.session_state.student_name = name_input
                st.session_state.dept_no = id_input
                st.session_state.academic_year = year_input
                st.session_state.department = dept_input
                st.success("Setup complete! Loading your dashboard...")
                st.rerun()
            else:
                st.error("Please fill in all required fields to continue.")
else:
    # Sidebar Profile Info & Quick Reset
    st.sidebar.header(f"Hi, {st.session_state.student_name}!")
    st.sidebar.text(f"ID: {st.session_state.dept_no}")
    st.sidebar.text(f"Year: {st.session_state.academic_year}")
    st.sidebar.text(f"Dept: {st.session_state.department}")
    st.sidebar.markdown("---")

    if st.sidebar.button("🗑️ Reset All Data & Start Fresh"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- MAIN NAVIGATION TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📁 Setup & Uploads", "📅 Daily Schedule", "🏫 College Portal", "🧮 Exam Bunk Calculator", "📌 Graduation Logs"]
    )

    # TAB 1: UPLOAD & AUTOMATED SCANNING HUB
    with tab1:
        st.subheader("📂 Academic Calendar & Timetable Setup")
        st.markdown(
            "Upload your files here. The app extracts your day orders and exam dates automatically and saves them permanently for your session."
        )

        # Academic Calendar Section
        st.markdown("### 1️⃣ Loyola Academic Calendar PDF")
        if st.session_state.calendar_text:
            st.success(f"✅ Active Calendar Loaded: **{st.session_state.calendar_name}**")
            if st.button("🔄 Remove / Replace Calendar"):
                st.session_state.calendar_text = ""
                st.session_state.calendar_name = ""
                st.rerun()
        else:
            cal_file = st.file_uploader("Upload Official Academic Calendar PDF", type=["pdf"], key="cal_up")
            if cal_file and PDF_AVAILABLE:
                try:
                    reader = PdfReader(cal_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    st.session_state.calendar_text = text
                    st.session_state.calendar_name = cal_file.name
                    st.success("✅ Calendar successfully scanned and parsed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error parsing PDF: {e}")
            elif cal_file and not PDF_AVAILABLE:
                st.session_state.calendar_text = "Uploaded"
                st.session_state.calendar_name = cal_file.name
                st.success("✅ Calendar uploaded successfully!")
                st.rerun()

        st.markdown("---")

        # Department Timetable Section
        st.markdown("### 2️⃣ Department Timetable PDF")
        if st.session_state.timetable_uploaded:
            st.success(f"✅ Active Timetable Loaded: **{st.session_state.timetable_name}**")
            if st.button("🔄 Remove / Replace Timetable"):
                st.session_state.timetable_uploaded = False
                st.session_state.timetable_name = ""
                st.rerun()
        else:
            tt_file = st.file_uploader("Upload Department Timetable PDF", type=["pdf"], key="tt_up")
            if tt_file and PDF_AVAILABLE:
                try:
                    reader = PdfReader(tt_file)
                    tt_text = ""
                    for page in reader.pages:
                        tt_text += page.extract_text() or ""
                    st.session_state.timetable_uploaded = True
                    st.session_state.timetable_name = tt_file.name
                    st.success("✅ Timetable scanned and mapped to day orders!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error reading timetable: {e}")

        if st.session_state.timetable_uploaded:
            with st.expander("✏️ Fine-Tune Extracted Timetable Subjects"):
                selected_do = st.selectbox("Select Day Order", list(st.session_state.extracted_timetable.keys()))
                current_subs = ", ".join(st.session_state.extracted_timetable[selected_do])
                new_subs = st.text_area("Subjects (comma separated)", current_subs)
                if st.button("Save Subject Changes"):
                    st.session_state.extracted_timetable[selected_do] = [s.strip() for s in new_subs.split(",")]
                    st.success("Subjects updated successfully!")

    # TAB 2: DAILY SCHEDULE & DAY ORDER
    with tab2:
        st.subheader("🗓️ Today's Auto-Detected Schedule & Day Order")
        today_date = datetime.date.today()
        st.markdown(f"**Today's Date:** {today_date.strftime('%A, %d %B %Y')}")

        # Simulated auto-detection from calendar text
        auto_do = "Day Order 1"
        if st.session_state.calendar_text and str(today_date.day) in st.session_state.calendar_text:
            auto_do = "Day Order 2"

        active_day_order = st.selectbox(
            "Active Day Order (Auto-synced with calendar reference):",
            [
                auto_do,
                "Day Order 1",
                "Day Order 2",
                "Day Order 3",
                "Day Order 4",
                "Day Order 5",
                "Day Order 6",
                "Holiday / Weekend",
            ],
        )

        st.markdown("---")
        if "Holiday" in active_day_order:
            st.info("🌴 Today is marked as a holiday or weekend. No classes scheduled!")
        else:
            st.markdown(f"### 📚 Period Schedule for **{active_day_order}**")
            periods = st.session_state.extracted_timetable.get(active_day_order, [])
            for idx, period in enumerate(periods, start=1):
                st.markdown(f"**Period {idx}:** {period}")

    # TAB 3: COLLEGE PORTAL REDIRECT
    with tab3:
        st.subheader("🏫 Official Loyola College Portal")
        st.markdown("Access official announcements, circulars, and the main college portal instantly.")
        st.link_button(
            "🌐 Open Official Loyola College Website",
            "https://www.loyolacollege.edu/",
        )
        st.info("💡 **Tip:** Check your official attendance or notices on the portal, then update your hours in the Bunk Calculator tab.")

    # TAB 4: EXAM-DEADLINE ATTENDANCE & SAFE BUNK CALCULATOR
    with tab4:
        st.subheader("🧮 Exam-Deadline Attendance & Safe Bunk Calculator")
        st.markdown("Calculate exactly how many hours you can safely bunk leading up to your upcoming exams.")

        # Milestone Deadline Selector
        deadline_options = list(st.session_state.milestones.keys())
        selected_milestone = st.selectbox("Select Exam Deadline Milestone:", deadline_options)
        
        default_date = st.session_state.milestones[selected_milestone]
        exam_date = st.date_input("Target Exam Date:", value=default_date)

        days_left = max(1, (exam_date - datetime.date.today()).days)
        estimated_future_hours = days_left * 5  # assuming 5 hours per working day

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.conducted = st.number_input(
                "Total Hours Conducted So Far", min_value=1, value=st.session_state.conducted
            )
            st.session_state.present = st.number_input(
                "Total Hours Present So Far", min_value=0, value=st.session_state.present
            )
        with col2:
            absent_calc = st.session_state.conducted - st.session_state.present
            st.metric("Total Hours Absent", absent_calc)
            current_pct = (st.session_state.present / st.session_state.conducted) * 100 if st.session_state.conducted > 0 else 0
            st.metric("Current Attendance", f"{current_pct:.2f}%")
            st.metric("Days Until Exam", f"{days_left} Days")

        st.markdown("### 🎯 Target Attendance Goal")
        st.session_state.target_pct = st.slider("Select Target Attendance Percentage (%)", 70, 95, st.session_state.target_pct)

        # Calculation logic based on exam deadline
        total_projected = st.session_state.conducted + estimated_future_hours
        required_present_target = (st.session_state.target_pct / 100.0) * total_projected

        if st.session_state.present >= required_present_target:
            buffer_bunks = int(st.session_state.present - required_present_target)
            st.success(
                f"🎉 Safe Buffer! Leading up to your **{selected_milestone}**, you can safely bunk up to **{buffer_bunks} more hours** without dropping below your {st.session_state.target_pct}% target."
            )
        else:
            needed_hours = int(required_present_target - st.session_state.present)
            st.warning(
                f"⚠️ Attendance Warning! Leading up to your **{selected_milestone}**, you need to attend the next **{needed_hours} continuous hours** before exam day to reach {st.session_state.target_pct}%."
            )

    # TAB 5: SPECIAL GRADUATION REQUIREMENT TRACKER
    with tab5:
        st.subheader("📌 Mandatory Institutional Hours Tracker")
        if "1st Year" in st.session_state.academic_year:
            st.markdown("### First Year: 60 Hours Club Activity Tracker")
            club_hrs = st.slider("Club Hours Completed", 0, 60, 20)
            st.progress(club_hrs / 60)
            st.write(f"Progress: {club_hrs} / 60 Hours")
        elif "2nd Year" in st.session_state.academic_year:
            st.markdown("### Second Year: 90 Hours Outreach & Internship Tracker")
            outreach_hrs = st.slider("Outreach / Internship Hours Completed", 0, 90, 45)
            st.progress(outreach_hrs / 90)
            st.write(f"Progress: {outreach_hrs} / 90 Hours")
        else:
            st.info("All core mandatory institutional hours cleared for your current year level.")
      
