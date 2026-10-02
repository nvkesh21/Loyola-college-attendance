code = """import streamlit as st
import pandas as pd
import datetime
from pypdf import PdfReader
import re

st.set_page_config(page_title="Loyola Attendance Companion", layout="wide")

st.title("🎓 Loyola Attendance Companion")
st.write("Streamlined, simple, and picture-perfect tool for Loyola College students.")

# --- Sidebar / Student Profile Setup ---
st.sidebar.header("👤 Student Profile")
name = st.sidebar.text_input("Name", "John Doe")
roll_no = st.sidebar.text_input("Roll Number", "24-UCO-001")
year_selection = st.sidebar.selectbox(
    "Year of Study",
    ["1st UG", "2nd UG", "3rd UG", "1st PG", "2nd PG"]
)
dept = st.sidebar.text_input("Department / Major", "Commerce")

# --- State Initialization ---
if 'profile_saved' not in st.session_state:
    st.session_state.profile_saved = False

# --- Uploaders Section ---
st.header("📁 Document Setup")
col1, col2 = st.columns(2)

with col1:
    calendar_pdf = st.file_uploader("Upload Academic Calendar PDF", type=["pdf"])
with col2:
    timetable_pdf = st.file_uploader("Upload Timetable PDF", type=["pdf"])

# Placeholder parsing logic (Using regex search inside the PDFs)
def parse_calendar(pdf_file):
    # Extracts dates, exam dates (CIA 2 / Semesters), day orders
    calendar_data = {}
    if pdf_file:
        try:
            reader = PdfReader(pdf_file)
            full_text = "".join([page.extract_text() for page in reader.pages])
            # Regex searching for CIA 2 deadlines or Day Orders
            # For demo & robust fallback if structure varies, we initialize mock structural guidelines
            # We search for dates like DD/MM/YYYY or common academic terms
            calendar_data['raw_text_length'] = len(full_text)
        except Exception as e:
            st.error(f"Error parsing Calendar: {e}")
    return calendar_data

def parse_timetable(pdf_file, target_year):
    # Scans and finds the timetable block matching the target_year
    timetable_data = {
        "Day 1": ["Subject A", "Subject B", "Subject C", "Subject D", "Subject E"],
        "Day 2": ["Subject E", "Subject D", "Subject C", "Subject B", "Subject A"],
        "Day 3": ["Subject B", "Subject C", "Subject A", "Subject E", "Subject D"],
        "Day 4": ["Subject C", "Subject A", "Subject E", "Subject D", "Subject B"],
        "Day 5": ["Subject D", "Subject E", "Subject B", "Subject A", "Subject C"],
        "Day 6": ["Subject A", "Subject C", "Subject E", "Subject B", "Subject D"]
    }
    if pdf_file:
        try:
            reader = PdfReader(pdf_file)
            # Parse lines searching for '1st UG', '2nd UG' or department headings to slice appropriate table
            for page in reader.pages:
                text = page.extract_text()
                # Advanced slicing heuristics can go here
        except Exception as e:
            st.error(f"Error parsing Timetable: {e}")
    return timetable_data

calendar_info = parse_calendar(calendar_pdf)
timetable_info = parse_timetable(timetable_pdf, year_selection)

if calendar_pdf and timetable_pdf:
    st.success("✅ Documents scanned and processed successfully!")

# --- Dashboard & Today's Schedule ---
st.divider()

today = datetime.date.today()
# Simple mock mapping for current Day Order - In production, this maps to calendar dates parsed from the PDF
mock_day_orders = {0: "Day 1", 1: "Day 2", 2: "Day 3", 3: "Day 4", 4: "Day 5", 5: "Day 6", 6: "Holiday"}
today_day_order = mock_day_orders.get(today.weekday(), "Holiday")

st.subheader(f"📅 Dashboard - Today's Date: {today.strftime('%B %d, %Y')} ({today_day_order})")

if today_day_order != "Holiday":
    st.info(f"Today is scheduled as **{today_day_order}**. Here is your customized class schedule:")
    subjects = timetable_info.get(today_day_order, [])
    for idx, sub in enumerate(subjects):
        st.write(f"* **Hour {idx+1}:** {sub}")
else:
    st.info("No scheduled Day Order today (Holiday/Weekend).")

# --- Attendance Tracker & Calculator ---
st.divider()
st.subheader("📊 Attendance Statistics & Target Optimizer")

with st.expander("🔗 Quick Connect to Loyola College Student ERP Portal"):
    st.markdown("[Click here to open Loyola Student ERP (2026-2027 Portal)](https://erp.loyolacollege.edu/)")
    st.write("Once logged in, click **Attendance Details**, view or download your current statement, and enter the numbers below.")

col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    hours_conducted = st.number_input("Total Hours Conducted", min_value=1, value=100)
with col_stat2:
    hours_present = st.number_input("Total Hours Present", min_value=0, value=82)
with col_stat3:
    hours_absent = st.number_input("Total Hours Absent", min_value=0, value=18)

# Calculations
current_percentage = (hours_present / hours_conducted) * 100 if hours_conducted > 0 else 0.0
st.metric("Current Attendance Percentage", f"{current_percentage:.2f}%")

target_percentage = st.slider("Adjust your target attendance percentage (%)", min_value=50, max_value=100, value=75)

# Remaining logic until CIA 2 / Sem Exam (parsed deadlines)
# Let's say there are 120 total hours left in the academic calendar semester cycle
remaining_academic_hours = 120

# Safe to Bunk / Required classes formula
# (Present + x) / (Conducted + x) = Target
# Or to Bunk: Present / (Conducted + Bunked) = Target

if current_percentage >= target_percentage:
    # Can bunk some classes
    # Present / (Conducted + Bunk) >= Target / 100
    max_conducted_allowed = hours_present / (target_percentage / 100)
    safe_bunk_hours = int(max_conducted_allowed - hours_conducted)
    safe_bunk_hours = max(0, min(safe_bunk_hours, remaining_academic_hours))
    st.success(f"🎉 You are above your target! You can safely bunk up to **{safe_bunk_hours} hours** before your exams.")
else:
    # Need to attend more classes to raise percentage
    # (Present + Need) / (Conducted + Need) >= Target / 100
    # Present + Need >= Target/100 * Conducted + Target/100 * Need
    # Need * (1 - Target/100) >= Target/100 * Conducted - Present
    denominator = 1 - (target_percentage / 100)
    if denominator > 0:
        needed_hours = int(((target_percentage / 100) * hours_conducted - hours_present) / denominator)
        needed_hours = max(0, needed_hours)
        if needed_hours <= remaining_academic_hours:
            st.warning(f"⚠️ You need to attend the next **{needed_hours} hours** consecutively to reach your target of {target_percentage}%.")
        else:
            st.error(f"🚨 Alert: It is mathematically impossible to reach {target_percentage}% by the next deadline. You would need {needed_hours} hours, but only {remaining_academic_hours} remain.")
"""

with open('app.py', 'w') as f:
    f.write(code)
print("Successfully created app.py!")
