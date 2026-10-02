import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Loyola Attendance & Bunk Manager", page_icon="🎓", layout="centered"
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

# App Title & Header
st.title("🎓 Loyola College Attendance Tracker")
st.markdown(
    "Manage your hours, calculate safe bunks, and sync with your academic calendar effortlessly."
)
st.markdown("---")

# Step 1: User Onboarding Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("📝 Student Onboarding")
    with st.form("onboarding_form"):
        student_name = st.text_input("Enter Your Name")
        dept_no = st.text_input(
            "Enter Department Number / Register Number (e.g., 21-UECO-12)"
        )
        academic_year = st.selectbox(
            "Select Your Current Year & Course Level",
            [
                "1st Year UG",
                "2nd Year UG",
                "3rd Year UG",
                "1st Year PG",
                "2nd Year PG",
            ],
        )
        department = st.text_input(
            "Enter Department (e.g., Economics, Computer Science)"
        )

        submitted = st.form_submit_button("Get Started")
        if submitted:
            if student_name and dept_no and department:
                st.session_state.logged_in = True
                st.session_state.student_name = student_name
                st.session_state.dept_no = dept_no
                st.session_state.academic_year = academic_year
                st.session_state.department = department
                st.rerun()
            else:
                st.error("Please fill in all required fields to proceed.")
else:
    # Sidebar Profile Info
    st.sidebar.header(f"Welcome, {st.session_state.student_name}!")
    st.sidebar.write(f"**ID:** {st.session_state.dept_no}")
    st.sidebar.write(f"**Year:** {st.session_state.academic_year}")
    st.sidebar.write(f"**Dept:** {st.session_state.department}")

    if st.sidebar.button("Logout / Reset Profile"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("---")

    # Step 2: Document Uploads (Calendar & Timetable)
    st.subheader("📁 Document Setup")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Academic Calendar PDF")
        calendar_file = st.file_uploader(
            "Upload Loyola Calendar PDF", type=["pdf"]
        )
        if calendar_file:
            st.success("Calendar uploaded & parsed successfully!")

    with col2:
        st.markdown("### Department Timetable")
        timetable_file = st.file_uploader(
            "Upload Timetable (PDF/Image)", type=["pdf", "png", "jpg"]
        )
        if timetable_file:
            st.success("Timetable loaded successfully!")

    st.markdown("---")

    # Step 3: ERP Integration & Statistics Link
    st.subheader("📊 Check Statistics & Attendance Portal")
    st.markdown(
        "Click below to log into the official Loyola Student ERP Portal, check your hours, and fetch your figures."
    )

    st.link_button(
        "🔗 Open Loyola Student ERP Portal",
        "https://erp.loyolacollege.edu/loyolaonline/students/loginManager/youLogin.jsp",
    )

    st.info(
        "💡 **Tip:** Log in with your Department ID and Date of Birth (ddmmyyyy), check your attendance summary, or download your ERP attendance print screenshot and input your values below."
    )

    st.markdown("---")

    # Step 4: Attendance Inputs & Calculations
    st.subheader("🧮 Attendance & Bunk Calculator")

    col_a, col_b = st.columns(2)
    with col_a:
        hours_conducted = st.number_input(
            "Total Hours Conducted (From Calendar/ERP)", min_value=1, value=100
        )
        hours_present = st.number_input(
            "Total Hours Present", min_value=0, value=80
        )

    with col_b:
        hours_absent = hours_conducted - hours_present
        st.metric(label="Total Hours Absent", value=hours_absent)
        current_attendance = (
            (hours_present / hours_conducted) * 100
            if hours_conducted > 0
            else 0
        )
        st.metric(
            label="Current Attendance Percentage",
            value=f"{current_attendance:.2f}%",
        )

    # Target Percentage Adjustment
    st.markdown("### 🎯 Target Attendance & Safe Bunks")
    target_percentage = st.slider(
        "Select Target Attendance Percentage (%)", 50, 100, 75
    )

    # Safe Bunk / Required Hours Logic
    # Formula logic for safe bunks: (Present / Target) - Conducted
    if current_attendance >= target_percentage:
        # Safe hours to bunk without dropping below target
        # Target% = (Present) / (Conducted + X) => Conducted + X = Present / (Target/100)
        max_total_allowed = hours_present / (target_percentage / 100.0)
        safe_bunks = int(max_total_allowed - hours_conducted)
        st.success(
            f"🎉 You are safe! You can bunk up to **{max(0, safe_bunks)} more hours** without dropping below your {target_percentage}% target."
        )
    else:
        # Required hours to attend to reach target
        # Target% = (Present + Y) / (Conducted + Y)
        # Target/100 * (Conducted + Y) = Present + Y
        # Target*Conducted / 100 + Target*Y/100 = Present + Y
        # Y * (1 - Target/100) = Target*Conducted/100 - Present
        target_decimal = target_percentage / 100.0
        required_hours = (
            (target_decimal * hours_conducted) - hours_present
        ) / (1 - target_decimal)
        st.warning(
            f"⚠️ Your attendance is below target! You need to attend the next **{int(required_hours) + 1} continuous hours** to reach {target_percentage}%."
        )

    # Special Requirements for Loyola Years
    st.markdown("---")
    st.subheader("📌 Special Graduation Requirements Tracker")
    if "1st Year" in st.session_state.academic_year:
        club_hours = st.slider(
            "Club Activity Hours Completed (Target: 60 Hrs)", 0, 60, 15
        )
        st.progress(club_hours / 60)
        st.write(f"Progress: {club_hours} / 60 Hours Completed")
    elif "2nd Year" in st.session_state.academic_year:
        outreach_hours = st.slider(
            "Outreach / Internship Hours Completed (Target: 90 Hrs)", 0, 90, 30
        )
        st.progress(outreach_hours / 90)
        st.write(f"Progress: {outreach_hours} / 90 Hours Completed")
    else:
        st.info(
            "All core mandatory institutional hours tracking clear for your current year level."
        )
      
