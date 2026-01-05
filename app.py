import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta

# إعدادات واجهة التطبيق
st.set_page_config(page_title="حاسبة الفروقات الوظيفية المتقدمة", layout="wide")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    st.number_input, st.date_input, st.selectbox { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📊 نظام حساب الفروقات الوظيفية (نسخة الإكسل)")

# دالة حساب الأشهر (تطابق منطق DATEDIF)
def calculate_months(start, end):
    if start and end and start < end:
        diff = relativedelta(end, start)
        return diff.years * 12 + diff.months
    return 0

# --- المدخلات ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 الرواتب والشهادة")
    old_salary = st.number_input("الراتب الاسمي القديم", value=0)
    salary_1 = st.number_input("راتب العلاوة الأولى", value=0)
    salary_2 = st.number_input("راتب العلاوة الثانية", value=0)
    salary_3 = st.number_input("راتب العلاوة الثالثة", value=0)
    salary_promotion = st.number_input("الراتب بعد الترفيع", value=0)
    
    st.divider()
    degree = st.selectbox("الشهادة (التحصيل العلمي)", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"])

with col2:
    st.subheader("📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة الأولى", value=None)
    d2 = st.date_input("تاريخ العلاوة الثانية", value=None)
    d3 = st.date_input("تاريخ العلاوة الثالثة", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة (إعداد القوائم)", value=None)

# --- منطق الحساب المأخوذ من الملف ---
# 1. حساب الأشهر
m1 = calculate_months(d1, d2)
m2 = calculate_months(d2, d3 if d3 else (dp if dp else de))
m3 = calculate_months(d3, dp if dp else de)
mp = calculate_months(dp, de)

# 2. الفروقات الاسمية
diff_nominal_1 = (salary_1 - old_salary) * m1
diff_nominal_2 = (salary_2 - salary_1) * m2
diff_nominal_3 = (salary_3 - salary_2) * m3
diff_nominal_p = (salary_promotion - (salary_3 if salary_3 > 0 else salary_2)) * mp

total_nominal = diff_nominal_1 + diff_nominal_2 + diff_nominal_3 + diff_nominal_p

# 3. نسبة الشهادة (حسب ملفك)
degree_rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية": 0.15}
rate = degree_rates.get(degree, 0)

# 4. الفرق العام (الاسمي × النسبة)
gen_diff_1 = diff_nominal_1 * rate
gen_diff_2 = diff_nominal_2 * rate
gen_diff_3 = diff_nominal_3 * rate
gen_diff_p = diff_nominal_p * rate

total_general = gen_diff_1 + gen_diff_2 + gen_diff_3 + gen_diff_p

# --- عرض النتائج ---
st.divider()
st.header("📋 ملخص الحسابات")

res1, res2, res3 = st.columns(3)
with res1:
    st.metric("إجمالي الأشهر", m1 + m2 + m3 + mp)
    st.write(f"أشهر العلاوة 1: {m1}")
    st.write(f"أشهر العلاوة 2: {m2}")
    st.write(f"أشهر العلاوة 3: {m3}")
    st.write(f"أشهر الترفيع: {mp}")

with res2:
    st.metric("إجمالي الفرق الاسمي", f"{total_nominal:,.0f} دينار")
    st.write(f"فرق علاوة 1: {diff_nominal_1:,.0f}")
    st.write(f"فرق علاوة 2: {diff_nominal_2:,.0f}")
    st.write(f"فرق علاوة 3: {diff_nominal_3:,.0f}")
    st.write(f"فرق ترفيع: {diff_nominal_p:,.0f}")

with res3:
    st.success(f"المجموع الكلي للفروقات (المستحق)")
    st.title(f"{total_general:,.0f}")
    st.info(f"النسبة المطبقة: {int(rate*100)}%")
