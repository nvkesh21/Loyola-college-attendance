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

    # July 2026
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

    # August 2026 (First CIA excluded)
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

    # September 2026
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

    # October 2026 (Second CIA excluded)
    work(datetime.date(2026, 10, 1), 1, "Mentoring for I & II PG / Staff Assessment (Day - 1)")[span_72](start_span)[span_72](end_span)
    work(datetime.date(2026, 10, 12), 2, "Release of Retest List / Practicals (Day - 2)")[span_73](start_span)[span_73](end_span)
    work(datetime.date(2026, 10, 13), 3, "Retest / Practicals (Day - 3)")[span_74](start_span)[span_74](end_span)
    work(datetime.date(2026, 10, 14), 4, "Retest / Practicals (Day - 4)")[span_75](start_span)[span_75](end_span)
    work(datetime.date(2026, 10, 15), 5, "Retest / Practicals (Day - 5)")[span_76](start_span)[span_76](end_span)
    work(datetime.date(2026, 10, 16), 6, "Practical Examination (Day - 6)")[span_77](start_span)[span_77](end_span)
    work(datetime.date(2026, 10, 17), 1, "General Staff Meeting & Last Signing Day (Working Saturday - Day - 1)")[span_78](start_span)[span_78](end_span)

    # --- EVEN SEMESTER WORKING DAYS (November 2026 - April 2027, excluding CIAs/Exams) ---
    work(datetime.date(2026, 11, 16), 1, "College Reopens for EVEN Semester (Day - 1)")[span_79](start_span)[span_79](end_span)
    work(datetime.date(2026, 11, 17), 2, "Regular Working Day (Day - 2)")[span_80](start_span)[span_80](end_span)
    work(datetime.date(2026, 11, 18), 3, "Registration Begins for Repeaters (Day - 3)")[span_81](start_span)[span_81](end_span)
    work(datetime.date(2026, 11, 19), 4, "Regular Working Day (Day - 4)")[span_82](start_span)[span_82](end_span)
    work(datetime.date(2026, 11, 20), 5, "Fee Payment Begins / Holy Mass (Day - 5)")[span_83](start_span)[span_83](end_span)
    work(datetime.date(2026, 11, 23), 6, "Regular Working Day (Day - 6)")[span_84](start_span)[span_84](end_span)
    work(datetime.date(2026, 11, 24), 1, "Regular Working Day (Day - 1)")[span_85](start_span)[span_85](end_span)
    work(datetime.date(2026, 11, 25), 2, "Regular Working Day (Day - 2)")[span_86](start_span)[span_86](end_span)
    work(datetime.date(2026, 11, 26), 3, "Regular Working Day (Day - 3)")[span_87](start_span)[span_87](end_span)
    work(datetime.date(2026, 11, 27), 4, "IQAC Meeting (Day - 4)")[span_88](start_span)[span_88](end_span)
    work(datetime.date(2026, 11, 30), 5, "Regular Working Day (Day - 5)")[span_89](start_span)[span_89](end_span)

    work(datetime.date(2026, 12, 1), 6, "Springboard Leadership Program (Day - 6)")[span_90](start_span)[span_90](end_span)
    work(datetime.date(2026, 12, 2), 1, "Internal Arrear Registration Begins (Day - 1)")[span_91](start_span)[span_91](end_span)
    work(datetime.date(2026, 12, 3), 2, "Feast of St. Francis Xavier - Holy Mass (Day - 2)")[span_92](start_span)[span_92](end_span)
    work(datetime.date(2026, 12, 4), 3, "Department Festival Day - 1 (Day - 3)")[span_93](start_span)[span_93](end_span)
    work(datetime.date(2026, 12, 5), 4, "Department Festival Day - 2 (Day - 4)")[span_94](start_span)[span_94](end_span)
    work(datetime.date(2026, 12, 7), 5, "Regular Working Day (Day - 5)")[span_95](start_span)[span_95](end_span)
    work(datetime.date(2026, 12, 8), 6, "Immaculate Conception of Our Lady (Day - 6)")[span_96](start_span)[span_96](end_span)
    work(datetime.date(2026, 12, 9), 1, "III UG Internship Begins (Day - 1)")[span_97](start_span)[span_97](end_span)
    work(datetime.date(2026, 12, 10), 2, "Regular Working Day (Day - 2)")[span_98](start_span)[span_98](end_span)
    work(datetime.date(2026, 12, 11), 3, "Regular Working Day (Day - 3)")[span_99](start_span)[span_99](end_span)
    work(datetime.date(2026, 12, 14), 4, "Regular Working Day (Day - 4)")[span_100](start_span)[span_100](end_span)
    work(datetime.date(2026, 12, 15), 5, "Semester Fee Payment without fine (Day - 5)")[span_101](start_span)[span_101](end_span)
    work(datetime.date(2026, 12, 16), 6, "Regular Working Day (Day - 6)")[span_102](start_span)[span_102](end_span)
    work(datetime.date(2026, 12, 17), 1, "Registration of Repeaters Ends (Day - 1)")[span_103](start_span)[span_103](end_span)
    work(datetime.date(2026, 12, 18), 2, "Regular Working Day (Day - 2)")[span_104](start_span)[span_104](end_span)
    work(datetime.date(2026, 12, 21), 3, "Regular Working Day (Day - 3)")[span_105](start_span)[span_105](end_span)
    work(datetime.date(2026, 12, 22), 4, "Christmas Celebration (Day - 4)")[span_106](start_span)[span_106](end_span)

    work(datetime.date(2027, 1, 4), 5, "College Reopens after Christmas Vacation (Day - 5)")[span_107](start_span)[span_107](end_span)
    work(datetime.date(2027, 1, 5), 6, "Regular Working Day (Day - 6)")[span_108](start_span)[span_108](end_span)
    work(datetime.date(2027, 1, 6), 1, "Training Programme for Staff (Day - 1)")[span_109](start_span)[span_109](end_span)
    work(datetime.date(2027, 1, 7), 2, "Semester Fee Payment with fine (Day - 2)")[span_110](start_span)[span_110](end_span)
    work(datetime.date(2027, 1, 8), 3, "Holy Mass / IQAC Meeting (Day - 3)")[span_111](start_span)[span_111](end_span)
    work(datetime.date(2027, 1, 9), 4, "Working Saturday (Day - 4)")[span_112](start_span)[span_112](end_span)
    work(datetime.date(2027, 1, 11), 5, "Regular Working Day (Day - 5)")[span_113](start_span)[span_113](end_span)
    work(datetime.date(2027, 1, 12), 6, "Regular Working Day (Day - 6)")[span_114](start_span)[span_114](end_span)
    work(datetime.date(2027, 1, 13), 1, "III UG Join Classes / Pongal Celebration (Day - 1)")[span_115](start_span)[span_115](end_span)
    work(datetime.date(2027, 1, 14), 2, "Bhogi (Day - 2)")[span_116](start_span)[span_116](end_span)
    work(datetime.date(2027, 1, 18), 3, "Regular Working Day (Day - 3)")[span_117](start_span)[span_117](end_span)
    work(datetime.date(2027, 1, 19), 4, "Regular Working Day (Day - 4)")[span_118](start_span)[span_118](end_span)
    work(datetime.date(2027, 1, 29), 5, "Regular Working Day (Day - 5)")[span_119](start_span)[span_119](end_span)
    work(datetime.date(2027, 1, 30), 6, "Parent-Teacher Meeting (Working Saturday - Day - 6)")[span_120](start_span)[span_120](end_span)

    work(datetime.date(2027, 2, 1), 1, "Regular Working Day (Day - 1)")[span_121](start_span)[span_121](end_span)
    work(datetime.date(2027, 2, 2), 2, "Regular Working Day (Day - 2)")[span_122](start_span)[span_122](end_span)
    work(datetime.date(2027, 2, 3), 3, "Regular Working Day (Day - 3)")[span_123](start_span)[span_123](end_span)
    work(datetime.date(2027, 2, 4), 4, "Feast of St. John De Britto (Day - 4)")[span_124](start_span)[span_124](end_span)
    work(datetime.date(2027, 2, 5), 5, "Online Exam Registration Begins (Day - 5)")[span_125](start_span)[span_125](end_span)
    work(datetime.date(2027, 2, 6), 6, "Sports Day (Working Saturday - Day - 6)")[span_126](start_span)[span_126](end_span)
    work(datetime.date(2027, 2, 8), 1, "Regular Working Day (Day - 1)")[span_127](start_span)[span_127](end_span)
    work(datetime.date(2027, 2, 9), 2, "Regular Working Day (Day - 2)")[span_128](start_span)[span_128](end_span)
    work(datetime.date(2027, 2, 10), 3, "Ash Wednesday (Day - 3)")[span_129](start_span)[span_129](end_span)
    work(datetime.date(2027, 2, 11), 4, "Feast of Our Lady of Lourdes (Day - 4)")[span_130](start_span)[span_130](end_span)
    work(datetime.date(2027, 2, 12), 5, "Seminar for Academic Staff (Day - 5)")[span_131](start_span)[span_131](end_span)
    work(datetime.date(2027, 2, 13), 6, "Seminar for Academic Staff (Working Saturday - Day - 6)")[span_132](start_span)[span_132](end_span)
    work(datetime.date(2027, 2, 15), 1, "Regular Working Day (Day - 1)")[span_133](start_span)[span_133](end_span)
    work(datetime.date(2027, 2, 16), 2, "Regular Working Day (Day - 2)")[span_134](start_span)[span_134](end_span)
    work(datetime.date(2027, 2, 17), 3, "Regular Working Day (Day - 3)")[span_135](start_span)[span_135](end_span)
    work(datetime.date(2027, 2, 18), 4, "Regular Working Day (Day - 4)")[span_136](start_span)[span_136](end_span)
    work(datetime.date(2027, 2, 19), 5, "Open Forum for Students (Day - 5)")[span_137](start_span)[span_137](end_span)
    work(datetime.date(2027, 2, 22), 6, "Regular Working Day (Day - 6)")[span_138](start_span)[span_138](end_span)
    work(datetime.date(2027, 2, 23), 1, "Regular Working Day (Day - 1)")[span_139](start_span)[span_139](end_span)
    work(datetime.date(2027, 2, 24), 2, "Springboard Leadership Program (Day - 2)")[span_140](start_span)[span_140](end_span)
    work(datetime.date(2027, 2, 25), 3, "Regular Working Day (Day - 3)")[span_141](start_span)[span_141](end_span)
    work(datetime.date(2027, 2, 26), 4, "Loyola Research Day (Day - 4)")[span_142](start_span)[span_142](end_span)

    work(datetime.date(2027, 3, 1), 5, "Online Exam Registration without fine (Day - 5)")[span_143](start_span)[span_143](end_span)
    work(datetime.date(2027, 3, 2), 6, "Regular Working Day (Day - 6)")[span_144](start_span)[span_144](end_span)
    work(datetime.date(2027, 3, 3), 1, "LSC Valedictory (Day - 1)")[span_145](start_span)[span_145](end_span)
    work(datetime.date(2027, 3, 4), 2, "Regular Working Day (Day - 2)")[span_146](start_span)[span_146](end_span)
    work(datetime
