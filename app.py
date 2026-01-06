import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات – النسخة الكاملة", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    th, td {text-align: right !important;}
    input, select, div[data-baseweb="select"] {direction: rtl;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 نظام الفروقات (النسخة المنقحة الكاملة)")
st.caption("محاكاة معادلات Excel مع حماية من تكرار الفروقات")

# ---------------------------------------------------------
# 🔧 الدوال الأساسية (مطابقة Excel)
# ---------------------------------------------------------

def excel_datedif(start, end):
    """محاكاة DATEDIF(start, end, 'M')"""
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def smart_months(start, *ends):
    """
    اختيار أول تاريخ نهاية صالح (Logic Skipping)
    هذه الدالة تطابق دالة IF المتداخلة في الإكسل لتحديد تاريخ النهاية
    """
    for e in ends:
        if e:
            return excel_datedif(start, e)
    return 0

# ---------------------------------------------------------
# 1️⃣ الإدخالات (Input Columns)
# ---------------------------------------------------------

st.subheader("1. البيانات الأساسية")

col1, col2 = st.columns(2)

with col1:
    # العمود D
    base_salary = st.number_input("الراتب الأساس (D)", value=250)
    # العمود F (قيمة الزيادة السنوية الثابتة)
    allowance_value = st.number_input("قيمة العلاوة الواحدة (F)", value=10)
    # العمود E
    promoted_salary = st.number_input("الراتب بعد الترفيع (E)", value=300)

    # العمود U
    degree = st.selectbox(
        "الشهادة (U)",
        ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى"]
    )

    # العمود V
    degree_rates = {
        "دكتوراه": 1.0,
        "ماجستير": 0.75,
        "بكالوريوس": 0.50,
        "أخرى": 0.15
    }
    rate = degree_rates[degree]

with col2:
    # الأعمدة G, H, I, J, K
    d1 = st.date_input("تاريخ العلاوة الأولى (G)", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة الثانية (H)", value=None)
    d3 = st.date_input("تاريخ العلاوة الثالثة (I)", value=None)
    dp = st.date_input("تاريخ الترفيع (J)", value=date(2024, 6, 1))
    de = st.date_input("تاريخ نهاية الاحتساب (K)", value=date(2024, 12, 1))

# ---------------------------------------------------------
# 2️⃣ الحسابات (Processing)
# ---------------------------------------------------------

# === أ) حساب عدد الأشهر (L, M, N, O) ===
# نمرر التواريخ التالية لتحديد أقرب تاريخ توقف
m1 = smart_months(d1, d2, d3, dp, de)
m2 = smart_months(d2, d3, dp, de) if d2 else 0
m3 = smart_months(d3, dp, de) if d3 else 0
mp = excel_datedif(dp, de) if dp else 0

# === ب) الفروقات الاسمية (P, Q, R, S) ===
# الأعمدة P, Q, R: (عدد الأشهر * قيمة العلاوة الثابتة)
p_nominal = m1 * allowance_value
q_nominal = m2 * allowance_value
r_nominal = m3 * allowance_value

# العمود S: فرق الترفيع
# المعادلة: عدد الأشهر * (راتب الترفيع - الراتب الأساس)
# ملاحظة: تم استخدام الراتب الأساس هنا لضمان حساب كامل الفرق للدرجة الجديدة
promotion_diff = max(promoted_salary - base_salary, 0)
s_nominal = mp * promotion_diff

# === ج) الفروقات العامة (بعد النسبة) ===
gen_p = p_nominal * rate
gen_q = q_nominal * rate
gen_r = r_nominal * rate
gen_s = s_nominal * rate

# === د) المجاميع النهائية (T) ===
total_nominal = p_nominal + q_nominal + r_nominal + s_nominal
total_general = gen_p + gen_q + gen_r + gen_s

# ---------------------------------------------------------
# 3️⃣ عرض النتائج (Outputs)
# ---------------------------------------------------------
st.divider()
st.subheader("2. النتائج التفصيلية")

# تجهيز البيانات للجدول
rows = []
if m1 > 0: rows.append(["العلاوة الأولى", m1, f"{p_nominal:,.0f}", f"{gen_p:,.1f}"])
if m2 > 0: rows.append(["العلاوة الثانية", m2, f"{q_nominal:,.0f}", f"{gen_q:,.1f}"])
if m3 > 0: rows.append(["العلاوة الثالثة", m3, f"{r_nominal:,.0f}", f"{gen_r:,.1f}"])
if mp > 0: rows.append(["الترفيع", mp, f"{s_nominal:,.0f}", f"{gen_s:,.1f}"])

if rows:
    # عرض الجدول
    st.table([
        {
            "المرحلة": r[0],
            "عدد الأشهر": r[1],
            "الفرق الاسمي": r[2],
            "الفرق العام (المستحق)": r[3]
        }
        for r in rows
    ])

    st.markdown("---")
    
    # عرض الملخص النهائي
    c_res1, c_res2, c_res3 = st.columns(3)
    
    with c_res1:
        st.info("إجمالي الفرق الاسمي (T)")
        st.metric("Total Nominal", f"{total_nominal:,.0f}")
        
    with c_res2:
        st.warning(f"نسبة الشهادة ({int(rate*100)}%)")
        st.metric("Degree Rate", f"{degree}")
        
    with c_res3:
        st.success("المجموع الكلي المستحق")
        st.metric("Final Amount", f"{total_general:,.1f}")

else:
    st.warning("⚠️ يرجى إدخال التواريخ لعرض النتائج.")
