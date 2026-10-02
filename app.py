import datetime
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Loyola College One-Stop Dashboard", page_icon="🎓", layout="centered"
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
st.title("🎓 Loyola College Student Hub")
st.markdown(
    "Your one-stop daily companion for Day Orders, Timetables, and Attendance."
)
st.markdown("---")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("📝 Quick Setup")
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

        submitted = st.form_submit_button("Launch Dashboard")
        if submitted:
            if student_name and dept_no and department:
                st.session_state.logged_in = True
                st.session_state.student_name = student_name
                st.session_state.dept_no = dept_no
                st.session_state.academic_year = academic_year
                st.session_state.department = department
                # Default mock timetable structure
                st.session_state.timetable = {
                    "Day Order 1": [
                        "Period 1: Core",
                        "Period 2: Core",
                        "Period 3: Allied",
                        "Period 4: Language",
                        "Period 5: Generic Elective",
                    ],
                    "Day Order 2": [
                        "Period 1: Allied",
                        "Period 2: Language",
                        "Period 3: Core",
                        "Period 4: Core",
                        "Period 5: Lab/Project",
                    ],
                    "Day Order 3": [
                        "Period 1: Core",
                        "Period 2: Core",
                        "Period 3: Soft Skills",
                        "Period 4: Allied",
                        "Period 5: Core",
                    ],
                    "Day Order 4": [
                        "Period 1: Language",
                        "Period 2: Allied",
                        "Period 3: Core",
                        "Period 4: Core",
                        "Period 5: Club/Outreach",
                    ],
                    "Day Order 5": [
                        "Period 1: Core",
                        "Period 2: Core",
                        "Period 3: Language",
                        "Period 4: Allied",
                        "Period 5: Seminar",
                    ],
                    "Day Order 6": [
                        "Period 1: Allied",
                        "Period 2: Core",
                        "Period 3: Core",
                        "Period 4: Sports/Library",
                        "Period 5: Value Education",
                    ],
                }
                st.rerun()
            else:
                st.error("Please fill in all details.")
else:
    # Sidebar Hub
    st.sidebar.header(f"Hi, {st.session_state.student_name}!")
    st.sidebar.text(f"ID: {st.session_state.dept_no}")
    st.sidebar.text(f"Year: {st.session_state.academic_year}")

    if st.sidebar.button("Reset Profile"):
        st.session_state.logged_in = False
        st.rerun()

    # --- MAIN DASHBOARD TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📅 Today & Timetable", "📊 ERP Portal & Stats", "🧮 Bunk Calculator", "📌 Graduation Logs"]
    )

    # TAB 1: TODAY & TIMETABLE (Dynamic Day Order view)
    with tab1:
        st.subheader("🗓️ Daily Schedule & Day Order")

        today_date = datetime.date.today().strftime("%A, %d %B %Y")
        st.markdown(f"**Today's Date:** {today_date}")

        # Day Order Selector synced with calendar reference
        selected_day_order = st.selectbox(
            "Active Day Order for Today (Auto-synced from Calendar reference):",
            [
                "Day Order 1",
                "Day Order 2",
                "Day Order 3",
                "Day Order 4",
                "Day Order 5",
                "Day Order 6",
                "Holiday / Sunday",
            ],
        )

        st.markdown("---")
        if "Holiday" in selected_day_order:
            st.info(
                "🌴 No classes scheduled for today! Enjoy your holiday or catch up on rest."
            )
        else:
            st.markdown(f"### 📚 Timetable Schedule for **{selected_day_order}**")
            periods = st.session_state.timetable.get(
                selected_day_order, ["No classes found"]
            )

            for idx, period in enumerate(periods, start=1):
                st.markdown(f"**Hour {idx}:** {period}")

            with st.expander("✏️ Customize Your Department Timetable"):
                st.markdown(
                    "Update your specific year/department subjects for each day order:"
                )
                do_to_edit = st.selectbox(
                    "Select Day Order to Edit", list(st.session_state.timetable.keys())
                )
                current_subjects = ", ".join(st.session_state.timetable[do_to_edit])
                new_subs_input = st.text_area(
                    "Enter subjects separated by commas (Period 1 to 5)",
                    current_subjects,
                )
                if st.button("Save Timetable Changes"):
                    st.session_state.timetable[do_to_edit] = [
                        s.strip() for s in new_subs_input.split(",")
                    ]
                    st.success("Timetable updated successfully!")
                    st.rerun()

    # TAB 2: ERP PORTAL & STATS LINK
    with tab2:
        st.subheader("🌐 Loyola College Official Portal & ERP")
        st.markdown(
            "Click below to visit the official Loyola College website or jump straight into the student ERP portal to view your live attendance figures."
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.link_button(
                "🏫 Official Loyola College Website",
                "https://www.loyolacollege.edu/",
            )
        with col_p2:
            st.link_button(
                "🔐 Student ERP Login Portal",
                "https://erp.loyolacollege.edu/loyolaonline/students/loginManager/youLogin.jsp",
            )

        st.info(
            "💡 **Instructions:** Log into the ERP portal using your Department ID and Date of Birth (ddmmyyyy format). Check your summary, then record your hours below."
        )

    # TAB 3: ATTENDANCE & BUNK CALCULATOR
    with tab3:
        st.subheader("🧮 Attendance & Safe Bunk Calculator")

        col_a, col_b = st.columns(2)
        with col_a:
            hours_conducted = st.number_input(
                "Total Hours Conducted So Far", min_value=1, value=120
            )
            hours_present = st.number_input(
                "Total Hours Present", min_value=0, value=100
            )

        with col_b:
            hours_absent = hours_conducted - hours_present
            st.metric("Total Hours Absent", hours_absent)
            current_pct = (
                (hours_present / hours_conducted) * 100
                if hours_conducted > 0
                else 0
            )
            st.metric("Current Attendance", f"{current_pct:.2f}%")

        st.markdown("### 🎯 Target Goal & Safe Bunks")
        target_pct = st.slider("Target Attendance Percentage (%)", 50, 95, 75)

        if current_pct >= target_pct:
            max_allowed = hours_present / (target_pct / 100.0)
            safe_bunks = int(max_allowed - hours_conducted)
            st.success(
                f"🎉 You are clear! You can safely bunk up to **{max(0, safe_bunks)} more hours** without dropping below {target_pct}%."
            )
        else:
            target_dec = target_pct / 100.0
            needed = (
                (target_dec * hours_conducted) - hours_present
            ) / (1 - target_dec)
            st.warning(
                f"⚠️ Attendance low! Attend the next **{int(needed) + 1} continuous hours** to hit your {target_pct}% benchmark."
            )

    # TAB 4: SPECIAL GRADUATION REQUIREMENT TRACKER
    with tab4:
        st.subheader("📌 Mandatory Institutional Hours Tracker")
        if "1st Year" in st.session_state.academic_year:
            st.markdown("### First Year: 60 Hours Club Activity Tracker")
            club = st.slider("Club Hours Logged", 0, 60, 20)
            st.progress(club / 60)
            st.write(f"Progress: {club} / 60 Hours")
        elif "2nd Year" in st.session_state.academic_year:
            st.markdown("### Second Year: 90 Hours Outreach & Internship Tracker")
            outreach = st.slider("Outreach/Internship Hours Logged", 0, 90, 45)
            st.progress(outreach / 90)
            st.write(f"Progress: {outreach} / 90 Hours")
        else:
            st.info(
                "No additional mandatory activity hour requirements listed for your current year level."
  )
          
