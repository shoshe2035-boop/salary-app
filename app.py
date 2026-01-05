import streamlit as st
from datetime import date

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة الفروقات الوظيفية", layout="wide")

st.markdown("""
<style>
.main { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("📊 نظام حساب الفروقات الوظيفية (مطابق للإكسل)")

# --------------------------------------------------
# دالة حساب الأشهر (مطابقة DATEDIF في Excel)
# --------------------------------------------------
def calculate_months(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# --------------------------------------------------
# المدخلات
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 الرواتب")
    old_salary = st.number_input("الراتب الاسمي القديم", value=0.0)
    salary_1 = st.number_input("راتب العلاوة الأولى", value=0.0)
    salary_2 = st.number_input("راتب العلاوة الثانية", value=0.0)
    salary_3 = st.number_input("راتب العلاوة الثالثة", value=0.0)
    salary_promotion = st.number_input("الراتب بعد الترفيع", value=0.0)

    st.divider()
    degree = st.selectbox(
        "التحصيل العلمي",
        ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"]
    )

with col2:
    st.subheader("📅 التواريخ (غير إلزامية)")
    d1 = st.date_input("تاريخ العلاوة الأولى", value=None)
    d2 = st.date_input("تاريخ العلاوة الثانية", value=None)
    d3 = st.date_input("تاريخ العلاوة الثالثة", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة", value=None)

# --------------------------------------------------
# حساب عدد الأشهر (حسب الإكسل)
# --------------------------------------------------
m1 = calculate_months(d1, d2)
m2 = calculate_months(d2, d3)
m3 = calculate_months(d3, dp)
mp = calculate_months(dp, de)

# --------------------------------------------------
# الفروقات الاسمية (Excel logic)
# --------------------------------------------------
diff_nom_1 = (salary_1 - old_salary) * m1
diff_nom_2 = (salary_2 - salary_1) * m2
diff_nom_3 = (salary_3 - salary_2) * m3
diff_nom_p = (salary_promotion - salary_3) * mp

# --------------------------------------------------
# نسبة الاستحقاق (مطابقة للإكسل)
# --------------------------------------------------
degree_rates = {
    "دكتوراه": 1.0,
    "ماجستير": 0.75,
    "بكالوريوس": 0.5,
    "أخرى/أمية": 0.0
}
rate = degree_rates[degree]

# --------------------------------------------------
# الفروقات العامة (الاسمي × النسبة)
# --------------------------------------------------
diff_gen_1 = diff_nom_1 * rate
diff_gen_2 = diff_nom_2 * rate
diff_gen_3 = diff_nom_3 * rate
diff_gen_p = diff_nom_p * rate

# المجاميع
total_nominal = diff_nom_1 + diff_nom_2 + diff_nom_3 + diff_nom_p
total_general = diff_gen_1 + diff_gen_2 + diff_gen_3 + diff_gen_p

# --------------------------------------------------
# عرض النتائج
# --------------------------------------------------
st.divider()
st.header("📋 النتائج التفصيلية")

res1, res2, res3 = st.columns(3)

with res1:
    st.subheader("🕒 عدد الأشهر")
    st.write(f"العلاوة الأولى: {m1}")
    st.write(f"العلاوة الثانية: {m2}")
    st.write(f"العلاوة الثالثة: {m3}")
    st.write(f"الترفيع: {mp}")

with res2:
    st.subheader("💰 الفرق الاسمي")
    st.write(f"علاوة أولى: {diff_nom_1:,.0f}")
    st.write(f"علاوة ثانية: {diff_nom_2:,.0f}")
    st.write(f"علاوة ثالثة: {diff_nom_3:,.0f}")
    st.write(f"ترفيع: {diff_nom_p:,.0f}")
    st.metric("المجموع الاسمي", f"{total_nominal:,.0f}")

with res3:
    st.subheader("✅ الفرق العام (بعد النسبة)")
    st.write(f"علاوة أولى: {diff_gen_1:,.0f}")
    st.write(f"علاوة ثانية: {diff_gen_2:,.0f}")
    st.write(f"علاوة ثالثة: {diff_gen_3:,.0f}")
    st.write(f"ترفيع: {diff_gen_p:,.0f}")
    st.metric("المجموع النهائي المستحق", f"{total_general:,.0f}")
    st.caption(f"نسبة الاستحقاق: {int(rate*100)}%")
