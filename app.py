import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات الذكية (تلقائي)", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl; text-align: right;}
    input, select {direction: rtl;}
    th, td {text-align: right !important;}
    div[data-testid="stMetricValue"] {font-size: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("⚡ حاسبة الفروقات (حساب الفرق تلقائياً)")
st.info("النظام يقوم بطرح الرواتب تلقائياً لحساب مقدار الفرق بناءً على تغير السنوات.")

# ---------------------------------------------------------
# 🔧 دوال الحساب المنطقي
# ---------------------------------------------------------

def get_months(start, end):
    """حساب الأشهر (DATEDIF M)"""
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_auto_diff(current_sal, current_date, prev_sal, prev_date, base_sal):
    """
    دالة لحساب الفرق تلقائياً بين الراتبين:
    - إذا سنة مختلفة: (الراتب الحالي - الراتب الأساسي)
    - إذا نفس السنة: (الراتب الحالي - الراتب السابق)
    """
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, "لا يوجد"
    
    # إذا كانت أول مرحلة (لا يوجد سابق)، تقارن بالأساس
    if not prev_date:
        diff = current_sal - base_sal
        return diff, diff, "عن الأساس (بداية)"
    
    # مقارنة السنوات
    if current_date.year > prev_date.year:
        # سنة جديدة -> العودة للأساس (تراكمي)
        diff = current_sal - base_sal
        return diff, diff, "سنة جديدة (عن الأساس)"
    else:
        # نفس السنة -> الفرق عن السابق فقط (تفاضلي)
        # هنا نستخدم الراتب السابق الفعلي للمرحلة السابقة
        reference_sal = prev_sal if prev_sal > 0 else base_sal
        diff = current_sal - reference_sal
        return diff, diff, "نفس السنة (عن السابق)"

# ---------------------------------------------------------
# 1️⃣ الإدخالات (Inputs)
# ---------------------------------------------------------
st.subheader("1. إدخال الرواتب والتواريخ")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 💰 الرواتب (المبالغ الكلية)")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=250, help="الراتب الذي يتم الطرح منه في السنوات الجديدة")
    s1 = st.number_input("الراتب بعد العلاوة الأولى", value=260)
    s2 = st.number_input("الراتب بعد العلاوة الثانية", value=270)
    s3 = st.number_input("الراتب بعد العلاوة الثالثة", value=0)
    sp = st.number_input("الراتب بعد الترفيع", value=300)

    st.write("---")
    degree = st.selectbox("الشهادة", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية/إعدادية"], index=3)
    rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية/إعدادية": 0.15}
    rate = rates[degree]

with col2:
    st.markdown("##### 📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة 2", value=date(2023, 1, 1))
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
    de = st.date_input("تاريخ نهاية الفترة", value=date(2024, 12, 1))

# ---------------------------------------------------------
# 2️⃣ المعالجة (Processing)
# ---------------------------------------------------------

# 1. تحديد تواريخ النهاية (Logic Skipping)
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de

# 2. حساب الأشهر
m1 = get_months(d1, end1)
m2 = get_months(d2, end2) if d2 else 0
m3 = get_months(d3, end3) if d3 else 0
mp = get_months(dp, de) if dp else 0

# 3. حساب الفروقات التلقائي (Auto Diff)

# -- العلاوة 1 --
diff1, _, note1 = calculate_auto_diff(s1, d1, base_sal, None, base_sal)
nom1 = diff1 * m1

# -- العلاوة 2 (تقارن بـ 1) --
diff2, _, note2 = calculate_auto_diff(s2, d2, s1, d1, base_sal)
nom2 = diff2 * m2

# -- العلاوة 3 (تقارن بـ 2 أو 1) --
prev_s_3 = s2 if s2 else s1
prev_d_3 = d2 if d2 else d1
diff3, _, note3 = calculate_auto_diff(s3, d3, prev_s_3, prev_d_3, base_sal)
nom3 = diff3 * m3

# -- الترفيع (يقارن بآخر مرحلة) --
if s3: prev_s_p, prev_d_p = s3, d3
elif s2: prev_s_p, prev_d_p = s2, d2
else: prev_s_p, prev_d_p = s1, d1

diff_p, _, note_p = calculate_auto_diff(sp, dp, prev_s_p, prev_d_p, base_sal)
nom_p = diff_p * mp

# 4. الحساب العام (النسبة)
gen1 = nom1 * rate
gen2 = nom2 * rate
gen3 = nom3 * rate
gen_p = nom_p * rate

# ---------------------------------------------------------
# 3️⃣ النتائج (Outputs)
# ---------------------------------------------------------
st.divider()
st.subheader("2. الجدول التفصيلي")

rows = []
# نعرض "مقدار الفرق المحتسب" (diff) لنريك كيف قام البرنامج بالطرح
if m1 > 0: rows.append(["العلاوة 1", m1, f"{diff1}", f"{nom1:,.0f}", f"{gen1:,.1f}", note1])
if m2 > 0: rows.append(["العلاوة 2", m2, f"{diff2}", f"{nom2:,.0f}", f"{gen2:,.1f}", note2])
if m3 > 0: rows.append(["العلاوة 3", m3, f"{diff3}", f"{nom3:,.0f}", f"{gen3:,.1f}", note3])
if mp > 0: rows.append(["الترفيع", mp, f"{diff_p}", f"{nom_p:,.0f}", f"{gen_p:,.1f}", note_p])

if rows:
    st.table([
        {"المرحلة": r[0], "الأشهر": r[1], "الفرق المحتسب (تلقائي)": r[2], "المجموع الاسمي": r[3], "المستحق العام": r[4], "ملاحظة": r[5]}
        for r in rows
    ])

    total_nom = nom1 + nom2 + nom3 + nom_p
    total_gen = gen1 + gen2 + gen3 + gen_p

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("إجمالي الفرق الاسمي")
        st.metric("Total Nominal", f"{total_nom:,.0f}")
    with c2:
        st.warning(f"نسبة الشهادة ({int(rate*100)}%)")
        st.metric("Ratio", degree)
    with c3:
        st.success("المبلغ المستحق النهائي")
        st.metric("Final Amount", f"{total_gen:,.1f}")

else:
    st.warning("يرجى إدخال التواريخ.")
