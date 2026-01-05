import streamlit as st
from datetime import date

# إعداد واجهة التطبيق
st.set_page_config(page_title="حاسبة الفروقات الاحترافية", layout="wide")

# تصميم الواجهة لتناسب اللغة العربية (RTL)
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stNumberInput, .stDateInput, .stSelectbox {direction: rtl;}
    div[data-testid="stMetricValue"] { font-size: 25px; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ نظام حساب الفروقات الوظيفية المعتمد")
st.info("ملاحظة: هذا النظام مصمم ليتطابق مع معادلات ملف Excel 2026 الخاص بك.")

# دالة حساب الأشهر (منطق DATEDIF المعتمد في ملفك)
def calculate_months(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# --- قسم المدخلات ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 البيانات المالية")
    old_salary = st.number_input("الراتب الاسمي القديم (الأساسي)", value=250, help="هذا هو الراتب الذي يُطرح منه الرواتب الجديدة")
    sal1 = st.number_input("راتب العلاوة 1", value=0)
    sal2 = st.number_input("راتب العلاوة 2", value=0)
    sal3 = st.number_input("راتب العلاوة 3", value=0)
    sal_p = st.number_input("الراتب بعد الترفيع", value=0)
    
    degree = st.selectbox("التحصيل العلمي (نسبة الشهادة)", ["دكتوراه (100%)", "ماجستير (75%)", "بكالوريوس (50%)", "أخرى/أمية (15%)"])
    rates = {"دكتوراه (100%)": 1.0, "ماجستير (75%)": 0.75, "بكالوريوس (50%)": 0.50, "أخرى/أمية (15%)": 0.15}
    current_rate = rates[degree]

with col2:
    st.subheader("📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=None)
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة (أمر ضروري)", value=date(2024, 12, 1))

# --- منطق الحساب القافز (Skipping Logic) ---
# هذا المنطق يحدد تاريخ نهاية كل مرحلة بناءً على توفر التاريخ الذي يليه
next1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
next2 = d3 if d3 else (dp if dp else de)
next3 = dp if dp else de

# 1. حساب الأشهر لكل مرحلة
m1 = calculate_months(d1, next1) if d1 else 0
m2 = calculate_months(d2, next2) if d2 else 0
m3 = calculate_months(d3, next3) if d3 else 0
mp = calculate_months(dp, de) if dp else 0

# 2. حساب الفروقات الاسمية (الراتب الجديد - الراتب الأصلي) كما في ملفك
f1_nom = (sal1 - old_salary) * m1 if sal1 > 0 else 0
f2_nom = (sal2 - old_salary) * m2 if sal2 > 0 else 0
f3_nom = (sal3 - old_salary) * m3 if sal3 > 0 else 0
fp_nom = (sal_p - old_salary) * mp if sal_p > 0 else 0

# 3. حساب الفرق العام (الاسمي × النسبة)
f1_gen = f1_nom * current_rate
f2_gen = f2_nom * current_rate
f3_gen = f3_nom * current_rate
fp_gen = fp_nom * current_rate

# --- عرض النتائج على شكل جدول منظم ---
st.divider()
st.subheader("📋 كشف تفصيلي بالفروقات")

# إنشاء جدول لعرض النتائج
data = []
if d1: data.append(["العلاوة 1", m1, f1_nom, f1_gen])
if d2: data.append(["العلاوة 2", m2, f2_nom, f2_gen])
if d3: data.append(["العلاوة 3", m3, f3_nom, f3_gen])
if dp: data.append(["الترفيع", mp, fp_nom, fp_gen])

if data:
    st.table({
        "المرحلة": [x[0] for x in data],
        "عدد الأشهر": [x[1] for x in data],
        "الفرق الاسمي": [f"{x[2]:,.0f}" for x in data],
        "الفرق العام (المستحق)": [f"{x[3]:,.1f}" for x in data]
    })
    
    total_nom = f1_nom + f2_nom + f3_nom + fp_nom
    total_gen = f1_gen + f2_gen + f3_gen + fp_gen

    c_nom, c_gen = st.columns(2)
    with c_nom:
        st.metric("إجمالي الفرق الاسمي", f"{total_nom:,.0f}")
    with c_gen:
        st.success(f"المجموع الكلي للمستحق: {total_gen:,.1f}")
else:
    st.warning("يرجى إدخال 'تاريخ العلاوة 1' على الأقل لبدء الحساب.")

st.caption("يتجاهل النظام تلقائياً أي علاوة لا تحتوي على تاريخ أو راتب كما في الإكسل.")
