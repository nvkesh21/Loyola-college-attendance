import datetime
from io import BytesIO
import pandas as pd
import pypdf
import streamlit as st

# Page Configuration for Mobile-Friendly Experience
st.set_page_config(
    page_title="Loyola Attendance Tracker",
    page_icon="🎓",
    layout="centered",
)

# Custom CSS for Mobile Optimization and Clean UI
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .metric-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

# --- STEP 1: ONBOARDING / USER DETAILS ---
if not st.session_state.logged_in:
  st.title("🎓 Loyola Attendance Tracker")
  st.write(
      "Seamlessly track your attendance, safe bunks, and exam deadlines based"
      " strictly on the academic calendar."
  )

  with st.form("user_setup"):
    st.subheader("Student Details")
    name = st.text_input("Full Name")
    roll_number = st.text_input("Roll Number / Application ID")
    year = st.selectbox(
        "Select Your Year",
        [
            "1st Year UG",
            "2nd Year UG",
            "3rd Year UG",
            "1st Year PG",
            "2nd Year PG",
        ],
    )
    department = st.text_input("Department (e.g., B.Sc. Mathematics, B.Com)")

    st.subheader("Upload Documents")
    calendar_pdf = st.file_uploader(
        "Upload Academic Calendar PDF", type=["pdf"]
    )
    timetable_pdf = st.file_uploader("Upload Department Timetable PDF", type=["pdf"])

    submit_button = st.form_submit_button("Launch Dashboard 🚀")

    if submit_button:
      if name and roll_number and department and calendar_pdf and timetable_pdf:
        st.session_state.logged_in = True
        st.session_state.name = name
        st.session_state.roll_number = roll_number
        st.session_state.year = year
        st.session_state.department = department

        # Read PDFs safely
        reader_cal = pypdf.PdfReader(calendar_pdf)
        cal_text = "".join(
            [page.extract_text() for page in reader_cal.pages]
        )
        st.session_state.cal_text = cal_text

        st.success("Setup complete! Loading your dashboard...")
        st.rerun()
      else:
        st.error("Please fill in all fields and upload both PDFs to proceed.")

else:
  # --- STEP 2: MAIN DASHBOARD ---
  st.sidebar.title(f"Welcome, {st.session_state.name}!")
  st.sidebar.write(f"**Roll No:** {st.session_state.roll_number}")
  st.sidebar.write(
      f"**Class:** {st.session_state.year} - {st.session_state.department}"
  )

  st.sidebar.markdown("---")
  st.sidebar.subheader("🔗 Quick Links")
  st.sidebar.markdown(
      "[Official Loyola College Website](https://www.loyola.edu)"
  )
  st.sidebar.markdown(
      "[Student ERP Portal Login](https://erp.loyola.edu)"
      " *(Check attendance here manually)*"
  )

  st.sidebar.markdown("---")
  if st.sidebar.button("Log Out / Reset Setup"):
    st.session_state.logged_in = False
    st.rerun()

  # Main Screen Content
  st.title("📊 Attendance & Bunk Dashboard")

  # Date and Day Order Check
  today = datetime.date.today()
  st.info(
      f"📅 **Today's Date:** {today.strftime('%A, %d %B %Y')} | Operating"
      " strictly on Total Hours Conduced."
  )

  # Manual Input for Hours (The reliable workaround for ERP)
  st.markdown("### 📥 Input Your Attendance Data")
  st.write(
      "Log into the official ERP portal via the sidebar link, check your hours,"
      " and input them below:"
  )

  col1, col2 = st.columns(2)
  with col1:
    total_conducted = st.number_input(
        "Total Hours Conducted So Far", min_value=0, value=50, step=1
    )
  with col2:
    total_present = st.number_input(
        "Total Hours Present", min_value=0, value=45, step=1
    )

  # Target Attendance Setting
  target_percentage = st.slider(
      "Target Attendance Percentage (%)", min_value=50, max_value=95, value=80
  )

  # Calculations
  if total_conducted > 0:
    current_percentage = (total_present / total_conducted) * 100
  else:
    current_percentage = 100.0

  st.markdown("---")
  st.subheader("📈 Statistics & Bunk Calculator")

  m1, m2 = st.columns(2)
  with m1:
    st.metric(
        label="Current Attendance", value=f"{current_percentage:.2f}%"
    )
  with m2:
    if current_percentage >= target_percentage:
      st.success("Status: Safe zone! You are above target.")
    else:
      st.error("Status: Danger zone! Attendance is low.")

  # Safe Bunk / Recovery Logic based on target requirement
  # Formula logic: (Present) / (Conducted + x) >= target/100
  if current_percentage >= target_percentage:
    # Safe bunks calculation: how many classes can you miss while staying >= target
    # Present / (Conducted + x) = target / 100 => x = (100 * Present / target) - Conducted
    max_classes_total = (100 * total_present) / target_percentage
    safe_bunks = int(max_classes_total - total_conducted)
    st.write(
        f"🟢 **Safe Bunks Available:** You can safely skip approximately **"
        f" {max(0, safe_bunks)} hours** without dropping below your"
        f" {target_percentage}% target before CIA 2 / Semester exams."
    )
  else:
    # Recovery calculation: how many consecutive classes must you attend
    # (Present + x) / (Conducted + x) = target / 100
    # 100*Present + 100x = target*Conducted + target*x
    # x * (100 - target) = target*Conducted - 100*Present
    classes_needed = (
        (target_percentage * total_conducted) - (100 * total_present)
    ) / (100 - target_percentage)
    st.write(
        f"🔴 **Classes Needed for Recovery:** You need to attend the next **"
        f" {int(classes_needed) + 1} consecutive hours** to bounce back up to"
        f" your {target_percentage}% target."
    )

  # Specific College Guidelines Footer Note
  st.markdown("---")
  st.caption(
      "💡 *Note: Account for institutional specific requirements like the 60-hour"
      " club activity (1st Year) or 90-hour outreach/internships (2nd Year) as"
      " outlined in your academic calendar PDF.*"
  )
  st.markdown(
      "<div style='text-align: center; color: gray;'>Built with ☕ by a student"
      " at Loyola College</div>",
      unsafe_allow_html=True,
  )
  
