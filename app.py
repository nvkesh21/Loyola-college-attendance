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

# --- INITIALIZE SESSION STATE & URL QUERY PARAMS PERSISTENCE ---
query_params = st.query_params

if 'setup_done' not in st.session_state:
    if "roll" in query_params and "year" in query_params:
        st.session_state.setup_done = True
        st.session_state.user = {
            'name': query_params.get("name", "Student"),
            'roll': query_params.get("roll", ""),
            'year': query_params.get("year", "1st UG"),
            'dept': 'Statistics'
        }
        st.session_state.attendance = {
            'conducted': int(query_params.get("cond", 0)),
            'present': int(query_params.get("pres", 0)),
            'absent': int(query_params.get("absnt", 0))
        }
    else:
        st.session_state.setup_done = False

if 'attendance' not in st.session_state:
    st.session_state.attendance = {'conducted': 0, 'present': 0, 'absent': 0}

# --- OFFICIAL WORKING DAYS MAPPING (Excludes CIAs and Semester Exams) ---
def get_official_working_days():
    """Maps ONLY regular working days. CIAs, Exams, and Holidays are excluded."""
    wd = {}
    
    def work(dt, order, ev):
        wd[dt] = {'day_order': order, 'event': ev}

    # --- ODD SEMESTER WORKING DAYS (June 2026 - October 2026, excluding CIAs/Exams) ---
    # June 2026
    work(datetime.date(2026, 6, 15), 1, "College Reopens / Inaugural Prayer Service (Day - 1)")
    work(datetime.date(2026, 6, 16), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 6, 17), 3, "Registration Begins for Repeaters (Day - 3)")
    work(datetime.date(2026, 6, 18), 4, "ODD Semester Fee Payment Begins (Day - 4)")
    work(datetime.date(2026, 6, 19), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2026, 6, 20), 6, "LSC Election (Working Saturday - Day - 6)")
    work(datetime.date(2026, 6, 22), 1, "IQAC Meeting (Day - 1)")
    work(datetime.date(2026, 6, 23), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 6, 24), 3, "Student Induction Programme (Day - 3)")
    work(datetime.date(2026, 6, 25), 4, "Student Induction Programme (Day - 4)")
    work(datetime.date(2026, 6, 27), 5, "Student Induction Programme (Working Saturday - Day - 5)")
    work(datetime.date(2026, 6, 29), 6, "Classes Begin for I PG / Bridge Course (Day - 6)")
    work(datetime.date(2026, 6, 30), 1, "I UG English Bridge Course (Day - 1)")

    # July 2026
    work(datetime.date(2026, 7, 1), 2, "I UG English Bridge Course (Day - 2)")
    work(datetime.date(2026, 7, 2), 3, "I UG English Bridge Course (Day - 3)")
    work(datetime.date(2026, 7, 3), 4, "I UG English Bridge Course / Holy Mass (Day - 4)")
    work(datetime.date(2026, 7, 6), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2026, 7, 7), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2026, 7, 8), 1, "Inauguration of LSC (Day - 1)")
    work(datetime.date(2026, 7, 9), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 7, 10), 3, "Last date for Registration of Repeaters (Day - 3)")
    work(datetime.date(2026, 7, 13), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 7, 14), 5, "Academic & Administrative Audit (Day - 5)")
    work(datetime.date(2026, 7, 15), 6, "Academic & Administrative Audit (Day - 6)")
    work(datetime.date(2026, 7, 16), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 7, 17), 2, "Semester Fee Payment without fine (Day - 2)")
    work(datetime.date(2026, 7, 18), 3, "Working Saturday (Day - 3)")
    work(datetime.date(2026, 7, 20), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 7, 21), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2026, 7, 22), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2026, 7, 23), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 7, 24), 2, "Semester Fee Payment with fine (Day - 2)")
    work(datetime.date(2026, 7, 27), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 7, 28), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 7, 29), 5, "Internal Arrear Registration (Day - 5)")
    work(datetime.date(2026, 7, 30), 6, "Homage to St. Ignatius of Loyola (Day - 6)")

    # August 2026 (First CIA excluded)
    work(datetime.date(2026, 8, 3), 1, "Online Registration for Semester Exams Begin (Day - 1)")
    work(datetime.date(2026, 8, 4), 2, "Springboard Leadership Program (Day - 2)")
    work(datetime.date(2026, 8, 5), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 8, 6), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 8, 7), 5, "Holy Mass (Day - 5)")
    work(datetime.date(2026, 8, 10), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2026, 8, 19), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 8, 20), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 8, 21), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 8, 22), 4, "98th Graduation Day (Working Saturday - Day - 4)")
    work(datetime.date(2026, 8, 24), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2026, 8, 25), 6, "FDP for Academic Staff (Day - 6)")
    work(datetime.date(2026, 8, 27), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 8, 28), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 8, 29), 3, "Parent-Teacher Meeting (Working Saturday - Day - 3)")
    work(datetime.date(2026, 8, 31), 4, "Bertram Tournament Valediction (Day - 4)")

    # September 2026
    work(datetime.date(2026, 9, 1), 5, "Springboard Leadership Program (Day - 5)")
    work(datetime.date(2026, 9, 2), 6, "Holy Mass (Day - 6)")
    work(datetime.date(2026, 9, 3), 1, "Ovations 2026 - Inauguration (Day - 1)")
    work(datetime.date(2026, 9, 7), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 9, 9), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 9, 10), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 9, 11), 5, "Open Forum for Students (Day - 5)")
    work(datetime.date(2026, 9, 15), 6, "Online Registration without fine (Day - 6)")
    work(datetime.date(2026, 9, 16), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 9, 17), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 9, 18), 3, "Ovations 2026 (Day - 3)")
    work(datetime.date(2026, 9, 19), 4, "Ovations 2026 (Working Saturday - Day - 4)")
    work(datetime.date(2026, 9, 21), 5, "Online Registration with fine (Day - 5)")
    work(datetime.date(2026, 9, 22), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2026, 9, 23), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 9, 24), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 9, 25), 3, "Corpus Christi Celebration (Day - 3)")
    work(datetime.date(2026, 9, 28), 4, "Mentoring for III UG (Day - 4)")
    work(datetime.date(2026, 9, 29), 5, "Mentoring for II UG (Day - 5)")
    work(datetime.date(2026, 9, 30), 6, "Mentoring for I UG (Day - 6)")

    # October 2026 (Second CIA excluded)
    work(datetime.date(2026, 10, 1), 1, "Mentoring for I & II PG / Staff Assessment (Day - 1)")
    work(datetime.date(2026, 10, 12), 2, "Release of Retest List / Practicals (Day - 2)")
    work(datetime.date(2026, 10, 13), 3, "Retest / Practicals (Day - 3)")
    work(datetime.date(2026, 10, 14), 4, "Retest / Practicals (Day - 4)")
    work(datetime.date(2026, 10, 15), 5, "Retest / Practicals (Day - 5)")
    work(datetime.date(2026, 10, 16), 6, "Practical Examination (Day - 6)")
    work(datetime.date(2026, 10, 17), 1, "General Staff Meeting & Last Signing Day (Working Saturday - Day - 1)")

    # --- EVEN SEMESTER WORKING DAYS (November 2026 - April 2027, excluding CIAs/Exams) ---
    work(datetime.date(2026, 11, 16), 1, "College Reopens for EVEN Semester (Day - 1)")
    work(datetime.date(2026, 11, 17), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 11, 18), 3, "Registration Begins for Repeaters (Day - 3)")
    work(datetime.date(2026, 11, 19), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 11, 20), 5, "Fee Payment Begins / Holy Mass (Day - 5)")
    work(datetime.date(2026, 11, 23), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2026, 11, 24), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2026, 11, 25), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 11, 26), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 11, 27), 4, "IQAC Meeting (Day - 4)")
    work(datetime.date(2026, 11, 30), 5, "Regular Working Day (Day - 5)")

    work(datetime.date(2026, 12, 1), 6, "Springboard Leadership Program (Day - 6)")
    work(datetime.date(2026, 12, 2), 1, "Internal Arrear Registration Begins (Day - 1)")
    work(datetime.date(2026, 12, 3), 2, "Feast of St. Francis Xavier - Holy Mass (Day - 2)")
    work(datetime.date(2026, 12, 4), 3, "Department Festival Day - 1 (Day - 3)")
    work(datetime.date(2026, 12, 5), 4, "Department Festival Day - 2 (Day - 4)")
    work(datetime.date(2026, 12, 7), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2026, 12, 8), 6, "Immaculate Conception of Our Lady (Day - 6)")
    work(datetime.date(2026, 12, 9), 1, "III UG Internship Begins (Day - 1)")
    work(datetime.date(2026, 12, 10), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 12, 11), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 12, 14), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2026, 12, 15), 5, "Semester Fee Payment without fine (Day - 5)")
    work(datetime.date(2026, 12, 16), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2026, 12, 17), 1, "Registration of Repeaters Ends (Day - 1)")
    work(datetime.date(2026, 12, 18), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2026, 12, 21), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2026, 12, 22), 4, "Christmas Celebration (Day - 4)")

    work(datetime.date(2027, 1, 4), 5, "College Reopens after Christmas Vacation (Day - 5)")
    work(datetime.date(2027, 1, 5), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2027, 1, 6), 1, "Training Programme for Staff (Day - 1)")
    work(datetime.date(2027, 1, 7), 2, "Semester Fee Payment with fine (Day - 2)")
    work(datetime.date(2027, 1, 8), 3, "Holy Mass / IQAC Meeting (Day - 3)")
    work(datetime.date(2027, 1, 9), 4, "Working Saturday (Day - 4)")
    work(datetime.date(2027, 1, 11), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2027, 1, 12), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2027, 1, 13), 1, "III UG Join Classes / Pongal Celebration (Day - 1)")
    work(datetime.date(2027, 1, 14), 2, "Bhogi (Day - 2)")
    work(datetime.date(2027, 1, 18), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2027, 1, 19), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2027, 1, 29), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2027, 1, 30), 6, "Parent-Teacher Meeting (Working Saturday - Day - 6)")

    work(datetime.date(2027, 2, 1), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2027, 2, 2), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2027, 2, 3), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2027, 2, 4), 4, "Feast of St. John De Britto (Day - 4)")
    work(datetime.date(2027, 2, 5), 5, "Online Exam Registration Begins (Day - 5)")
    work(datetime.date(2027, 2, 6), 6, "Sports Day (Working Saturday - Day - 6)")
    work(datetime.date(2027, 2, 8), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2027, 2, 9), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2027, 2, 10), 3, "Ash Wednesday (Day - 3)")
    work(datetime.date(2027, 2, 11), 4, "Feast of Our Lady of Lourdes (Day - 4)")
    work(datetime.date(2027, 2, 12), 5, "Seminar for Academic Staff (Day - 5)")
    work(datetime.date(2027, 2, 13), 6, "Seminar for Academic Staff (Working Saturday - Day - 6)")
    work(datetime.date(2027, 2, 15), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2027, 2, 16), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2027, 2, 17), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2027, 2, 18), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2027, 2, 19), 5, "Open Forum for Students (Day - 5)")
    work(datetime.date(2027, 2, 22), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2027, 2, 23), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2027, 2, 24), 2, "Springboard Leadership Program (Day - 2)")
    work(datetime.date(2027, 2, 25), 3, "Regular Working Day (Day - 3)")
    work(datetime.date(2027, 2, 26), 4, "Loyola Research Day (Day - 4)")

    work(datetime.date(2027, 3, 1), 5, "Online Exam Registration without fine (Day - 5)")
    work(datetime.date(2027, 3, 2), 6, "Regular Working Day (Day - 6)")
    work(datetime.date(2027, 3, 3), 1, "LSC Valedictory (Day - 1)")
    work(datetime.date(2027, 3, 4), 2, "Regular Working Day (Day - 2)")
    work(datetime.date(2027, 3, 5), 3, "Holy Mass (Day - 3)")
    work(datetime.date(2027, 3, 8), 4, "International Women's Day (Day - 4)")
    work(datetime.date(2027, 3, 9), 5, "Regular Working Day (Day - 5)")
    work(datetime.date(2027, 3, 11), 6, "Online Exam Registration with fine (Day - 6)")
    work(datetime.date(2027, 3, 12), 1, "Regular Working Day (Day - 1)")
    work(datetime.date(2027, 3, 13), 2, "College Day (Working Saturday - Day - 2)")
    work(datetime.date(2027, 3, 15), 3, "Exit Poll / Staff Assessment (Day - 3)")
    work(datetime.date(2027, 3, 16), 4, "Regular Working Day (Day - 4)")
    work(datetime.date(2027, 3, 24), 5, "Release of Retest List (Day - 5)")
    work(datetime.date(2027, 3, 29), 6, "Retest / Practicals (Day - 6)")
    work(datetime.date(2027, 3, 30), 1, "Retest / Practicals (Day - 1)")
    work(datetime.date(2027, 3, 31), 2, "Retest / Practicals (Day - 2)")

    work(datetime.date(2027, 4, 1), 3, "General Staff Meeting / Practicals (Day - 3)")

    return wd

# --- HELPER: GET CALENDAR STATUS FOR ANY DATE ---
def check_date_status(dt):
    working_days = get_official_working_days()
    if dt in working_days:
        return {
            'is_working_day': True,
            'day_order': working_days[dt]['day_order'],
            'event': working_days[dt]['event']
        }
    else:
        return {
            'is_working_day': False,
            'day_order': None,
            'event': 'Holiday / Exam / CIA Period (No Day Order)'
        }

# --- 100% RELIABLE HARDCODED STATISTICS TIMETABLES ---
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

# --- ONBOARDING SCREEN ---
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
                
                st.query_params["name"] = name
                st.query_params["roll"] = roll_number
                st.query_params["year"] = year
                st.query_params["cond"] = "0"
                st.query_params["pres"] = "0"
                st.query_params["absnt"] = "0"
                
                st.session_state.setup_done = True
                st.rerun()
            else:
                st.error("Please fill in your name and roll number.")

# --- MAIN APP DASHBOARD ---
else:
    user = st.session_state.user
    tt_data = get_statistics_timetable(user['year'])
    
    # --- SIDEBAR & SIMULATION OVERRIDE ---
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(f"**Roll No:** {user['roll']}")
        st.caption(f"**Course:** B.Sc. Statistics ({user['year']})")
        st.markdown("---")
        
        st.subheader("⚙️ Simulation / Date Override")
        use_simulation = st.checkbox("Manual Date & Day Order Override", value=False)
        
        default_live_date = datetime.date.today()
        
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
        st.markdown("### 📌 Quick Links")
        st.link_button("Official College Website", "https://www.loyolacollege.edu")
        st.markdown("---")
        if st.button("🔄 Reset Profile"):
            st.query_params.clear()
            st.session_state.setup_done = False
            st.rerun()

    # --- TOP STATUS BANNER ---
    st.title("📊 Statistics Attendance Dashboard")
    
    # Standard if-else block 
