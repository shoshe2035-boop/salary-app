import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات – شاملة", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    th, td {text-align: right !important;}
    input, select, div[data-baseweb="select"] {direction: rtl;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 نظام الفروقات (مع قيم علاوات متعددة)")
st.caption("إمكانية تحديد قيمة مختلفة لكل علاوة (1، 2، 3)")

# ---------------------------------------------------------
# 🔧 الدوال
# ---------------------------------------------------------
def excel_datedif(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def smart_months(start, *ends):
    for e in ends:
        if e:
            return excel_datedif(start, e)
    return 0

# ---------------------------------------------------------
# 1️⃣ الإدخالات
# ---------------------------------------------------------
st.subheader("1. البيانات المالية")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("##### 💵 الرواتب الأساسية")
    base_salary = st.number_input("الراتب الاسمي القديم (D)", value=250)
    promoted_salary = st.number_input("الراتب بعد الترفيع (E)", value=300)
    
    st.markdown("---")
    degree = st.selectbox("الشهادة", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى"])
    rate = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى": 0.15}[degree]

with c2:
    st.markdown("##### 📈 قيم العلاوات (المبلغ المضاف)")
    # هنا أضفنا قيم العلاوات المفقودة
    val_1 = st.number_input("قيمة العلاوة الأولى (F1)", value=10, help="مقدار الزيادة بالدينار")
    val_2 = st.number_input("قيمة العلاوة الثانية (F2)", value=10, help="اكتب 0 إذا كانت نفس السابقة أو لا توجد")
    val_3 = st.number_input("قيمة العلاوة الثالثة (F3)", value=10, help="اكتب 0 إذا كانت نفس السابقة أو لا توجد")

with c3:
    st.markdown("##### 📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
    de = st.date_input("نهاية الفترة", value=date(2024, 12, 1))

# ---------------------------------------------------------
# 2️⃣ الحسابات
# ---------------------------------------------------------

# حساب الأشهر
m1 = smart_months(d1, d2, d3, dp, de)
m2 = smart_months(d2, d3, dp, de) if d2 else 0
m3 = smart_months(d3, dp, de) if d3 else 0
mp = excel_datedif(dp, de) if dp else 0

# حساب الفروقات الاسمية (باستخدام القيم الخاصة لكل مرحلة)
# إذا كانت قيمة العلاوة 2 أو 3 صفر، نستخدم القيمة التي قبلها (اختياري، أو اتركها 0)
# هنا سأفترض أن المستخدم سيدخل القيمة يدوياً، أو نستخدم القيمة 1 إذا أدخلها
nominal_1 = m1 * val_1
nominal_2 = m2 * (val_2 if val_2 > 0 else val_1) # استخدام ذكي: لو تركتها 0 يأخذ السابقة
nominal_3 = m3 * (val_3 if val_3 > 0 else val_2 if val_2 > 0 else val_1)

# فرق الترفيع (القفزة الكاملة عن الراتب القديم)
diff_prom_amount = max(promoted_salary - base_salary, 0)
nominal_prom = mp * diff_prom_amount

# الفروقات العامة (بعد النسبة)
gen_1 = nominal_1 * rate
gen_2 = nominal_2 * rate
gen_3 = nominal_3 * rate
gen_prom = nominal_prom * rate

# المجاميع
total_nom = nominal_1 + nominal_2 + nominal_3 + nominal_prom
total_gen = gen_1 + gen_2 + gen_3 + gen_prom

# ---------------------------------------------------------
# 3️⃣ النتائج
# ---------------------------------------------------------
st.divider()
st.subheader("2. الجدول التفصيلي")

data = []
if m1 > 0: data.append(["العلاوة الأولى", m1, f"{val_1}", f"{nominal_1:,.0f}", f"{gen_1:,.1f}"])
# عرض العلاوة 2 و 3 حتى لو كانت القيمة المدخلة 0 (لأننا أخذنا القيمة السابقة احتياطاً) أو حسب المدخل
v2_used = val_2 if val_2 > 0 else val_1
v3_used = val_3 if val_3 > 0 else (val_2 if val_2 > 0 else val_1)

if m2 > 0: data.append(["العلاوة الثانية", m2, f"{v2_used}", f"{nominal_2:,.0f}", f"{gen_2:,.1f}"])
if m3 > 0: data.append(["العلاوة الثالثة", m3, f"{v3_used}", f"{nominal_3:,.0f}", f"{gen_3:,.1f}"])
if mp > 0: data.append(["الترفيع", mp, f"{diff_prom_amount} (عن الأساس)", f"{nominal_prom:,.0f}", f"{gen_prom:,.1f}"])

if data:
    st.table([
        {"المرحلة": r[0], "الأشهر": r[1], "قيمة الزيادة المعتمدة": r[2], "الفرق الاسمي": r[3], "الفرق العام": r[4]}
        for r in data
    ])
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    with res1:
        st.info("المجموع الاسمي")
        st.metric("Total Nominal", f"{total_nom:,.0f}")
    with res2:
        st.warning(f"النسبة ({int(rate*100)}%)")
        st.metric("Degree", degree)
    with res3:
        st.success("المستحق النهائي")
        st.metric("Final Amount", f"{total_gen:,.1f}")
else:
    st.warning("أدخل التواريخ.")
