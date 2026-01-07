import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة والتنسيق الجمالي
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات - مصطفى حسن", layout="wide")

# CSS متقدم لتحسين المظهر ودعم اللغة العربية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

    html, body, [data-testid="stSidebar"], .main {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* تنسيق الحاويات والبطاقات */
    .stNumberInput, .stDateInput, .stSelectbox {
        transition: 0.3s;
    }
    
    /* تنسيق الجداول */
    [data-testid="stTable"] {
        background-color: #ffffff;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    th {
        background-color: #1E3A8A !important;
        color: white !important;
        text-align: right !important;
    }

    /* المذيل الجمالي */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f8f9fa;
        color: #1e3a8a;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-top: 3px solid #1e3a8a;
        z-index: 100;
    }
    
    /* أيقونة الجانب */
    .sidebar-info {
        background-color: #e0e7ff;
        padding: 15px;
        border-radius: 10px;
        border-right: 5px solid #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# الشريط الجانبي - الهوية البصرية
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=100)
    st.markdown("<div class='sidebar-info'>", unsafe_allow_html=True)
    st.markdown("### 👤 المطور المسؤول")
    st.write("**أستاذ: مصطفى حسن صكبان**")
    st.write("📍 محافظة الديوانية")
    st.write("🏢 شعبة حسابات الثانوي")
    st.write("📞 07702360003")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    st.caption("حقوق النشر محفوظة © 2026")

# ---------------------------------------------------------
# واجهة التطبيق الرئيسية
# ---------------------------------------------------------
st.title("⚖️ حاسبة الفروقات الوظيفية الذكية")
st.markdown("---")

# دوال الحساب المعتمدة سابقاً
def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_allowance_logic(current_sal, current_date, prev_sal, prev_date):
    if not current_sal or current_sal == 0 or not current
