import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات - مصطفى حسن", layout="wide")

# إضافة حقوق الملكية في الشريط الجانبي (Sidebar)
with st.sidebar:
    st.markdown("### 🛡️ حقوق الملكية والبرمجة")
    st.markdown("""
    **إعداد وتطوير:**
    **مصطفى حسن صكبان**
    
    **العنوان:**
    العراق - محافظة الديوانية
    قسم الشؤون المالية - شعبة حسابات الثانوي
    
    **للتواصل:**
    [07702360003](tel:07702360003)
    
    **الإصدار:** 1.0.1
    ---
    **ملاحظة:** جميع الحقوق محفوظة © 2026
    """)
    st.divider()
    st.info("نظام حسابي متطور لمعالجة فروقات الترفيع والعلاوات.")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl; text-align: right;}
    input, select {direction: rtl;}
    th, td {text-align: right !important;}
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: #333;
        text-align: center;
        padding: 5px;
        font-size: 11px;
        border-top: 1px solid #e6e9ef;
        z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ حاسبة الفروقات الوظيفية")
st.caption("تطوير: مصطفى حسن صكبان - قسم الشؤون المالية")

# ---------------------------------------------------------
# 🔧 دوال الحساب
# ---------------------------------------------------------

def get_months(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_allowance_logic(current_sal, current_date, prev_sal, prev_date):
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, ""
    ref_sal = prev_sal if prev_sal else 0
    step_diff = current_sal - ref_sal
    if not prev_date:
        return step_diff, step_diff, "بداية"
    if current_date.year > prev_date.year:
        return step_diff, step_diff * 2, f"سنة جديدة (×2)"
    else:
        return step_diff, step_diff, "نفس السنة"

def calculate_promotion_logic(current_sal, current_date, prev_sal, prev_date, base_sal):
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, ""
    check_year = prev_date.year if prev_date else current_date.year
    if current_date.year > check_year:
        diff = current_sal - base_sal
        return (current_sal - (prev_sal if prev_sal else base_sal)), diff, "سنة جديدة (عودة للأساس)"
    else:
        ref_sal = prev_sal if prev_sal else base_sal
        diff = current_sal - ref_sal
        return diff, diff, "نفس السنة"

# ---------------------------------------------------------
# 1️⃣ الإدخالات
# ---------------------------------------------------------
st.subheader("1. البيانات")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 💰 الرواتب")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0)
    s1 = st.number_input("الراتب بعد العلاوة الأولى", value=0)
    s2 = st.number_input("الراتب بعد العلاوة الثانية", value=0)
    s3 = st.number_input("الراتب بعد العلاوة الثالثة", value=0)
    sp = st.number_input("الراتب بعد الترفيع", value=0)

    st.write("---")
    degree_options = ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"]
    degree = st.selectbox("التحصيل العلمي", degree_options, index=3)
    rates = {"دكتوراه": 1.00, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
    rate = rates.get(degree, 0)

with col2:
    st.markdown("##### 📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=None)
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة", value=date.today())

# ---------------------------------------------------------
# 2️⃣ المعالجة المنطقية
# ---------------------------------------------------------
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de
endp = de

rows = []
total_nom = 0

if s1 > 0 and d1:
    d_raw, d_final, note = calculate_allowance_logic(s1, d1, base_sal, None)
    m = get_months(d1, end1)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["علاوة 1", m, d_final, f"{nom:,.0f}", note])

if s2 > 0 and d2:
    prev_s, prev_d = s1 if s1 > 0 else base_sal, d1 if s1 > 0 else None
    d_raw, d_final, note = calculate_allowance_logic(s2, d2, prev_s, prev_d)
    m = get_months(d2, end2)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["علاوة 2", m, d_final, f"{nom:,.0f}", note])

if s3 > 0 and d3:
    prev_s = s2 if s2 > 0 else (s1 if s1 > 0 else base_sal)
    prev_d = d2 if s2 > 0 else (d1 if d1 else None)
    d_raw, d_final, note = calculate_allowance_logic(s3, d3, prev_s, prev_d)
    m = get_months(d3, end3)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["علاوة 3", m, d_final, f"{nom:,.0f}", note])

if sp > 0 and dp:
    if s3 > 0: prev_s, prev_d = s3, d3
    elif s2 > 0: prev_s, prev_d = s2, d2
    elif s1 > 0: prev_s, prev_d = s1, d1
    else: prev_s, prev_d = base_sal, None
    d_raw, d_final, note = calculate_promotion_logic(sp, dp, prev_s, prev_d, base_sal)
    m = get_months(dp, endp)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["الترف
