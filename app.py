import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة - العنوان الجديد V3
# ---------------------------------------------------------
st.set_page_config(page_title="النظام المحدث V3", layout="wide")

# CSS لتنسيق الواجهة
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl;}
    h1 {color: #d62728;} 
</style>
""", unsafe_allow_html=True)

st.title("🔴 النظام الجديد V3 (تم التحديث بنجاح)")
st.info("هذه النسخة تحسب الفروقات بناءً على الفرق عن الراتب القديم مباشرة (نظام القفز).")

# ---------------------------------------------------------
# دوال الحساب
# ---------------------------------------------------------
def get_months_diff(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.subheader("1️⃣ البيانات المالية")
c1, c2, c3, c4 = st.columns(4)
with c1:
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=250)
with c2:
    s1 = st.number_input("راتب العلاوة 1", value=260)
with c3:
    s2 = st.number_input("راتب العلاوة 2", value=270)
with c4:
    sp = st.number_input("الراتب بعد الترفيع", value=300)

s3 = st.number_input("راتب العلاوة 3 (اختياري)", value=0)

st.subheader("2️⃣ التواريخ والشهادة")
d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
d2 = st.date_input("تاريخ العلاوة 2", value=date(2023, 1, 1))
d3 = st.date_input("تاريخ العلاوة 3", value=None)
dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
de = st.date_input("نهاية الفترة", value=date(2024, 12, 1))

degree = st.selectbox("الشهادة", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"], index=3)
rate = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية": 0.15}[degree]

# ---------------------------------------------------------
# منطق المعالجة
# ---------------------------------------------------------
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de

m1 = get_months_diff(d1, end1)
m2 = get_months_diff(d2, end2) if d2 else 0
m3 = get_months_diff(d3, end3) if d3 else 0
mp = get_months_diff(dp, de) if dp else 0

# الفروقات (عن الراتب الأساسي)
f1 = (s1 - base_sal) * m1 if s1 else 0
f2 = (s2 - base_sal) * m2 if s2 else 0
f3 = (s3 - base_sal) * m3 if s3 else 0
fp = (sp - base_sal) * mp if sp else 0

# ---------------------------------------------------------
# عرض النتائج
# ---------------------------------------------------------
st.divider()
st.subheader("3️⃣ جدول النتائج")

rows = []
if m1 > 0: rows.append(["العلاوة 1", m1, f"{f1:,.0f}", f"{f1 * rate:,.1f}"])
if m2 > 0: rows.append(["العلاوة 2", m2, f"{f2:,.0f}", f"{f2 * rate:,.1f}"])
if m3 > 0: rows.append(["العلاوة 3", m3, f"{f3:,.0f}", f"{f3 * rate:,.1f}"])
if mp > 0: rows.append(["الترفيع", mp, f"{fp:,.0f}", f"{fp * rate:,.1f}"])

if rows:
    st.table([{"المرحلة": r[0], "أشهر": r[1], "فرق اسمي": r[2], "فرق عام": r[3]} for r in rows])
    total = (f1+f2+f3+fp) * rate
    st.success(f"المستحق النهائي: {total:,.1f}")
else:
    st.warning("الرجاء إدخال التواريخ")
