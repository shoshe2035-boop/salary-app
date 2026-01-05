import streamlit as st
from datetime import date

# إعداد الصفحة وتنسيقها
st.set_page_config(page_title="حاسبة الفروقات الوظيفية - النسخة المطابقة", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stNumberInput, .stDateInput, .stSelectbox {direction: rtl;}
    th {text-align: right !important;}
    td {text-align: right !important;}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ الحاسبة الوظيفية (مطابقة لملف 2026)")

# دالة حساب الأشهر (منطق الإكسل DATEDIF)
def get_m(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# --- واجهة الإدخال ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("💰 الرواتب")
    base_salary = st.number_input("الراتب الاسمي القديم", value=250)
    sal1 = st.number_input("راتب العلاوة الأولى", value=260)
    sal2 = st.number_input("راتب العلاوة الثانية", value=270)
    sal3 = st.number_input("راتب العلاوة الثالثة (اختياري)", value=0)
    sal_p = st.number_input("الراتب بعد الترفيع", value=300)
    
    degree = st.selectbox("الشهادة", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية/متوسطة"], index=3)
    rate = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية/متوسطة": 0.15}[degree]

with c2:
    st.subheader("📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة الأولى", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة الثانية", value=date(2023, 1, 1))
    d3 = st.date_input("تاريخ العلاوة الثالثة", value=None)
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
    de = st.date_input("تاريخ نهاية الفترة", value=date(2024, 12, 1))

# --- منطق الحساب القفزي المطابق للإكسل ---
# تحديد تاريخ نهاية كل مرحلة (إذا كان تاريخ العلاوة التالية مفقود، يأخذ تاريخ الترفيع)
end_m1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end_m2 = d3 if d3 else (dp if dp else de)
end_m3 = dp if dp else de

# 1. حساب عدد الأشهر
m1 = get_m(d1, end_m1)
m2 = get_m(d2, end_m2) if d2 else 0
m3 = get_m(d3, end_m3) if d3 else 0
mp = get_m(dp, de) if dp else 0

# 2. حساب الفروقات الاسمية (مطابق لمعادلة الإكسل: الفرق عن الأساس * الأشهر)
f1_nom = (sal1 - base_salary) * m1 if sal1 > 0 else 0
f2_nom = (sal2 - base_salary) * m2 if sal2 > 0 else 0
f3_nom = (sal3 - base_salary) * m3 if sal3 > 0 else 0
fp_nom = (sal_p - base_salary) * mp if sal_p > 0 else 0

# --- عرض النتائج في جدول ---
st.divider()
st.subheader("📊 تفاصيل الحساب")

stages = []
if m1 > 0: stages.append(["العلاوة 1", m1, f1_nom, f1_nom * rate])
if m2 > 0: stages.append(["العلاوة 2", m2, f2_nom, f2_nom * rate])
if m3 > 0: stages.append(["العلاوة 3", m3, f3_nom, f3_nom * rate])
if mp > 0: stages.append(["الترفيع", mp, fp_nom, fp_nom * rate])

if stages:
    st.table({
        "المرحلة": [s[0] for s in stages],
        "الأشهر": [s[1] for s in stages],
        "الفرق الاسمي": [f"{s[2]:,.0f}" for s in stages],
        "الفرق العام (المستحق)": [f"{s[3]:,.1f}" for s in stages]
    })
    
    total_gen = sum(s[3] for s in stages)
    st.success(f"المجموع الكلي للفروقات المستحقة: {total_gen:,.1f} دينار")
else:
    st.warning("الرجاء التأكد من إدخال التواريخ بشكل صحيح.")
