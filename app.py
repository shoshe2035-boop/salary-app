import streamlit as st
from datetime import date

st.set_page_config(page_title="حاسبة الفروقات الوظيفية", layout="wide")
st.markdown("<style>.main{direction:rtl;text-align:right}</style>", unsafe_allow_html=True)

st.title("📊 حاسبة الفروقات الوظيفية (مطابقة للإكسل)")

# =========================
# دالة DATEDIF "M"
# =========================
def months_diff(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# =========================
# بيانات عامة
# =========================
base_salary = st.number_input("💰 الراتب قبل أي علاوة", min_value=0)

degree = st.selectbox(
    "🎓 التحصيل العلمي",
    ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"]
)

degree_rate = {
    "دكتوراه": 1.0,
    "ماجستير": 0.75,
    "بكالوريوس": 0.50,
    "أخرى/أمية": 0.0
}[degree]

st.divider()
st.header("🧩 العلاوات والترفيع (اختياري)")

stages = []
current_salary = base_salary

# =========================
# علاوة 1
# =========================
if st.checkbox("إضافة علاوة أولى"):
    with st.expander("العلاوة الأولى", expanded=True):
        s1 = st.number_input("راتب بعد العلاوة الأولى", min_value=0, key="s1")
        d1 = st.date_input("تاريخ العلاوة الأولى", value=None, key="d1")
        d2 = st.date_input("تاريخ العلاوة التالية", value=None, key="d2")

        m = months_diff(d1, d2)
        if m > 0 and s1 > current_salary:
            stages.append(("العلاوة الأولى", m, s1 - current_salary))
            current_salary = s1

# =========================
# علاوة 2
# =========================
if st.checkbox("إضافة علاوة ثانية"):
    with st.expander("العلاوة الثانية", expanded=True):
        s2 = st.number_input("راتب بعد العلاوة الثانية", min_value=0, key="s2")
        d3 = st.date_input("تاريخ العلاوة الثانية", value=None, key="d3")
        d4 = st.date_input("تاريخ العلاوة التالية", value=None, key="d4")

        m = months_diff(d3, d4)
        if m > 0 and s2 > current_salary:
            stages.append(("العلاوة الثانية", m, s2 - current_salary))
            current_salary = s2

# =========================
# علاوة 3
# =========================
if st.checkbox("إضافة علاوة ثالثة"):
    with st.expander("العلاوة الثالثة", expanded=True):
        s3 = st.number_input("راتب بعد العلاوة الثالثة", min_value=0, key="s3")
        d5 = st.date_input("تاريخ العلاوة الثالثة", value=None, key="d5")
        d6 = st.date_input("تاريخ الترفيع", value=None, key="d6")

        m = months_diff(d5, d6)
        if m > 0 and s3 > current_salary:
            stages.append(("العلاوة الثالثة", m, s3 - current_salary))
            current_salary = s3

# =========================
# الترفيع
# =========================
if st.checkbox("إضافة ترفيع"):
    with st.expander("الترفيع", expanded=True):
        sp = st.number_input("الراتب بعد الترفيع", min_value=0, key="sp")
        dp = st.date_input("تاريخ الترفيع", value=None, key="dp")
        de = st.date_input("تاريخ نهاية الفترة", value=None, key="de")

        m = months_diff(dp, de)
        if m > 0 and sp > current_salary:
            stages.append(("الترفيع", m, sp - current_salary))

# =========================
# النتائج
# =========================
st.divider()
st.header("📋 النتائج التفصيلية")

total_nominal = 0
total_general = 0

if not stages:
    st.info("لم تتم إضافة أي علاوة أو ترفيع")
else:
    for name, months, diff in stages:
        nominal = diff * months
        general = nominal * degree_rate

        total_nominal += nominal
        total_general += general

        st.subheader(name)
        st.write("عدد الأشهر:", months)
        st.write("الفرق الاسمي:", f"{nominal:,.0f}")
        st.write("الفرق العام:", f"{general:,.0f}")
        st.divider()

    st.success("✅ المجموع النهائي")
    st.write("إجمالي الفرق الاسمي:", f"{total_nominal:,.0f}")
    st.write("إجمالي الفرق العام (المستحق):", f"{total_general:,.0f}")
