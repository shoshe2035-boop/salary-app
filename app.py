import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات الاحترافية", layout="wide")

st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl; text-align: right;}
    input, select {direction: rtl;}
    th, td {text-align: right !important;}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ حاسبة الفروقات (النسخة النهائية المستقرة)")
st.info("تم تعطيل التعبئة التلقائية المزعجة. لن تظهر نتائج إلا عند إدخال الرواتب.")

# ---------------------------------------------------------
# 🔧 دوال الحساب (المنطق المختلط المعتمد)
# ---------------------------------------------------------

def get_months(start, end):
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_allowance_logic(current_sal, current_date, prev_sal, prev_date):
    if not current_sal or current_sal == 0 or not current_date:
        return 0, 0, "لا يوجد"
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
        return 0, 0, "لا يوجد"
    if current_date.year > (prev_date.year if prev_date else current_date.year):
        diff = current_sal - base_sal
        return (current_sal - prev_sal), diff, "سنة جديدة (أساس)"
    else:
        ref_sal = prev_sal if prev_sal else base_sal
        diff = current_sal - ref_sal
        return diff, diff, "نفس السنة"

# ---------------------------------------------------------
# 1️⃣ الإدخالات (تم تصفير القيم الافتراضية لمنع التعبئة التلقائية)
# ---------------------------------------------------------
st.subheader("1. البيانات")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 💰 الرواتب")
    # تم تغيير القيمة الافتراضية من 250 إلى 0 لمنع الحساب المسبق
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0, key="base_sal")
    s1 = st.number_input("الراتب بعد العلاوة الأولى", value=0, key="s1")
    s2 = st.number_input("الراتب بعد العلاوة الثانية", value=0, key="s2")
    s3 = st.number_input("الراتب بعد العلاوة الثالثة", value=0, key="s3")
    sp = st.number_input("الراتب بعد الترفيع", value=0, key="sp")

    st.write("---")
    degree_options = ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"]
    degree = st.selectbox("التحصيل العلمي", degree_options, index=3)
    
    rates = {"دكتوراه": 1.00, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
    rate = rates.get(degree, 0)

with col2:
    st.markdown("##### 📅 التواريخ")
    # وضع التواريخ فارغة بشكل افتراضي
    d1 = st.date_input("تاريخ العلاوة 1", value=None)
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة", value=date.today())

# ---------------------------------------------------------
# 2️⃣ المعالجة المنطقية (مع شرط التحقق من البيانات)
# ---------------------------------------------------------

# شرط أمان: لا تحسب شيئاً إذا كان الراتب الأساسي صفر
if base_sal > 0 and d1:
    end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
    end2 = d3 if d3 else (dp if dp else de)
    end3 = dp if dp else de

    m1 = get_months(d1, end1)
    m2 = get_months(d2, end2) if d2 else 0
    m3 = get_months(d3, end3) if d3 else 0
    mp = get_months(dp, de) if dp else 0

    diff1_raw, diff1_final, note1 = calculate_allowance_logic(s1, d1, base_sal, None)
    nom1 = diff1_final * m1

    prev_s_2 = s1 if s1 > 0 else base_sal
    prev_d_2 = d1 if s1 > 0 else None
    diff2_raw, diff2_final, note2 = calculate_allowance_logic(s2, d2, prev_s_2, prev_d_2)
    nom2 = diff2_final * m2

    prev_s_3 = s2 if s2 > 0 else (s1 if s1 > 0 else base_sal)
    prev_d_3 = d2 if s2 > 0 else (d1 if s1 > 0 else None)
    diff3_raw, diff3_final, note3 = calculate_allowance_logic(s3, d3, prev_s_3, prev_d_3)
    nom3 = diff3_final * m3

    prev_s_p = s3 if s3 > 0 else (s2 if s2 else (s1 if s1 else base_sal))
    prev_d_p = d3 if d3 else (d2 if d2 else d1)
    diff_p_raw, diff_p_final, note_p = calculate_promotion_logic(sp, dp, prev_s_p, prev_d_p, base_sal)
    nom_p = diff_p_final * mp

    total_nom = nom1 + nom2 + nom3 + nom_p
    total_gen = total_nom * rate

    # 3️⃣ عرض النتائج
    st.divider()
    rows = []
    if m1 > 0: rows.append(["علاوة 1", m1, f"{diff1_final}", f"{nom1:,.0f}"])
    if m2 > 0: rows.append(["علاوة 2", m2, f"{diff2_final}", f"{nom2:,.0f}"])
    if m3 > 0: rows.append(["علاوة 3", m3, f"{diff3_final}", f"{nom3:,.0f}"])
    if mp > 0: rows.append(["ترفيع", mp, f"{diff_p_final}", f"{nom_p:,.0f}"])

    if rows:
        st.table([{"المرحلة": r[0], "أشهر": r[1], "الفرق": r[2], "الاسمي": r[3]} for r in rows])
        c_r1, c_r2 = st.columns(2)
        c_r1.metric("إجمالي الاسمي", f"{total_nom:,.0f}")
        c_r2.success(f"المستحق ({int(rate*100)}%): {total_gen:,.1f}")
else:
    st.warning("الرجاء إدخال الراتب الأساسي وتاريخ العلاوة الأولى لبدء الحساب.")
