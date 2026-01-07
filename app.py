import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات الشاملة", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl; text-align: right;}
    input, select {direction: rtl;}
    th, td {text-align: right !important;}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ حاسبة الفروقات (النسخة المرنة V12)")
st.info("يمكنك الآن حساب الترفيع وحده، أو العلاوات وحدها، أو الجميع معاً.")

# ---------------------------------------------------------
# 🔧 دوال الحساب
# ---------------------------------------------------------

def get_months(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_allowance_logic(current_sal, current_date, prev_sal, prev_date):
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, ""
    ref_sal = prev_sal if prev_sal else 0
    step_diff = current_sal - ref_sal
    if not prev_date:
        return step_diff, step_diff, "بداية"
    if current_date.year > prev_date.year:
        return step_diff, step_diff * 2, f"سنة جديدة (×2)"
    else:
        return step_diff, step_diff, "نفس السنة"

def calculate_promotion_logic(current_sal, current_date, prev_sal, prev_date, base_sal):
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, ""
    # إذا كانت سنة الترفيع أكبر من سنة آخر إجراء (أو سنة الترفيع نفسها إذا لم يوجد سابق)
    check_year = prev_date.year if prev_date else current_date.year
    if current_date.year > check_year:
        diff = current_sal - base_sal
        return (current_sal - (prev_sal if prev_sal else base_sal)), diff, "سنة جديدة (عودة للأساس)"
    else:
        ref_sal = prev_sal if prev_sal else base_sal
        diff = current_sal - ref_sal
        return diff, diff, "نفس السنة"

# ---------------------------------------------------------
# 1️⃣ الإدخالات
# ---------------------------------------------------------
st.subheader("1. البيانات")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 💰 الرواتب")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0)
    s1 = st.number_input("الراتب بعد العلاوة الأولى", value=0)
    s2 = st.number_input("الراتب بعد العلاوة الثانية", value=0)
    s3 = st.number_input("الراتب بعد العلاوة الثالثة", value=0)
    sp = st.number_input("الراتب بعد الترفيع", value=0)

    st.write("---")
    degree_options = ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"]
    degree = st.selectbox("التحصيل العلمي", degree_options, index=3)
    rates = {"دكتوراه": 1.00, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
    rate = rates.get(degree, 0)

with col2:
    st.markdown("##### 📅 التواريخ")
    d1 = st.date_input("تاريخ العلاوة 1", value=None)
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة", value=date.today())

# ---------------------------------------------------------
# 2️⃣ المعالجة المنطقية (بدون شروط منع)
# ---------------------------------------------------------

# تحديد التواريخ المتعاقبة
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de
endp = de

rows = []
total_nom = 0

# حساب العلاوة 1
if s1 > 0 and d1:
    d_raw, d_final, note = calculate_allowance_logic(s1, d1, base_sal, None)
    m = get_months(d1, end1)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["علاوة 1", m, d_final, f"{nom:,.0f}", note])

# حساب العلاوة 2
if s2 > 0 and d2:
    prev_s = s1 if s1 > 0 else base_sal
    prev_d = d1 if s1 > 0 else None
    d_raw, d_final, note = calculate_allowance_logic(s2, d2, prev_s, prev_d)
    m = get_months(d2, end2)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["علاوة 2", m, d_final, f"{nom:,.0f}", note])

# حساب العلاوة 3
if s3 > 0 and d3:
    prev_s = s2 if s2 > 0 else (s1 if s1 > 0 else base_sal)
    prev_d = d2 if s2 > 0 else (d1 if d1 else None)
    d_raw, d_final, note = calculate_allowance_logic(s3, d3, prev_s, prev_d)
    m = get_months(d3, end3)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["علاوة 3", m, d_final, f"{nom:,.0f}", note])

# حساب الترفيع (يعمل الآن حتى لو العلاوات فارغة)
if sp > 0 and dp:
    # البحث عن آخر راتب وتاريخ قبل الترفيع
    if s3 > 0: prev_s, prev_d = s3, d3
    elif s2 > 0: prev_s, prev_d = s2, d2
    elif s1 > 0: prev_s, prev_d = s1, d1
    else: prev_s, prev_d = base_sal, None
    
    d_raw, d_final, note = calculate_promotion_logic(sp, dp, prev_s, prev_d, base_sal)
    m = get_months(dp, endp)
    if m > 0:
        nom = d_final * m
        total_nom += nom
        rows.append(["الترفيع", m, d_final, f"{nom:,.0f}", note])

# ---------------------------------------------------------
# 3️⃣ النتائج
# ---------------------------------------------------------
if rows:
    st.divider()
    st.table([{"المرحلة": r[0], "أشهر": r[1], "الفرق الشهري": r[2], "الاسمي الكلي": r[3], "ملاحظة": r[4]} for r in rows])
    
    total_gen = total_nom * rate
    c1, c2 = st.columns(2)
    c1.metric("إجمالي الفرق الاسمي", f"{total_nom:,.0f}")
    c2.success(f"المستحق النهائي ({int(rate*100)}%): {total_gen:,.1f}")
else:
    st.warning("يرجى إدخال بيانات (راتب وتاريخ) لأي مرحلة لعرض النتائج.")
