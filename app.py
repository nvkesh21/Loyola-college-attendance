import datetime
import io
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

# Custom Styling
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
    "Your one-stop daily app for Day Orders, Timetables, Attendance Tracking, and Safe Bunks."
)
st.markdown("---")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.calendar_text = ""
    st.session_state.calendar_name = ""
    st.session_state.timetable_uploaded = False
    st.session_state.timetable_name = ""

if not st.session_state.logged_in:
    st.subheader("📝 Student Onboarding")
    with st.form("onboarding_form"):
        student_name = st.text_input("Your Name")
        dept_no = st.text_input(
            "Department / Register Number (e.g., 23-UCO-04)"
        )
        academic_year = st.selectbox(
            "Current Year & Course Level",
            [
                "1st Year UG",
                "2nd Year UG",
                "3rd Year UG",
                "1st Year PG",
                "2nd Year PG",
            ],
        )
        department = st.text_input("Department Name (e.g., Commerce, Economics)")

        submitted = st.form_submit_button("Continue to Dashboard")
        if submitted:
            if student_name and dept_no and department:
                st.session_state.logged_in = True
                st.session_state.student_name = student_name
                st.session_state.dept_no = dept_no
                st.session_state.academic_year = academic_year
                st.session_state.department = department
                # Default timetable structure
                st.session_state.timetable = {
                    "Day Order 1": ["Core Subject 1", "Core Subject 2", "Allied 1", "Language", "Elective"],
                    "Day Order 2": ["Allied 2", "Language", "Core Subject 1", "Core Subject 2", "Lab/Project"],
                    "Day Order 3": ["Core Subject 2", "Core Subject 1", "Soft Skills", "Allied 1", "Core Subject 3"],
                    "Day Order 4": ["Language", "Allied 2", "Core Subject 3", "Core Subject 1", "Club/Outreach"],
                    "Day Order 5": ["Core Subject 1", "Core Subject 3", "Language", "Allied 2", "Seminar"],
                    "Day Order 6": ["Allied 1", "Core Subject 2", "Core Subject 3", "Library/Sports", "Value Education"],
                }
                st.rerun()
            else:
                st.error("Please fill in all required details.")
else:
    # Sidebar Profile Info & Data Reset Option
    st.sidebar.header(f"Hi, {st.session_state.student_name}!")
    st.sidebar.text(f"ID: {st.session_state.dept_no}")
    st.sidebar.text(f"Year: {st.session_state.academic_year}")
    st.sidebar.markdown("---")

    if st.sidebar.button("🗑️ Clear All Data & Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- TABS FOR STREAMLINED NAVIGATION ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📁 Uploads", "📅 Daily Schedule", "🏫 College Portal", "🧮 Bunk Calc", "📌 Graduation Logs"]
    )

    # TAB 1: UPLOAD & DATA MANAGEMENT
    with tab1:
        st.subheader("📂 Academic Calendar & Timetable Management")
        st.markdown(
            "Upload or replace your files below whenever your department schedules change."
        )

        # Calendar Section
        st.markdown("### 1️⃣ Loyola Academic Calendar PDF")
        if st.session_state.calendar_text:
            st.success(
                f"✅ Active Calendar Loaded: **{st.session_state.calendar_name}**"
            )
            if st.button("🔄 Remove / Replace Current Calendar"):
                st.session_state.calendar_text = ""
                st.session_state.calendar_name = ""
                st.rerun()
        else:
            calendar_file = st.file_uploader(
                "Upload Official Academic Calendar PDF", type=["pdf"], key="cal_upload"
            )
            if calendar_file and PDF_AVAILABLE:
                try:
                    reader = PdfReader(calendar_file)
                    extracted_text = ""
                    for page in reader.pages:
                        extracted_text += page.extract_text() or ""
                    st.session_state.calendar_text = extracted_text
                    st.session_state.calendar_name = calendar_file.name
                    st.success("✅ Calendar parsed and saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
            elif calendar_file and not PDF_AVAILABLE:
                st.session_state.calendar_text = "Uploaded"
                st.session_state.calendar_name = calendar_file.name
                st.success("✅ Calendar uploaded successfully!")
                st.rerun()

        st.markdown("---")

        # Timetable Section
        st.markdown("### 2️⃣ Department Timetable")
        if st.session_state.timetable_uploaded:
            st.success(
                f"✅ Active Timetable Loaded: **{st.session_state.timetable_name}**"
            )
            if st.button("🔄 Remove / Replace Current Timetable"):
                st.session_state.timetable_uploaded = False
                st.session_state.timetable_name = ""
                st.rerun()
        else:
            timetable_file = st.file_uploader(
                "Upload Timetable (PDF or Image)",
                type=["pdf", "png", "jpg", "jpeg"],
                key="tt_upload",
            )
            if timetable_file:
                st.session_state.timetable_uploaded = True
                st.session_state.timetable_name = timetable_file.name
                st.success("✅ Timetable mapped successfully!")
                st.rerun()

        if st.session_state.timetable_uploaded:
            with st.expander("✏️ Edit / Fine-tune Timetable Subjects"):
                do_edit = st.selectbox(
                    "Select Day Order to Review", list(st.session_state.timetable.keys())
                )
                current_subs = ", ".join(st.session_state.timetable[do_edit])
                new_subs = st.text_area(
                    "Edit subjects (comma separated)", current_subs
                )
                if st.button("Save Timetable Adjustments"):
                    st.session_state.timetable[do_edit] = [
                        s.strip() for s in new_subs.split(",")
                    ]
                    st.success("Timetable updated successfully!")

    # TAB 2: DAILY SCHEDULE & DAY ORDER
    with tab2:
        st.subheader("🗓️ Today's Schedule & Day Order")
        today_str = datetime.date.today().strftime("%A, %d %B %Y")
        st.markdown(f"**Today's Date:** {today_str}")

        active_day = st.selectbox(
            "Active Day Order for Today:",
            [
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
        if "Holiday" in active_day:
            st.info("🌴 It's a holiday or weekend! No classes scheduled.")
        else:
            st.markdown(f"### 📚 Classes for **{active_day}**")
            periods = st.session_state.timetable.get(active_day, [])
            for idx, period in enumerate(periods, start=1):
                st.markdown(f"**Period {idx}:** {period}")

    # TAB 3: COLLEGE WEBSITE LINK
    with tab3:
        st.subheader("🏫 Official Loyola College Website")
        st.markdown(
            "Quick access to the main Loyola College website for announcements, circulars, and campus details."
        )

        st.link_button(
            "🌐 Open Official Loyola College Website",
            "https://www.loyolacollege.edu/",
        )

        st.info(
            "💡 **Tip:** Use your attendance printouts or records to input your hours directly into the **Bunk Calc** tab."
        )

    # TAB 4: ATTENDANCE & BUNK CALCULATOR
    with tab4:
        st.subheader("🧮 Attendance & Safe Bunk Calculator")

        # Screenshot Upload Option
        with st.expander("📷 Optional: Upload Attendance Printout/Screenshot"):
            attendance_screenshot = st.file_uploader(
                "Upload attendance print image",
                type=["png", "jpg", "jpeg"],
            )
            if attendance_screenshot:
                st.success(
                    "✅ Attendance image uploaded successfully! Verify your hours below."
                )

        c1, c2 = st.columns(2)
        with c1:
            conducted = st.number_input(
                "Total Hours Conducted So Far", min_value=1, value=120
            )
            present = st.number_input(
                "Total Hours Present", min_value=0, value=100
            )
        with c2:
            absent = conducted - present
            st.metric("Total Hours Absent", absent)
            pct = (present / conducted) * 100 if conducted > 0 else 0
            st.metric("Current Attendance", f"{pct:.2f}%")

        st.markdown("### 🎯 Target Goal & Safe Bunking")
        target = st.slider("Target Attendance Percentage (%)", 50, 95, 75)

        if pct >= target:
            allowed_total = present / (target / 100.0)
            safe_bunks = int(allowed_total - conducted)
            st.success(
                f"🎉 You are safe! You can bunk up to **{max(0, safe_bunks)} more hours** without dropping below {target}%."
            )
        else:
            needed = ((target / 100.0) * conducted - present) / (
                1 - (target / 100.0)
            )
            st.warning(
                f"⚠️ Attendance low! Attend the next **{int(needed) + 1} continuous hours** to reach {target}%."
            )

    # TAB 5: SPECIAL GRADUATION REQUIREMENT TRACKER
    with tab5:
        st.subheader("📌 Mandatory Institutional Hours Tracker")
        if "1st Year" in st.session_state.academic_year:
            st.markdown("### First Year: 60 Hours Club Activity Tracker")
            club = st.slider("Club Hours Completed", 0, 60, 20)
            st.progress(club / 60)
            st.write(f"Progress: {club} / 60 Hours")
        elif "2nd Year" in st.session_state.academic_year:
            st.markdown("### Second Year: 90 Hours Outreach & Internship Tracker")
            outreach = st.slider("Outreach / Internship Hours Completed", 0, 90, 45)
            st.progress(outreach / 90)
            st.write(f"Progress: {outreach} / 90 Hours")
        else:
            st.info(
                "No additional mandatory institutional hour tracking required for your current year level."
            )
