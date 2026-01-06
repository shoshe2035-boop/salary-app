import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات V10 (المنطق المختلط)", layout="wide")

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

st.title("⚖️ حاسبة الفروقات (المنطق المختلط V10)")
st.info("""
القواعد المطبقة:
1. **العلاوات:** عند تغير السنة يتم **مضاعفة الفرق** (×2).
2. **الترفيع:** عند تغير السنة يتم **العودة للراتب الأساسي** (Old Nominal).
""")

# ---------------------------------------------------------
# 🔧 دوال الحساب
# ---------------------------------------------------------

def get_months(start, end):
    """حساب الأشهر (DATEDIF M)"""
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_allowance_logic(current_sal, current_date, prev_sal, prev_date):
    """
    منطق العلاوات:
    - سنة جديدة -> (الحالي - السابق) * 2
    - نفس السنة -> (الحالي - السابق)
    """
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, "لا يوجد"
    
    # التأكد من الراتب السابق (إذا لا يوجد نعتبره 0 لتجنب الخطأ، ولكن منطقياً يجب أن يمرر)
    ref_sal = prev_sal if prev_sal else 0
    step_diff = current_sal - ref_sal

    # إذا لم يوجد تاريخ سابق (أول علاوة)، نعتبرها فرق عادي
    if not prev_date:
        return step_diff, step_diff, "بداية (فرق عادي)"

    if current_date.year > prev_date.year:
        final_diff = step_diff * 2
        return step_diff, final_diff, f"سنة جديدة (مضاعفة: {step_diff}×2)"
    else:
        return step_diff, step_diff, "نفس السنة (فرق عادي)"

def calculate_promotion_logic(current_sal, current_date, prev_sal, prev_date, base_sal):
    """
    منطق الترفيع:
    - سنة جديدة -> (الحالي - الأساس)
    - نفس السنة -> (الحالي - السابق)
    """
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, "لا يوجد"
    
    if not prev_date: # حالة نادرة (ترفيع مباشر)
        diff = current_sal - base_sal
        return diff, diff, "عن الأساس (بداية)"

    if current_date.year > prev_date.year:
        # سنة جديدة -> العودة للأساس
        diff = current_sal - base_sal
        return (current_sal - prev_sal), diff, "سنة جديدة (عودة للأساس)"
    else:
        # نفس السنة -> الفرق عن السابق
        ref_sal = prev_sal if prev_sal else base_sal
        diff = current_sal - ref_sal
        return diff, diff, "نفس السنة (عن السابق)"

# ---------------------------------------------------------
# 1️⃣ الإدخالات
# ---------------------------------------------------------
st.subheader("1. البيانات")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 💰 الرواتب")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=250)
    s1 = st.number_input("الراتب بعد العلاوة الأولى", value=302)
    s2 = st.number_input("الراتب بعد العلاوة الثانية", value=308)
    s3 = st.number_input("الراتب بعد العلاوة الثالثة", value=314)
    sp = st.number_input("الراتب بعد الترفيع", value=320)

    st.write("---")
    st.markdown("##### 🎓 الشهادة")
    degree_options = ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"]
    degree = st.selectbox("التحصيل العلمي", degree_options, index=3)
    
    rates = {
        "دكتوراه": 1.00, "ماجستير": 0.75, "دبلوم": 0.55,
        "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15,
        "ابتدائية": 0.15, "أمية": 0.15
    }
    rate = rates.get(degree, 0)
    st.caption(f"النسبة: {int(rate*100)}%")

with col2:
    st.markdown("##### 📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة 2", value=date(2023, 1, 1))
    d3 = st.date_input("تاريخ العلاوة 3", value=date(2024, 6, 1))
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 12, 1))
    de = st.date_input("تاريخ نهاية الفترة", value=date(2025, 1, 1))

# ---------------------------------------------------------
# 2️⃣ المعالجة
# ---------------------------------------------------------

# تحديد التواريخ النهائية
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de

# حساب الأشهر
m1 = get_months(d1, end1)
m2 = get_months(d2, end2) if d2 else 0
m3 = get_months(d3, end3) if d3 else 0
mp = get_months(dp, de) if dp else 0

# === حساب الفروقات (تطبيق المنطق المختلط) ===

# -- 1. العلاوة الأولى (دائماً تقارن بالأساس وتعتبر فرق عادي) --
# ملاحظة: العلاوة الأولى تعتبر step من الأساس
diff1_raw, diff1_final, note1 = calculate_allowance_logic(s1, d1, base_sal, None) 
# تعديل بسيط: العلاوة الأولى عادة لا تضاعف لأنها لا تملك تاريخ سابق للمقارنة، أو تعتمد على تاريخ التعيين
# هنا سنعتبرها فرق عادي (Step)
nom1 = diff1_final * m1

# -- 2. العلاوة الثانية (منطق العلاوات: مضاعفة) --
prev_s_2 = s1 if s1 > 0 else base_sal
prev_d_2 = d1 if s1 > 0 else None
diff2_raw, diff2_final, note2 = calculate_allowance_logic(s2, d2, prev_s_2, prev_d_2)
nom2 = diff2_final * m2

# -- 3. العلاوة الثالثة (منطق العلاوات: مضاعفة) --
if s2 > 0 and d2:
    prev_s_3, prev_d_3 = s2, d2
elif s1 > 0 and d1:
    prev_s_3, prev_d_3 = s1, d1
else:
    prev_s_3, prev_d_3 = base_sal, None

diff3_raw, diff3_final, note3 = calculate_allowance_logic(s3, d3, prev_s_3, prev_d_3)
nom3 = diff3_final * m3

# -- 4. الترفيع (منطق الترفيع: عودة للأساس) --
if s3 > 0 and d3:
    prev_s_p, prev_d_p = s3, d3
elif s2 > 0 and d2:
    prev_s_p, prev_d_p = s2, d2
elif s1 > 0 and d1:
    prev_s_p, prev_d_p = s1, d1
else:
    prev_s_p, prev_d_p = base_sal, None

diff_p_raw, diff_p_final, note_p = calculate_promotion_logic(sp, dp, prev_s_p, prev_d_p, base_sal)
nom_p = diff_p_final * mp

# الحساب العام
gen1 = nom1 * rate
gen2 = nom2 * rate
gen3 = nom3 * rate
gen_p = nom_p * rate

# ---------------------------------------------------------
# 3️⃣ النتائج
# ---------------------------------------------------------
st.divider()
st.subheader("2. الجدول التفصيلي")

rows = []
if m1 > 0: rows.append(["العلاوة 1", m1, f"{diff1_raw} ➞ {diff1_final}", f"{nom1:,.0f}", f"{gen1:,.1f}", note1])
if m2 > 0: rows.append(["العلاوة 2", m2, f"{diff2_raw} ➞ {diff2_final}", f"{nom2:,.0f}", f"{gen2:,.1f}", note2])
if m3 > 0: rows.append(["العلاوة 3", m3, f"{diff3_raw} ➞ {diff3_final}", f"{nom3:,.0f}", f"{gen3:,.1f}", note3])
if mp > 0: rows.append(["الترفيع", mp, f"{diff_p_raw} ➞ {diff_p_final}", f"{nom_p:,.0f}", f"{gen_p:,.1f}", note_p])

if rows:
    st.table([
        {"المرحلة": r[0], "الأشهر": r[1], "الفرق (المعتمد)", "الاسمي": r[3], "المستحق": r[4], "ملاحظة": r[5]}
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
        st.warning(f"النسبة ({int(rate*100)}%)")
        st.metric("Degree", degree)
    with c3:
        st.success("المستحق النهائي")
        st.metric("Final Amount", f"{total_gen:,.1f}")

else:
    st.warning("أدخل التواريخ.")
