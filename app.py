import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات الذكية V5", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl;}
    div[data-testid="stMetricValue"] {font-size: 26px;}
    th {text-align: right !important;}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ نظام الفروقات (معالجة الترفيع الذكية)")
st.info("تم تحديث منطق الترفيع: يحسب الفرق عن 'الراتب القديم' إذا كانت السنة جديدة، وعن 'آخر علاوة' إذا كان في نفس السنة.")

# ---------------------------------------------------------
# دالة حساب الأشهر
# ---------------------------------------------------------
def get_months_diff(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# ---------------------------------------------------------
# 1️⃣ المدخلات
# ---------------------------------------------------------
st.subheader("1. البيانات المالية والتواريخ")
c1, c2 = st.columns(2)

with c1:
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=250)
    s1 = st.number_input("راتب العلاوة 1", value=260)
    s2 = st.number_input("راتب العلاوة 2", value=270)
    s3 = st.number_input("راتب العلاوة 3", value=0)
    sp = st.number_input("الراتب بعد الترفيع", value=300)
    
    degree = st.selectbox("الشهادة", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"], index=3)
    rate = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية": 0.15}[degree]

with c2:
    d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة 2", value=date(2023, 1, 1))
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
    de = st.date_input("تاريخ نهاية الفترة", value=date(2024, 12, 1))

# ---------------------------------------------------------
# 2️⃣ منطق المعالجة (تحديد الفترات)
# ---------------------------------------------------------
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de

m1 = get_months_diff(d1, end1)
m2 = get_months_diff(d2, end2) if d2 else 0
m3 = get_months_diff(d3, end3) if d3 else 0
mp = get_months_diff(dp, de) if dp else 0

# ---------------------------------------------------------
# 3️⃣ حساب الفروقات (تطبيق شرط الترفيع الجديد)
# ---------------------------------------------------------

# حساب فروقات العلاوات (دائماً عن الراتب الأساسي القديم حسب ملف الإكسل)
f1_nom = (s1 - base_sal) * m1 if s1 else 0
f2_nom = (s2 - base_sal) * m2 if s2 else 0
f3_nom = (s3 - base_sal) * m3 if s3 else 0

# --- منطق الترفيع الذكي ---
promotion_note = ""
fp_nom = 0

if dp and sp:
    # 1. تحديد تاريخ وراتب آخر مرحلة قبل الترفيع
    last_event_date = None
    last_event_salary = 0
    
    if d3: 
        last_event_date = d3
        last_event_salary = s3
    elif d2:
        last_event_date = d2
        last_event_salary = s2
    elif d1:
        last_event_date = d1
        last_event_salary = s1
    
    # 2. تطبيق الشرط
    if last_event_date:
        if dp.year > last_event_date.year:
            # سنة جديدة = مضاعفة (الراتب الاسمي القديم)
            fp_nom = (sp - base_sal) * mp
            promotion_note = "(سنة جديدة: عودة للأساس)"
        else:
            # نفس السنة = فرق الزيادة فقط (عن آخر علاوة)
            fp_nom = (sp - last_event_salary) * mp
            promotion_note = "(نفس السنة: فرق عن السابق)"
    else:
        # إذا كان الترفيع هو أول حدث
        fp_nom = (sp - base_sal) * mp

# حساب الفروقات العامة (بعد النسبة)
f1_gen = f1_nom * rate
f2_gen = f2_nom * rate
f3_gen = f3_nom * rate
fp_gen = fp_nom * rate

# ---------------------------------------------------------
# 4️⃣ عرض النتائج المفصلة
# ---------------------------------------------------------
st.divider()
st.subheader("2. التفاصيل")

rows = []
if m1 > 0: rows.append(["العلاوة الأولى", m1, f1_nom, f1_gen, ""])
if m2 > 0: rows.append(["العلاوة الثانية", m2, f2_nom, f2_gen, ""])
if m3 > 0: rows.append(["العلاوة الثالثة", m3, f3_nom, f3_gen, ""])
if mp > 0: rows.append(["الترفيع", mp, fp_nom, fp_gen, promotion_note])

if rows:
    # عرض الجدول
    st.table([
        {
            "المرحلة": r[0], 
            "الأشهر": r[1], 
            "الفرق الاسمي": f"{r[2]:,.0f}", 
            "الفرق العام": f"{r[3]:,.1f}",
            "ملاحظات": r[4]
        } 
        for r in rows
    ])

    # المجاميع النهائية
    total_nom = f1_nom + f2_nom + f3_nom + fp_nom
    total_gen = f1_gen + f2_gen + f3_gen + fp_gen

    st.markdown("---")
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.metric("المجموع الاسمي الكلي", f"{total_nom:,.0f} دينار")
    with c_res2:
        st.success(f"المستحق النهائي (العام): {total_gen:,.1f} دينار")
else:
    st.warning("الرجاء إدخال البيانات.")
