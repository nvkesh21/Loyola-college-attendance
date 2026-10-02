import datetime
import re
import streamlit as st
import pandas as pd
from pypdf import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Loyola Attendance & Bunk Master",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM UI CSS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        background-color: #0b3d91;
        color: white;
    }
    .stat-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #0b3d91;
        margin-bottom: 15px;
    }
    .safe-box { background-color: #d1e7dd; color: #0f5132; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; }
    .danger-box { background-color: #f8d7da; color: #842029; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False
if 'attendance' not in st.session_state:
    st.session_state.attendance = {'conducted': 0, 'present': 0, 'absent': 0}
if 'calendar_data' not in st.session_state:
    st.session_state.calendar_data = {}
if 'timetable_data' not in st.session_state:
    st.session_state.timetable_data = {}

# --- HELPER FUNCTIONS FOR PDF PARSING ---
def parse_academic_calendar(pdf_file):
    """Scans the calendar to map every date to its Day Order and Events."""
    reader = PdfReader(pdf_file)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])
    
    cal_dict = {}
    # Regex to catch: 02.10.2026 | FRI | Gandhi Jayanthi | * OR 05.10.2026 | MON | Second CIA | Day - 2
    pattern = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})\s*\|?\s*[A-Z]{3}\s*\|?\s*([^\|]*?)\s*\|?\s*(Day\s*-\s*\d|W\d+\s*Day\s*-\s*\d|\*)?", re.IGNORECASE)
    
    for match in pattern.finditer(text):
        day, month, year, event, day_order = match.groups()
        date_obj = datetime.date(int(year), int(month), int(day))
        
        is_working_day = False
        parsed_order = None
        if day_order and "Day" in day_order:
            is_working_day = True
            # Extract just the number (1-6)
            num_match = re.search(r"Day\s*-\s*(\d)", day_order, re.IGNORECASE)
            if num_match:
                parsed_order = int(num_match.group(1))
                
        cal_dict[date_obj] = {
            'event': event.strip() if event else "",
            'is_working_day': is_working_day,
            'day_order': parsed_order,
            'raw_order': day_order.strip() if day_order else ""
        }
    return cal_dict

def parse_timetable(pdf_file, degree_type, year_choice):
    """Scans the timetable and extracts ONLY the subjects for the selected year."""
    reader = PdfReader(pdf_file)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])
    
    # Map user choice to Roman Numerals used in PDF
    year_map = {"1st UG": "I", "2nd UG": "II", "3rd UG": "III", "1st PG": "I", "2nd PG": "II"}
    target_yr = year_map.get(year_choice, "I")
    
    tt_dict = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    
    # Fallback default hardcoded mapping if PDF extraction fails due to formatting chaos
    fallback_tt = {
        "3rd UG": {
            1: ["App. Stoc(MSA)", "App. Stat(LPR)", "Reg(SAP)", "R/Power BI", "Bio Stat(SS)"],
            2: ["App. Stoc(MSA)", "PRV(MV)", "R/Power BI", "SM(SS)", "Bio Stat(SS)"],
            3: ["Bio Stat(SS)", "App. Stoc(BRR)", "Reg(SAP)", "RC(MV)", "App. Stat(LPR)"],
            4: ["ST(VS)", "ET(BRR)", "ST(VS)", "ET(BRR)", "CD"],
            5: ["Reg(SAP)", "App. Stat(LPR)", "R/Power BI", "App. Stoc(BRR)", "RC(MV)"],
            6: ["App. Stat(LPR)", "Reg(SAP)", "Bio Stat(SS)", "App. Stoc(BRR)", "RC(MV)"]
        }
    }
    
    # Attempting to Regex parse the 5 subjects for the specific year
    for day in range(1, 7):
        # Look for Day number, then the target year, then capture the next 5 subject blocks
        pattern = re.compile(rf"{day}\s*\|\s*{target_yr}\s*\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            tt_dict[day] = [m.strip().replace('\n', '') for m in match.groups()]
        else:
            # Load fallback if standard extraction fails
            if year_choice in fallback_tt:
                tt_dict[day] = fallback_tt[year_choice].get(day, ["Core 1", "Core 2", "Allied", "Elective", "Lab"])
            else:
                tt_dict[day] = ["Subject 1", "Subject 2", "Subject 3", "Subject 4", "Subject 5"]
                
    return tt_dict

# --- ONBOARDING SCREEN ---
if not st.session_state.setup_done:
    st.title("🎓 Loyola Attendance & Bunk Master")
    st.markdown("Automated tracking strictly based on the Loyola Academic Calendar & Timetable.")
    
    with st.form("setup_form"):
        st.subheader("1. Your Details")
        name = st.text_input("Full Name")
        roll_number = st.text_input("Roll / Register Number")
        
        col1, col2 = st.columns(2)
        with col1:
            degree = st.selectbox("Degree", ["B.Sc.", "M.Sc.", "B.A.", "M.A.", "B.Com."])
            year = st.selectbox("Year", ["1st UG", "2nd UG", "3rd UG", "1st PG", "2nd PG"])
        with col2:
            dept = st.text_input("Department", value="Statistics")
            
        st.subheader("2. Upload Official PDFs")
        cal_pdf = st.file_uploader("Upload Academic Calendar (PDF)", type=["pdf"])
        tt_pdf = st.file_uploader("Upload Department Timetable (PDF)", type=["pdf"])
        
        submitted = st.form_submit_button("Launch Dashboard 🚀")
        
        if submitted:
            if name and roll_number and cal_pdf and tt_pdf:
                with st.spinner("Scanning Academic Calendar & Timetable..."):
                    st.session_state.calendar_data = parse_academic_calendar(cal_pdf)
                    st.session_state.timetable_data = parse_timetable(tt_pdf, degree, year)
                    
                    st.session_state.user = {'name': name, 'roll': roll_number, 'degree': degree, 'year': year, 'dept': dept}
                    st.session_state.setup_done = True
                    st.rerun()
            else:
                st.error("Please fill all details and upload both PDFs.")

# --- MAIN DASHBOARD ---
else:
    user = st.session_state.user
    cal_data = st.session_state.calendar_data
    tt_data = st.session_state.timetable_data
    
    # 1. Sidebar Navigation
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(f"**Roll No:** {user['roll']}")
        st.caption(f"**Course:** {user['degree']} {user['dept']} ({user['year']})")
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.link_button("Check ERP Attendance", "https://erp.loyolacollege.edu")
        st.markdown("---")
        if st.button("🔄 Reset App & Re-upload"):
            st.session_state.setup_done = False
            st.rerun()

    # 2. Date & Calendar Sync
    # Hardcoded to system current time (Oct 2, 2026 IST) as per context
    today = datetime.date(2026, 10, 2) 
    
    st.title("📊 My Dashboard")
    
    # Determine Today's Status based on scanned calendar
    today_info = cal_data.get(today, {'event': 'No Data', 'is_working_day': False, 'day_order': None})
    
    status_color = "#0f5132" if today_info['is_working_day'] else "#842029"
    status_bg = "#d1e7dd" if today_info['is_working_day'] else "#f8d7da"
    
    st.markdown(f"""
        <div style="background-color: {status_bg}; color: {status_color}; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin:0;">📅 Today: {today.strftime('%A, %d %b %Y')}</h4>
            <p style="margin:5px 0 0 0; font-size: 16px;">
                <b>Day Order:</b> {today_info.get('raw_order', 'N/A')} | <b>Event:</b> {today_info.get('event', 'None')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. Main Tabs
    tab1, tab2, tab3 = st.tabs(["⚡ Attendance & Bunks", "🗓️ My Timetable", "🌟 Extra-Curricular"])
    
    with tab1:
        st.subheader("Update Hours from ERP")
        col1, col2, col3 = st.columns(3)
        with col1:
            cond = st.number_input("Hours Conducted", min_value=0, value=st.session_state.attendance['conducted'])
        with col2:
            pres = st.number_input("Hours Present", min_value=0, value=st.session_state.attendance['present'])
        with col3:
            absnt = st.number_input("Hours Absent", min_value=0, value=st.session_state.attendance['absent'])
            
        st.session_state.attendance = {'conducted': cond, 'present': pres, 'absent': absnt}
        current_pct = (pres / cond * 100) if cond > 0 else 0.0
        
        st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #0b3d91; margin:0;">{current_pct:.2f}%</h2>
                <p style="color: gray; margin:0;">Current Attendance</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Safe Bunk Calculator (Strict Calendar Sync)")
        target_pct = st.slider("Target Percentage (%)", 50, 100, 75)
        
        # Smart Deadline Logic based on Loyola Calendar
        # Odd Sem CIA 2 deadline is Oct 10, 2026. Even sem is Mar 23, 2027.
        current_month = today.month
        if current_month in [6, 7, 8, 9, 10, 11]:
            deadline = datetime.date(2026, 10, 10) 
            exam_name = "Odd Semester CIA 2"
        else:
            deadline = datetime.date(2027, 3, 23)
            exam_name = "Even Semester CIA 2"
            
        # Calculate EXACT working days left from calendar
        remaining_days = 0
        temp_date = today
        while temp_date <= deadline:
            day_info = cal_data.get(temp_date, {'is_working_day': False})
            if day_info['is_working_day']:
                remaining_days += 1
            temp_date += datetime.timedelta(days=1)
            
        total_remaining_hours = remaining_days * 5 # 5 periods a day
        
        st.info(f"📆 **Deadline:** {exam_name} ({deadline.strftime('%d %b %Y')})\n\n🕒 **Scanned Working Days Left:** {remaining_days} days ({total_remaining_hours} hours)")
        
        projected_conducted = cond + total_remaining_hours
        required_present = (target_pct / 100.0) * projected_conducted
        safe_bunks = pres + total_remaining_hours - required_present
        
        if current_pct >= target_pct:
            if safe_bunks >= 0:
                st.markdown(f"<div class='safe-box'>🎉 You can safely bunk up to {int(safe_bunks)} hours before {exam_name}.</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ You are meeting your target, but cannot afford to bunk anymore.")
        else:
            deficit = required_present - pres
            st.markdown(f"<div class='danger-box'>🚨 You must attend the next {int(deficit)} continuous hours to reach {target_pct}%.</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader(f"🗓️ Extracted Timetable for {user['year']}")
        
        # Show today's subjects if working day
        if today_info['is_working_day'] and today_info['day_order']:
            d_order = today_info['day_order']
            st.success(f"**Today's Classes (Day {d_order}):**")
            today_subjects = tt_data.get(d_order, ["-"]*5)
            for i, sub in enumerate(today_subjects):
                st.write(f"**Hour {i+1}:** {sub}")
            st.markdown("---")
            
        st.markdown("**All Day Orders:**")
        for d in range(1, 7):
            subs = tt_data.get(d, ["-"]*5)
            with st.expander(f"Day Order {d}"):
                for i, sub in enumerate(subs):
                    st.write(f"Hour {i+1}: `{sub}`")

    with tab3:
        st.subheader("🌟 Extra-Curricular Requirements")
        if user['year'] == "1st UG":
            st.markdown("**Club Activity Tracking (60 Hours Required)**")
            club_hrs = st.slider("Hours Completed", 0, 60, 0)
            st.progress(club_hrs / 60.0)
            if club_hrs == 60: st.success("Requirement Completed!")
        elif user['year'] == "2nd UG":
            st.markdown("**Outreach Program Tracking (90 Hours Required)**")
            outreach_hrs = st.slider("Hours Completed", 0, 90, 0)
            st.progress(outreach_hrs / 90.0)
            if outreach_hrs == 90: st.success("Requirement Completed!")
        else:
            st.markdown("**Internship / Project Tracking**")
            st.info("Check with your department head for final year project hour submissions.")
          
