import streamlit as st
from datetime import date

# إعداد الصفحة وتنسيقها لتكون احترافية ومطابقة لطلبك
st.set_page_config(page_title="حاسبة الفروقات الوظيفية المعتمدة", layout="wide")

# إعداد واجهة المستخدم لتكون من اليمين لليسار (RTL)
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stNumberInput, .stDateInput, .stSelectbox {direction: rtl;}
    div.stTableCell {text-align: right !important;}
    th {background-color: #f0f2f6 !important; text-align: right !important;}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ حاسبة الفروقات الوظيفية (نسخة مطابقة لملف 2026)")

# دالة حساب الأشهر (DATEDIF M)
def get_m(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# =========================
# قسم المدخلات (الرواتب والشهادة)
# =========================
st.subheader("1️⃣ البيانات الأساسية والرواتب")
c1, c2, c3 = st.columns([2, 2, 2])

with c1:
    base_salary = st.number_input("الراتب الاسمي القديم (الأساس)", value=250)
    degree = st.selectbox("التحصيل العلمي (الشهادة)", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية/متوسطة"], index=3)
    # نسبة الشهادة حسب ملف الإكسل الخاص بك
    rate = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية/متوسطة": 0.15}[degree]

with c2:
    sal1 = st.number_input("راتب العلاوة 1", value=260)
    sal2 = st.number_input("راتب العلاوة 2", value=270)
    sal3 = st.number_input("راتب العلاوة 3 (اختياري)", value=0)

with c3:
    sal_p = st.number_input("الراتب بعد الترفيع", value=300)
    de = st.date_input("تاريخ نهاية الفترة (أمر القوائم)", value=date(2024, 12, 1))

st.divider()

# =========================
# قسم التواريخ
# =========================
st.subheader("2️⃣ التواريخ (اترك الحقل فارغاً إذا لم يوجد)")
d_col1, d_col2, d_col3, d_col4 = st.columns(4)

with d_col1:
    d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
with d_col2:
    d2 = st.date_input("تاريخ العلاوة 2", value=date(2023, 1, 1))
with d_col3:
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
with d_col4:
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))

# =========================
# منطق الحساب (مطابق للإكسل حرفياً)
# =========================
# تحديد نهاية كل مرحلة (القفز فوق الفارغ)
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de

# حساب الأشهر
m1 = get_m(d1, end1)
m2 = get_m(d2, end2) if d2 else 0
m3 = get_m(d3, end3) if d3 else 0
mp = get_m(dp, de) if dp else 0

# حساب الفروقات (الراتب الجديد - الراتب الأساسي القديم)
f1_nom = (sal1 - base_salary) * m1 if sal1 > 0 else 0
f2_nom = (sal2 - base_salary) * m2 if sal2 > 0 else 0
f3_nom = (sal3 - base_salary) * m3 if sal3 > 0 else 0
fp_nom = (sal_p - base_salary) * mp if sal_p > 0 else 0

# =========================
# عرض النتائج في جدول واحد
# =========================
st.divider()
st.subheader("3️⃣ كشف النتائج التفصيلي")

table_data = []
if m1 > 0: table_data.append({"المرحلة": "العلاوة الأولى", "الأشهر": m1, "الفرق الاسمي": f1_nom, "الفرق العام": f1_nom * rate})
if m2 > 0: table_data.append({"المرحلة": "العلاوة الثانية", "الأشهر": m2, "الفرق الاسمي": f2_nom, "الفرق العام": f2_nom * rate})
if m3 > 0: table_data.append({"المرحلة": "العلاوة الثالثة", "الأشهر": m3, "الفرق الاسمي": f3_nom, "الفرق العام": f3_nom * rate})
if mp > 0: table_data.append({"المرحلة": "الترفيع", "الأشهر": mp, "الفرق الاسمي": fp_nom, "الفرق العام": fp_nom * rate})

if table_data:
    st.table(table_data)
    
    total_nominal = f1_nom + f2_nom + f3_nom + fp_nom
    total_general = total_nominal * rate
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.metric("إجمالي الفرق الاسمي", f"{total_nominal:,.0f} دينار")
    with res_c2:
        st.success(f"المجموع الكلي للمستحق (الفرق العام): {total_general:,.1f} دينار")
else:
    st.warning("الرجاء إدخال تاريخ العلاوة الأولى وتاريخ نهاية الفترة على الأقل.")
