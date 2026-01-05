import streamlit as st
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="حاسبة الفروقات الوظيفية", layout="wide")

st.markdown("""
<style>
.main {direction: rtl; text-align: right;}
</style>
""", unsafe_allow_html=True)

st.title("📊 حاسبة الفروقات الوظيفية (مطابقة للإكسل)")

# =========================
# دالة حساب الأشهر (DATEDIF M)
# =========================
def calculate_months(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# =========================
# الإدخالات
# =========================
c1, c2 = st.columns(2)

with c1:
    st.subheader("💰 الرواتب")
    old_salary = st.number_input("الراتب قبل أي علاوة", min_value=0)
    salary_1 = st.number_input("راتب العلاوة الأولى", min_value=0)
    salary_2 = st.number_input("راتب العلاوة الثانية", min_value=0)
    salary_3 = st.number_input("راتب العلاوة الثالثة", min_value=0)
    salary_promotion = st.number_input("الراتب بعد الترفيع", min_value=0)

 لاين

    degree = st.selectbox(
        "التحصيل العلمي",
        ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"]
    )

with c2:
    st.subheader("📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة الأولى", value=None)
    d2 = st.date_input("تاريخ العلاوة الثانية", value=None)
    d3 = st.date_input("تاريخ العلاوة الثالثة", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة", value=None)

# =========================
# نسبة الشهادة (مطابقة للإكسل)
# =========================
degree_rates = {
    "دكتوراه": 1.0,
    "ماجستير": 0.75,
    "بكالوريوس": 0.50,
    "أخرى/أمية": 0.0
}
rate = degree_rates[degree]

# =========================
# منطق المراحل (مثل Excel)
# =========================
stages = []

# علاوة 1
if d1 and d2 and salary_1 > old_salary:
    months = calculate_months(d1, d2)
    stages.append({
        "name": "العلاوة الأولى",
        "months": months,
        "nominal": (salary_1 - old_salary) * months
    })

# علاوة 2
if d2 and d3 and salary_2 > salary_1:
    months = calculate_months(d2, d3)
    stages.append({
        "name": "العلاوة الثانية",
        "months": months,
        "nominal": (salary_2 - salary_1) * months
    })

# علاوة 3
if d3 and dp and salary_3 > salary_2:
    months = calculate_months(d3, dp)
    stages.append({
        "name": "العلاوة الثالثة",
        "months": months,
        "nominal": (salary_3 - salary_2) * months
    })

# الترفيع
if dp and de and salary_promotion > salary_3:
    months = calculate_months(dp, de)
    stages.append({
        "name": "الترفيع",
        "months": months,
        "nominal": (salary_promotion - salary_3) * months
    })

# =========================
# عرض النتائج
# =========================
st.divider()
st.header("📋 تفاصيل الفروقات")

total_nominal = 0
total_general = 0

if not stages:
    st.warning("لم يتم إدخال بيانات كافية لأي علاوة أو ترفيع")
else:
    for s in stages:
        general = s["nominal"] * rate
        total_nominal += s["nominal"]
        total_general += general

        st.subheader(s["name"])
        st.write("عدد الأشهر:", s["months"])
        st.write("الفرق الاسمي:", f"{s['nominal']:,.0f}")
        st.write("الفرق العام:", f"{general:,.0f}")
        st.divider()

    st.success("✅ النتيجة النهائية")
    st.write("إجمالي الفرق الاسمي:", f"{total_nominal:,.0f}")
    st.write("إجمالي الفرق العام (المستحق):", f"{total_general:,.0f}")
