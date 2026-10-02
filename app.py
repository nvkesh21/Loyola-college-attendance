import datetime
import re
import streamlit as st
import pandas as pd
import pdfplumber

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Loyola Attendance & Bunk Master",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM UI STYLING FOR A NATIVE APP FEEL ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background-color: #0b3d91;
        color: white;
        height: 45px;
    }
    .stat-card {
        background-color: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid #0b3d91;
        margin-bottom: 15px;
    }
    .safe-box { background-color: #d1e7dd; color: #0f5132; padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    .danger-box { background-color: #f8d7da; color: #842029; padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False
if 'attendance' not in st.session_state:
    st.session_state.attendance = {'conducted': 0, 'present': 0, 'absent': 0}
if 'calendar_data' not in st.session_state:
    st.session_state.calendar_data = {}

# --- PRECISION PDF PARSING ENGINE ---
def parse_academic_calendar(pdf_file):
    """Scans the calendar PDF using pdfplumber to map working days and events accurately."""
    cal_dict = {}
    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
                
    pattern = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})\s*\|?\s*[A-Z]{3}\s*\|?\s*([^\|]*?)\s*\|?\s*(Day\s*-\s*\d|W\d+\s*Day\s*-\s*\d|\*)?", re.IGNORECASE)
    
    for match in pattern.finditer(full_text):
        day, month, year, event, day_order = match.groups()
        date_obj = datetime.date(int(year), int(month), int(day))
        
        is_working_day = False
        parsed_order = None
        if day_order and "Day" in day_order:
            is_working_day = True
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

def get_timetable(year_choice):
    """Returns exact department subject mappings for B.Sc. Statistics[span_2](start_span)[span_2](end_span)."""
    timetable_mapping = {
        "1st UG": {
            1: ["PRV(MV)", "GL", "GE", "AR", "AR"],
            2: ["SM(SS)", "PRV(MV)", "GE", "FC", "SM(SS)"],
            3: ["App. Stoc (MSA)", "App. Stat (LPR)", "Reg. (SAP)", "R / Power BI", "Bio Stat (SS)"],
            4: ["ST (VS)", "App. Stoc (MSA)", "ET(BRR)", "R / Power BI", "CD"],
            5: ["PRV(MV)", "ET(BRR)", "SM(SS)", "AO", "GE"],
            6: ["SM(SS)", "GL", "GE", "PRV(MV)", "AR"]
        },
        "2nd UG": {
            1: ["ST (VS)", "FC", "ET(BRR)", "GE", "AO"],
            2: ["ET(BRR)", "GE", "CD", "AO", "AO"],
            3: ["Bio Stat (SS)", "App. Stoc (BRR)", "Reg. (SAP)", "RC (MV)", "App. Stat (LPR)"],
            4: ["ST (VS)", "App. Stat (LPR)", "ET(BRR)", "Reg. (SAP)", "CD"],
            5: ["ET(BRR)", "AO", "GL", "GE", "ST (VS)"],
            6: ["ET(BRR)", "ST (VS)", "GL", "GE", "AO"]
        },
        "3rd UG": {
            1: ["App. Stoc (MSA)", "App. Stat (LPR)", "Reg. (SAP)", "R / Power BI", "Bio Stat (SS)"],
            2: ["App. Stoc (MSA)", "PRV(MV)", "R / Power BI", "ME", "SM(SS)"],
            3: ["Bio Stat (SS)", "App. Stoc (BRR)", "Reg. (SAP)", "RC (MV)", "App. Stat (LPR)"],
            4: ["ST (VS)", "App. Stoc (MSA)", "ET(BRR)", "R / Power BI", "Bio Stat (VS)"],
            5: ["Reg. (SAP)", "App. Stat (LPR)", "R / Power BI", "App. Stoc (BRR)", "RC (MV)"],
            6: ["App. Stat (LPR)", "Reg. (SAP)", "Bio Stat (SS)", "App. Stoc (BRR)", "RC (MV)"]
        }
    }
    return timetable_mapping.get(year_choice, timetable_mapping["3rd UG"])

# --- ONBOARDING SCREEN ---
if not st.session_state.setup_done:
    st.title("🎓 Loyola Attendance & Bunk Master")
    st.markdown("Streamlined tracking built specifically for Loyola College students.")
    
    with st.form("setup_form"):
        st.subheader("1. Student Details")
        name = st.text_input("Full Name")
        roll_number = st.text_input("Roll / Register Number")
        
        col1, col2 = st.columns(2)
        with col1:
            degree = st.selectbox("Degree Level", ["B.Sc.", "M.Sc."])
            year = st.selectbox("Select Year", ["1st UG", "2nd UG", "3rd UG"])
        with col2:
            dept = st.text_input("Department", value="Statistics")
            
        st.subheader("2. Upload Official PDFs")
        cal_pdf = st.file_uploader("Upload Academic Calendar (PDF)", type=["pdf"])
        tt_pdf = st.file_uploader("Upload Department Timetable (PDF)", type=["pdf"])
        
        submitted = st.form_submit_button("Launch Dashboard 🚀")
        
        if submitted:
            if name and roll_number and cal_pdf and tt_pdf:
                with st.spinner("Processing official calendar and timetable..."):
                    st.session_state.calendar_data = parse_academic_calendar(cal_pdf)
                    st.session_state.user = {'name': name, 'roll': roll_number, 'degree': degree, 'year': year, 'dept': dept}
                    st.session_state.setup_done = True
                    st.rerun()
            else:
                st.error("Please fill in all details and upload both required PDFs.")

# --- MAIN APP DASHBOARD ---
else:
    user = st.session_state.user
    cal_data = st.session_state.calendar_data
    tt_data = get_timetable(user['year'])
    
    # --- SIDEBAR & LIVE SIMULATION OVERRIDE ---
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(f"**Roll No:** {user['roll']}")
        st.caption(f"**Course:** {user['degree']} {user['dept']} ({user['year']})")
        st.markdown("---")
        
        st.subheader("⚙️ Simulation / Date Override")
        use_simulation = st.checkbox("Manual Date & Day Order Override", value=False)
        
        # Default live context date (Oct 2, 2026)
        default_live_date = datetime.date(2026, 10, 2)
        
        if use_simulation:
            active_date = st.date_input("Override Date", value=default_live_date)
            active_day_order = st.selectbox("Override Day Order", [1, 2, 3, 4, 5, 6], index=0)
            active_event = "Manual Simulation Mode"
        else:
            active_date = default_live_date
            cal_match = cal_data.get(active_date, {'day_order': 1, 'event': 'Regular Working Day'})
            active_day_order = cal_match.get('day_order') or 1
            active_event = cal_match.get('event', 'Regular Working Day')
            
        st.markdown("---")
        st.markdown("### 📌 Quick Links")
        st.link_button("Official College Website", "https://www.loyolacollege.edu")
        st.markdown("---")
        if st.button("🔄 Reset App & Re-upload"):
            st.session_state.setup_done = False
            st.rerun()

    # --- TOP STATUS BANNER ---
    st.title("📊 Attendance Dashboard")
    
    st.markdown(f"""
        <div style="background-color: #d1e7dd; color: #0f5132; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin:0;">📅 Active Date: {active_date.strftime('%A, %d %b %Y')}</h4>
            <p style="margin:5px 0 0 0; font-size: 16px;">
                <b>Day Order:</b> Day - {active_day_order} | <b>Status / Event:</b> {active_event}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- INTERACTIVE TABS ---
    tab1, tab2, tab3 = st.tabs(["⚡ Attendance & Bunks", "🗓️ My Timetable", "🌟 Milestone Tracker"])
    
    with tab1:
        st.subheader("Update Hours from ERP")
        col1, col2, col3 = st.columns(3)
        with col1:
            cond = st.number_input("Total Hours Conducted", min_value=0, value=st.session_state.attendance['conducted'], step=1)
        with col2:
            pres = st.number_input("Hours Present", min_value=0, value=st.session_state.attendance['present'], step=1)
        with col3:
            absnt = st.number_input("Hours Absent", min_value=0, value=st.session_state.attendance['absent'], step=1)
            
        st.session_state.attendance = {'conducted': cond, 'present': pres, 'absent': absnt}
        current_pct = (pres / cond * 100) if cond > 0 else 0.0
        
        st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #0b3d91; margin:0;">{current_pct:.2f}%</h2>
                <p style="color: gray; margin:0;">Current Attendance Percentage</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Safe Bunk Calculator (Strict Calendar Sync)")
        target_pct = st.slider("Target Attendance Percentage (%)", 50, 100, 75)
        
        # Determine deadline based on active date benchmark (CIA 2 exams)[span_3](start_span)[span_3](end_span)[span_4](start_span)[span_4](end_span)
        current_month = active_date.month
        if current_month in [6, 7, 8, 9, 10, 11]:
            deadline = datetime.date(2026, 10, 10) # Odd Semester CIA 2 ends[span_5](start_span)[span_5](end_span)
            exam_name = "Odd Semester CIA 2"
        else:
            deadline = datetime.date(2027, 3, 23) # Even Semester CIA 2 ends[span_6](start_span)[span_6](end_span)
            exam_name = "Even Semester CIA 2"
            
        # Count exact working days from active date up to deadline using scanned calendar
        remaining_days = 0
        temp_date = active_date
        while temp_date <= deadline:
            day_info = cal_data.get(temp_date, {'is_working_day': False})
            if day_info['is_working_day']:
                remaining_days += 1
            temp_date += datetime.timedelta(days=1)
            
        total_remaining_hours = remaining_days * 5 
        
        st.info(f"📆 **Deadline Benchmark:** {exam_name} ({deadline.strftime('%d %b %Y')})[span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span)\n\n🕒 **Working Days Left:** {remaining_days} days (~{total_remaining_hours} hours)")
        
        projected_conducted = cond + total_remaining_hours
        required_present = (target_pct / 100.0) * projected_conducted
        safe_bunks = pres + total_remaining_hours - required_present
        
        if current_pct >= target_pct:
            if safe_bunks >= 0:
                st.markdown(f"<div class='safe-box'>🎉 You are safe! You can safely bunk up to {int(safe_bunks)} hours before {exam_name}.</div>", unsafe_allow_html=True)
                if safe_bunks > 5:
                    st.balloons() # Wow factor animation
            else:
                st.warning("⚠️ You are meeting your target right now, but cannot afford any more bunks.")
        else:
            deficit = required_present - pres
            st.markdown(f"<div class='danger-box'>🚨 Attendance below target! You need to attend the next {int(deficit)} continuous hours to recover to {target_pct}%.</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader(f"🗓️ Timetable Subjects for {user['year']} ({user['dept']})")
        
        st.success(f"**Active Subjects for Day Order {active_day_order}:**")
        current_subjects = tt_data.get(active_day_order, ["-"]*5)
        for i, sub in enumerate(current_subjects):
            st.write(f"**Hour {i+1}:** `{sub}`")
        st.markdown("---")
            
        st.markdown("**Complete Day Order Subject Reference:**")
        for d in range(1, 7):
            subs = tt_data.get(d, ["-"]*5)
            with st.expander(f"Day Order {d}"):
                for i, sub in enumerate(subs):
                    st.write(f"Hour {i+1}: `{sub}`")

    with tab3:
        st.subheader("🌟 Extra-Curricular & Milestone Trackers")
        if user['year'] == "1st UG":
            st.markdown("**Club Activity Tracking (60 Hours Required)**")
            club_hrs = st.slider("Completed Club Hours", 0, 60, 0)
            st.progress(club_hrs / 60.0)
            if club_hrs == 60: 
                st.success("🎉 Club Activity Requirement Completed!")
                st.balloons()
        elif user['year'] == "2nd UG":
            st.markdown("**Outreach Program Tracking (90 Hours Required)**")
            outreach_hrs = st.slider("Completed Outreach Hours", 0, 90, 0)
            st.progress(outreach_hrs / 90.0)
            if outreach_hrs == 90: 
                st.success("🎉 Outreach Requirement Completed!")
                st.balloons()
        else:
            st.markdown("**Internship / Project Hour Submissions**")
            st.info("Check with your department head for final year project milestone updates and hour logs.")
                  
