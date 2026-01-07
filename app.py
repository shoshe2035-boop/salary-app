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
    if not current_sal or current_sal == 0 or not current_date: return 0, 0, ""
    ref_sal = prev_sal if prev_sal else 0
    step_diff = current_sal - ref_sal
    if not prev_date: return step_diff, step_diff, "بداية"
    if current_date.year > prev_date.year:
        return step_diff, step_diff * 2, "سنة جديدة (×2)"
    return step_diff, step_diff, "نفس السنة"

def calculate_promotion_logic(current_sal, current_date, prev_sal, prev_date, base_sal):
    if not current_sal or current_sal == 0 or not current_date: return 0, 0, ""
    check_year = prev_date.year if prev_date else current_date.year
    if current_date.year > check_year:
        return (current_sal - (prev_sal if prev_sal else base_sal)), (current_sal - base_sal), "سنة جديدة (أساس)"
    return (current_sal - (prev_sal if prev_sal else base_sal)), (current_sal - (prev_sal if prev_sal else base_sal)), "نفس السنة"

# 1️⃣ الإدخالات بتنسيق أعمدة
c1, c2 = st.columns(2)

with c1:
    st.info("💰 المبالغ والرواتب")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0, min_value=0)
    s1 = st.number_input("الراتب بعد العلاوة 1", value=0, min_value=0)
    s2 = st.number_input("الراتب بعد العلاوة 2", value=0, min_value=0)
    s3 = st.number_input("الراتب بعد العلاوة 3", value=0, min_value=0)
    sp = st.number_input("الراتب بعد الترفيع", value=0, min_value=0)
    
    st.divider()
    degree = st.selectbox("🎓 التحصيل العلمي (النسبة)", 
                          ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)
    rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
    rate = rates.get(degree, 0)

with c2:
    st.info("📅 جدول التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=None)
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today())

# 2️⃣ المعالجة
end1 = d2 or d3 or dp or de
end2 = d3 or dp or de
end3 = dp or de
endp = de

rows = []
total_nom = 0

# (تطبيق المنطق الحسابي لجميع المراحل كما في V13)
# العلاوة 1
if s1 > 0 and d1:
    dr, df, note = calculate_allowance_logic(s1, d1, base_sal, None)
    m = get_months(d1, end1)
    if m > 0:
        total_nom += (df * m)
        rows.append({"المرحلة": "علاوة 1", "أشهر": m, "الفرق": df, "الاسمي": f"{df*m:,.0f}", "ملاحظة": note})

# العلاوة 2
if s2 > 0 and d2:
    dr, df, note = calculate_allowance_logic(s2, d2, s1 or base_sal, d1 if s1 > 0 else None)
    m = get_months(d2, end2)
    if m > 0:
        total_nom += (df * m)
        rows.append({"المرحلة": "علاوة 2", "أشهر": m, "الفرق": df, "الاسمي": f"{df*m:,.0f}", "ملاحظة": note})

# العلاوة 3
if s3 > 0 and d3:
    ps, pd = (s2, d2) if s2 > 0 else ((s1, d1) if s1 > 0 else (base_sal, None))
    dr, df, note = calculate_allowance_logic(s3, d3, ps, pd)
    m = get_months(d3, end3)
    if m > 0:
        total_nom += (df * m)
        rows.append({"المرحلة": "علاوة 3", "أشهر": m, "الفرق": df, "الاسمي": f"{df*m:,.0f}", "ملاحظة": note})

# الترفيع
if sp > 0 and dp:
    ps, pd = (s3, d3) if s3 > 0 else ((s2, d2) if s2 > 0 else ((s1, d1) if s1 > 0 else (base_sal, None)))
    dr, df, note = calculate_promotion_logic(sp, dp, ps, pd, base_sal)
    m = get_months(dp, endp)
    if m > 0:
        total_nom += (df * m)
        rows.append({"المرحلة": "الترفيع", "أشهر": m, "الفرق": df, "الاسمي": f"{df*m:,.0f}", "ملاحظة": note})

# 3️⃣ النتائج
st.markdown("### 📊 كشف النتائج")
if rows:
    st.table(rows)
    
    total_gen = total_nom * rate
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.metric("إجمالي الفرق الاسمي", f"{total_nom:,.0f} د.ع")
    with res_c2:
        st.metric("المستحق النهائي (العام)", f"{total_gen:,.1f} د.ع", delta=f"{int(rate*100)}% نسبة الشهادة")
else:
    st.warning("الرجاء إدخال البيانات للبدء في الحساب.")

# المذيل
st.markdown(f"""
<div class="footer">
    مصطفى حسن صكبان - شعبة حسابات الثانوي - محافظة الديوانية - 2026 ©
</div>
""", unsafe_allow_html=True)
