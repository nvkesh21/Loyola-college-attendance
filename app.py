import datetime
import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Loyola Statistics Bunk Master",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM UI STYLING ---
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

# --- INITIALIZE SESSION STATE SAFELY ---
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False

if 'attendance' not in st.session_state:
    st.session_state.attendance = {'conducted': 0, 'present': 0, 'absent': 0}

if 'user' not in st.session_state:
    st.session_state.user = {'name': '', 'roll': '', 'year': '1st UG', 'dept': 'Statistics'}

# --- OFFICIAL WORKING DAYS MAPPING (Excludes CIAs, Exams, Weekends, and Holidays) ---
def get_official_working_days():
    wd = {}
    def work(dt, order, ev):
        wd[dt] = {'day_order': order, 'event': ev}

    # --- ODD SEMESTER WORKING DAYS (June 2026 - October 2026) ---
    work(datetime.date(2026, 6, 15), 1, "College Reopens / Inaugural Prayer Service (Day - 1)")[span_0](start_span)[span_0](end_span)
    work(datetime.date(2026, 6, 16), 2, "Regular Working Day (Day - 2)")[span_1](start_span)[span_1](end_span)
    work(datetime.date(2026, 6, 17), 3, "Registration Begins for Repeaters (Day - 3)")[span_2](start_span)[span_2](end_span)
    work(datetime.date(2026, 6, 18), 4, "ODD Semester Fee Payment Begins (Day - 4)")[span_3](start_span)[span_3](end_span)
    work(datetime.date(2026, 6, 19), 5, "Regular Working Day (Day - 5)")[span_4](start_span)[span_4](end_span)
    work(datetime.date(2026, 6, 20), 6, "LSC Election (Working Saturday - Day - 6)")[span_5](start_span)[span_5](end_span)
    work(datetime.date(2026, 6, 22), 1, "IQAC Meeting (Day - 1)")[span_6](start_span)[span_6](end_span)
    work(datetime.date(2026, 6, 23), 2, "Regular Working Day (Day - 2)")[span_7](start_span)[span_7](end_span)
    work(datetime.date(2026, 6, 24), 3, "Student Induction Programme (Day - 3)")[span_8](start_span)[span_8](end_span)
    work(datetime.date(2026, 6, 25), 4, "Student Induction Programme (Day - 4)")[span_9](start_span)[span_9](end_span)
    work(datetime.date(2026, 6, 27), 5, "Student Induction Programme (Working Saturday - Day - 5)")[span_10](start_span)[span_10](end_span)
    work(datetime.date(2026, 6, 29), 6, "Classes Begin for I PG / Bridge Course (Day - 6)")[span_11](start_span)[span_11](end_span)
    work(datetime.date(2026, 6, 30), 1, "I UG English Bridge Course (Day - 1)")[span_12](start_span)[span_12](end_span)

    work(datetime.date(2026, 7, 1), 2, "I UG English Bridge Course (Day - 2)")[span_13](start_span)[span_13](end_span)
    work(datetime.date(2026, 7, 2), 3, "I UG English Bridge Course (Day - 3)")[span_14](start_span)[span_14](end_span)
    work(datetime.date(2026, 7, 3), 4, "I UG English Bridge Course / Holy Mass (Day - 4)")[span_15](start_span)[span_15](end_span)
    work(datetime.date(2026, 7, 6), 5, "Regular Working Day (Day - 5)")[span_16](start_span)[span_16](end_span)
    work(datetime.date(2026, 7, 7), 6, "Regular Working Day (Day - 6)")[span_17](start_span)[span_17](end_span)
    work(datetime.date(2026, 7, 8), 1, "Inauguration of LSC (Day - 1)")[span_18](start_span)[span_18](end_span)
    work(datetime.date(2026, 7, 9), 2, "Regular Working Day (Day - 2)")[span_19](start_span)[span_19](end_span)
    work(datetime.date(2026, 7, 10), 3, "Last date for Registration of Repeaters (Day - 3)")[span_20](start_span)[span_20](end_span)
    work(datetime.date(2026, 7, 13), 4, "Regular Working Day (Day - 4)")[span_21](start_span)[span_21](end_span)
    work(datetime.date(2026, 7, 14), 5, "Academic & Administrative Audit (Day - 5)")[span_22](start_span)[span_22](end_span)
    work(datetime.date(2026, 7, 15), 6, "Academic & Administrative Audit (Day - 6)")[span_23](start_span)[span_23](end_span)
    work(datetime.date(2026, 7, 16), 1, "Regular Working Day (Day - 1)")[span_24](start_span)[span_24](end_span)
    work(datetime.date(2026, 7, 17), 2, "Semester Fee Payment without fine (Day - 2)")[span_25](start_span)[span_25](end_span)
    work(datetime.date(2026, 7, 18), 3, "Working Saturday (Day - 3)")[span_26](start_span)[span_26](end_span)
    work(datetime.date(2026, 7, 20), 4, "Regular Working Day (Day - 4)")[span_27](start_span)[span_27](end_span)
    work(datetime.date(2026, 7, 21), 5, "Regular Working Day (Day - 5)")[span_28](start_span)[span_28](end_span)
    work(datetime.date(2026, 7, 22), 6, "Regular Working Day (Day - 6)")[span_29](start_span)[span_29](end_span)
    work(datetime.date(2026, 7, 23), 1, "Regular Working Day (Day - 1)")[span_30](start_span)[span_30](end_span)
    work(datetime.date(2026, 7, 24), 2, "Semester Fee Payment with fine (Day - 2)")[span_31](start_span)[span_31](end_span)
    work(datetime.date(2026, 7, 27), 3, "Regular Working Day (Day - 3)")[span_32](start_span)[span_32](end_span)
    work(datetime.date(2026, 7, 28), 4, "Regular Working Day (Day - 4)")[span_33](start_span)[span_33](end_span)
    work(datetime.date(2026, 7, 29), 5, "Internal Arrear Registration (Day - 5)")[span_34](start_span)[span_34](end_span)
    work(datetime.date(2026, 7, 30), 6, "Homage to St. Ignatius of Loyola (Day - 6)")[span_35](start_span)[span_35](end_span)

    work(datetime.date(2026, 8, 3), 1, "Online Registration for Semester Exams Begin (Day - 1)")[span_36](start_span)[span_36](end_span)
    work(datetime.date(2026, 8, 4), 2, "Springboard Leadership Program (Day - 2)")[span_37](start_span)[span_37](end_span)
    work(datetime.date(2026, 8, 5), 3, "Regular Working Day (Day - 3)")[span_38](start_span)[span_38](end_span)
    work(datetime.date(2026, 8, 6), 4, "Regular Working Day (Day - 4)")[span_39](start_span)[span_39](end_span)
    work(datetime.date(2026, 8, 7), 5, "Holy Mass (Day - 5)")[span_40](start_span)[span_40](end_span)
    work(datetime.date(2026, 8, 10), 6, "Regular Working Day (Day - 6)")[span_41](start_span)[span_41](end_span)
    work(datetime.date(2026, 8, 19), 1, "Regular Working Day (Day - 1)")[span_42](start_span)[span_42](end_span)
    work(datetime.date(2026, 8, 20), 2, "Regular Working Day (Day - 2)")[span_43](start_span)[span_43](end_span)
    work(datetime.date(2026, 8, 21), 3, "Regular Working Day (Day - 3)")[span_44](start_span)[span_44](end_span)
    work(datetime.date(2026, 8, 22), 4, "98th Graduation Day (Working Saturday - Day - 4)")[span_45](start_span)[span_45](end_span)
    work(datetime.date(2026, 8, 24), 5, "Regular Working Day (Day - 5)")[span_46](start_span)[span_46](end_span)
    work(datetime.date(2026, 8, 25), 6, "FDP for Academic Staff (Day - 6)")[span_47](start_span)[span_47](end_span)
    work(datetime.date(2026, 8, 27), 1, "Regular Working Day (Day - 1)")[span_48](start_span)[span_48](end_span)
    work(datetime.date(2026, 8, 28), 2, "Regular Working Day (Day - 2)")[span_49](start_span)[span_49](end_span)
    work(datetime.date(2026, 8, 29), 3, "Parent-Teacher Meeting (Working Saturday - Day - 3)")[span_50](start_span)[span_50](end_span)
    work(datetime.date(2026, 8, 31), 4, "Bertram Tournament Valediction (Day - 4)")[span_51](start_span)[span_51](end_span)

    work(datetime.date(2026, 9, 1), 5, "Springboard Leadership Program (Day - 5)")[span_52](start_span)[span_52](end_span)
    work(datetime.date(2026, 9, 2), 6, "Holy Mass (Day - 6)")[span_53](start_span)[span_53](end_span)
    work(datetime.date(2026, 9, 3), 1, "Ovations 2026 - Inauguration (Day - 1)")[span_54](start_span)[span_54](end_span)
    work(datetime.date(2026, 9, 7), 2, "Regular Working Day (Day - 2)")[span_55](start_span)[span_55](end_span)
    work(datetime.date(2026, 9, 9), 3, "Regular Working Day (Day - 3)")[span_56](start_span)[span_56](end_span)
    work(datetime.date(2026, 9, 10), 4, "Regular Working Day (Day - 4)")[span_57](start_span)[span_57](end_span)
    work(datetime.date(2026, 9, 11), 5, "Open Forum for Students (Day - 5)")[span_58](start_span)[span_58](end_span)
    work(datetime.date(2026, 9, 15), 6, "Online Registration without fine (Day - 6)")[span_59](start_span)[span_59](end_span)
    work(datetime.date(2026, 9, 16), 1, "Regular Working Day (Day - 1)")[span_60](start_span)[span_60](end_span)
    work(datetime.date(2026, 9, 17), 2, "Regular Working Day (Day - 2)")[span_61](start_span)[span_61](end_span)
    work(datetime.date(2026, 9, 18), 3, "Ovations 2026 (Day - 3)")[span_62](start_span)[span_62](end_span)
    work(datetime.date(2026, 9, 19), 4, "Ovations 2026 (Working Saturday - Day - 4)")[span_63](start_span)[span_63](end_span)
    work(datetime.date(2026, 9, 21), 5, "Online Registration with fine (Day - 5)")[span_64](start_span)[span_64](end_span)
    work(datetime.date(2026, 9, 22), 6, "Regular Working Day (Day - 6)")[span_65](start_span)[span_65](end_span)
    work(datetime.date(2026, 9, 23), 1, "Regular Working Day (Day - 1)")[span_66](start_span)[span_66](end_span)
    work(datetime.date(2026, 9, 24), 2, "Regular Working Day (Day - 2)")[span_67](start_span)[span_67](end_span)
    work(datetime.date(2026, 9, 25), 3, "Corpus Christi Celebration (Day - 3)")[span_68](start_span)[span_68](end_span)
    work(datetime.date(2026, 9, 28), 4, "Mentoring for III UG (Day - 4)")[span_69](start_span)[span_69](end_span)
    work(datetime.date(2026, 9, 29), 5, "Mentoring for II UG (Day - 5)")[span_70](start_span)[span_70](end_span)
    work(datetime.date(2026, 9, 30), 6, "Mentoring for I UG (Day - 6)")[span_71](start_span)[span_71](end_span)

    work(datetime.date(2026, 10, 1), 1, "Mentoring for I & II PG / Staff Assessment (Day - 1)")[span_72](start_span)[span_72](end_span)
    work(datetime.date(2026, 10, 12), 2, "Release of Retest List / Practicals (Day - 2)")[span_73](start_span)[span_73](end_span)
    work(datetime.date(2026, 10, 13), 3, "Retest / Practicals (Day - 3)")[span_74](start_span)[span_74](end_span)
    work(datetime.date(2026, 10, 14), 4, "Retest / Practicals (Day - 4)")[span_75](start_span)[span_75](end_span)
    work(datetime.date(2026, 10, 15), 5, "Retest / Practicals (Day - 5)")[span_76](start_span)[span_76](end_span)
    work(datetime.date(2026, 10, 16), 6, "Practical Examination (Day - 6)")[span_77](start_span)[span_77](end_span)
    work(datetime.date(2026, 10, 17), 1, "General Staff Meeting & Last Signing Day (Working Saturday - Day - 1)")[span_78](start_span)[span_78](end_span)

    return wd

def check_date_status(dt):
    working_days = get_official_working_days()
    if dt in working_days:
        return {'is_working_day': True, 'day_order': working_days[dt]['day_order'], 'event': working_days[dt]['event']}
    else:
        return {'is_working_day': False, 'day_order': None, 'event': 'Holiday / Exam / CIA Period (No Day Order)'}

def get_statistics_timetable(year_choice):
    timetable_data = {
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
    return timetable_data.get(year_choice, timetable_data["1st UG"])

# --- ONBOARDING FORM SCREEN ---
if not st.session_state.setup_done:
    st.title("📊 Loyola Statistics Bunk Master")
    st.markdown("Exclusive attendance & schedule tracker for B.Sc. Statistics students.")
    
    with st.form("setup_form"):
        st.subheader("Student Details")
        name = st.text_input("Full Name")
        roll_number = st.text_input("Roll / Register Number")
        year = st.selectbox("Select Your Year", ["1st UG", "2nd UG", "3rd UG"])
        
        submitted = st.form_submit_button("Launch Dashboard 🚀")
        
        if submitted:
            if name and roll_number:
                st.session_state.user = {'name': name, 'roll': roll_number, 'year': year, 'dept': 'Statistics'}
                st.session_state.setup_done = True
                st.rerun()
            else:
                st.error("Please fill in your name and roll number.")

# --- MAIN APP DASHBOARD ---
else:
    user = st.session_state.user
    tt_data = get_statistics_timetable(user['year'])
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(f"**Roll No:** {user['roll']}")
        st.caption(f"**Course:** B.Sc. Statistics ({user['year']})")
        st.markdown("---")
        
        st.subheader("⚙️ Simulation / Date Override")
        use_simulation = st.checkbox("Manual Date & Day Order Override", value=False)
        
        default_live_date = datetime.date(2026, 6, 15) # Default to opening day so it shows classes immediately
        
        if use_simulation:
            active_date = st.date_input("Override Date", value=default_live_date)
            active_day_order = st.selectbox("Override Day Order", [1, 2, 3, 4, 5, 6], index=0)
            is_working = True
            active_event = "Manual Simulation Mode"
        else:
            active_date = default_live_date
            status = check_date_status(active_date)
            is_working = status['is_working_day']
            active_day_order = status['day_order'] or 1
            active_event = status['event']
            
        st.markdown("---")
        if st.button("🔄 Reset Profile"):
            st.session_state.setup_done = False
            st.rerun()

    st.title("📊 Statistics Attendance Dashboard")
    
    if is_working:
        banner_bg = "#d1e7dd"
        banner_fg = "#0f5132"
    else:
        banner_bg = "#f8d7da"
        banner_fg = "#842029"
    
    st.markdown(f"""
        <div style="background-color: {banner_bg}; color: {banner_fg}; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin:0;">📅 Active Date: {active_date.strftime('%A, %d %b %Y')}</h4>
            <p style="margin:5px 0 0 0; font-size: 16px;">
                <b>Status:</b> {active_event}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
        
        st.markdown("### 🎯 Safe Bunk Calculator")
        target_pct = st.slider("Target Attendance Percentage (%)", 50, 100, 75)
        
        deadline = datetime.date(2026, 10, 10)
        exam_name = "Odd Semester CIA 2 / Exams"
            
        remaining_days = 0
        temp_date = active_date
        working_days_dict = get_official_working_days()
        while temp_date <= deadline:
            if temp_date in working_days_dict:
                remaining_days += 1
            temp_date += datetime.timedelta(days=1)
            
        total_remaining_hours = remaining_days * 5 
        
        st.info(f"📆 **Deadline Benchmark:** {exam_name} ({deadline.strftime('%d %b %Y')})\n\n🕒 **Working Days Left:** {remaining_days} days (~{total_remaining_hours} hours)")
        
        projected_conducted = cond + total_remaining_hours
        required_present = (target_pct / 100.0) * projected_conducted
        safe_bunks = pres + total_remaining_hours - required_present
        
        if current_pct >= target_pct:
            if safe_bunks >= 0:
                st.markdown(f"<div class='safe-box'>🎉 You are safe! You can safely bunk up to {int(safe_bunks)} hours before {exam_name}.</div>", unsafe_allow_html=True)
                if safe_bunks > 5:
                    st.balloons()
            else:
                st.warning("⚠️ You are meeting your target right now, but cannot afford any more bunks.")
        else:
            deficit = required_present - pres
            st.markdown(f"<div class='danger-box'>🚨 Attendance below target! You need to attend the next {int(deficit)} continuous hours to reach {target_pct}%.</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader(f"🗓️ Timetable Subjects for B.Sc. Statistics ({user['year']})")
        
        if is_working:
            st.success(f"**Active Subjects for Day Order {active_day_order}:**")
            current_subjects = tt_data.get(active_day_order, ["-"]*5)
            for i, sub in enumerate(current_subjects):
                st.write(f"**Hour {i+1}:** `{sub}`")
        else:
            st.warning("Today is a holiday, CIA test, or exam period. No regular classes scheduled!")
            
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
            st.markdown("**
