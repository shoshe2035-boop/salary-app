import streamlit as st
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="حاسبة الفروقات الوظيفية", layout="wide")

# تصميم الواجهة RTL
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stNumberInput, .stDateInput, .stSelectbox {direction: rtl;}
</style>
""", unsafe_allow_html=True)

st.title("📊 حاسبة الفروقات الوظيفية (مطابقة لملف 2026)")

# دالة حساب الأشهر (منطق DATEDIF M)
def get_m(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# --- المدخلات ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("💰 الرواتب الاسمية")
    old_salary = st.number_input("الراتب الاسمي القديم (الأساس)", value=250, step=1)
    sal1 = st.number_input("راتب العلاوة الأولى", value=260, step=1)
    sal2 = st.number_input("راتب العلاوة الثانية", value=270, step=1)
    sal3 = st.number_input("راتب العلاوة الثالثة (اتركه 0 إذا لم يوجد)", value=0, step=1)
    sal_p = st.number_input("الراتب بعد الترفيع", value=300, step=1)
    
    st.markdown("---")
    degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"], index=3)

with c2:
    st.subheader("📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة الأولى", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة الثانية", value=date(2023, 1, 1))
    d3 = st.date_input("تاريخ العلاوة الثالثة", value=None)
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
    de = st.date_input("تاريخ نهاية الفترة", value=date(2024, 12, 1))

# --- منطق الحساب المطابق للإكسل ---

# تحديد التاريخ التالي المتاح لكل مرحلة
next_after_1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
next_after_2 = d3 if d3 else (dp if dp else de)
next_after_3 = dp if dp else de

# 1. حساب الأشهر
m1 = get_m(d1, next_after_1)
m2 = get_m(d2, next_after_2) if d2 else 0
m3 = get_m(d3, next_after_3) if d3 else 0
mp = get_m(dp, de) if dp else 0

# 2. حساب الفروقات (الراتب الحالي - الراتب القديم الأساسي) كما في الإكسل
f1 = (sal1 - old_salary) * m1 if sal1 > 0 else 0
f2 = (sal2 - old_salary) * m2 if sal2 > 0 else 0
f3 = (sal3 - old_salary) * m3 if sal3 > 0 else 0
fp = (sal_p - old_salary) * mp if sal_p > 0 else 0

total_nominal = f1 + f2 + f3 + fp

# 3. نسبة الشهادة
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية": 0.15}
current_rate = rates[degree]

final_total = total_nominal * current_rate

# --- عرض النتائج ---
st.divider()
res1, res2 = st.columns(2)

with res1:
    st.info(f"التحصيل: {degree} ({int(current_rate*100)}%)")
    st.write(f"أشهر العلاوة 1: **{m1}** | الفرق: **{f1:,.1f}**")
    st.write(f"أشهر العلاوة 2: **{m2}** | الفرق: **{f2:,.1f}**")
    st.write(f"أشهر العلاوة 3: **{m3}** | الفرق: **{f3:,.1f}**")
    st.write(f"أشهر الترفيع: **{mp}** | الفرق: **{fp:,.1f}**")

with res2:
    st.metric("إجمالي الفرق الاسمي", f"{total_nominal:,.1f}")
    st.success(f"المجموع الكلي للمستحق: {final_total:,.1f}")

st.caption("ملاحظة: تم ضبط الحساب ليطابق منطق ملف الإكسل المرفق (الفرق يحسب من الراتب الأساسي القديم).")
