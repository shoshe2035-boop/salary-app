import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة (تم تغيير العنوان لتعرف أن التحديث تم)
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة Excel النهائية", layout="wide")

# تنسيق الجداول والنصوص (RTL)
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    div.stButton > button {width: 100%;}
    .stTable {direction: rtl; text-align: right;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
    th, td {text-align: right !important;}
</style>
""", unsafe_allow_html=True)

st.title("📊 الحاسبة المطابقة للإكسل (Excel 2026)")
st.info("القاعدة المطبقة: في حال اختلاف السنة يتم الحساب عن 'الراتب الأساسي'، وفي حال تشابه السنة يتم الحساب عن 'الراتب السابق'.")

# ---------------------------------------------------------
# دوال الحساب
# ---------------------------------------------------------
def get_months(start, end):
    """حساب الفرق بالأشهر (DATEDIF)"""
    if not start or not end or start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_stage_diff(current_salary, current_date, prev_salary, prev_date, base_salary):
    """
    دالة ذكية تحدد المعادلة بناءً على السنة
    """
    if current_salary == 0 or not current_date:
        return 0, "لا يوجد"

    # الحالة الأولى: إذا لم يكن هناك تاريخ سابق (أول علاوة) -> دائماً عن الأساس
    if not prev_date:
        return current_salary - base_salary, "بداية (عن الأساس)"

    # مقارنة السنوات
    if current_date.year > prev_date.year:
        # سنة جديدة -> العودة للأساس (مضاعفة)
        return current_salary - base_salary, "سنة جديدة (عن الأساس)"
    else:
        # نفس السنة -> الفرق عن السابق فقط (بدون مضاعفة)
        return current_salary - prev_salary, "نفس السنة (عن السابق)"

# ---------------------------------------------------------
# 1️⃣ المدخلات
# ---------------------------------------------------------
st.subheader("1. إدخال البيانات")
c1, c2 = st.columns(2)

with c1:
    base_sal = st.number_input("الراتب الاسمي القديم", value=250)
    s1 = st.number_input("راتب العلاوة 1", value=260)
    s2 = st.number_input("راتب العلاوة 2", value=270)
    s3 = st.number_input("راتب العلاوة 3", value=0)
    sp = st.number_input("الراتب بعد الترفيع", value=300)
    
    st.write("---")
    degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "بكالوريوس", "أخرى/أمية"], index=3)
    # النسب حسب ملف الإكسل
    rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "بكالوريوس": 0.50, "أخرى/أمية": 0.15}
    rate = rates[degree]

with c2:
    d1 = st.date_input("تاريخ العلاوة 1", value=date(2022, 6, 1))
    d2 = st.date_input("تاريخ العلاوة 2", value=date(2023, 1, 1))
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=date(2024, 6, 1))
    de = st.date_input("تاريخ نهاية الفترة", value=date(2024, 12, 1))

# ---------------------------------------------------------
# 2️⃣ المعالجة المنطقية (Logic)
# ---------------------------------------------------------

# 1. تحديد التواريخ النهائية (تجاوز المراحل الفارغة)
end1 = d2 if d2 else (d3 if d3 else (dp if dp else de))
end2 = d3 if d3 else (dp if dp else de)
end3 = dp if dp else de

# 2. حساب عدد الأشهر
m1 = get_months(d1, end1)
m2 = get_months(d2, end2) if d2 else 0
m3 = get_months(d3, end3) if d3 else 0
mp = get_months(dp, de) if dp else 0

# 3. حساب الفروقات (تطبيق قاعدة السنوات)
# العلاوة الأولى (دائماً تقارن بالأساس)
diff1, type1 = calculate_stage_diff(s1, d1, base_sal, None, base_sal)
val1_nom = diff1 * m1

# العلاوة الثانية (تقارن بالأولى)
diff2, type2 = calculate_stage_diff(s2, d2, s1, d1, base_sal)
val2_nom = diff2 * m2

# العلاوة الثالثة (تقارن بالثانية، وإن لم توجد فبالأولى)
prev_s_for_3 = s2 if s2 else s1
prev_d_for_3 = d2 if d2 else d1
diff3, type3 = calculate_stage_diff(s3, d3, prev_s_for_3, prev_d_for_3, base_sal)
val3_nom = diff3 * m3

# الترفيع (يقارن بآخر مرحلة موجودة)
prev_s_for_p = s3 if s3 else (s2 if s2 else s1)
prev_d_for_p = d3 if d3 else (d2 if d2 else d1)
diff_p, type_p = calculate_stage_diff(sp, dp, prev_s_for_p, prev_d_for_p, base_sal)
val_p_nom = diff_p * mp

# 4. حساب القيم العامة (بعد ضرب النسبة)
val1_gen = val1_nom * rate
val2_gen = val2_nom * rate
val3_gen = val3_nom * rate
val_p_gen = val_p_nom * rate

# ---------------------------------------------------------
# 3️⃣ عرض النتائج (الجدول والمجاميع)
# ---------------------------------------------------------
st.divider()
st.subheader("2. التفاصيل والحسابات")

rows = []
if m1 > 0: rows.append(["العلاوة الأولى", m1, f"{val1_nom:,.0f}", f"{val1_gen:,.1f}", type1])
if m2 > 0: rows.append(["العلاوة الثانية", m2, f"{val2_nom:,.0f}", f"{val2_gen:,.1f}", type2])
if m3 > 0: rows.append(["العلاوة الثالثة", m3, f"{val3_nom:,.0f}", f"{val3_gen:,.1f}", type3])
if mp > 0: rows.append(["الترفيع", mp, f"{val_p_nom:,.0f}", f"{val_p_gen:,.1f}", type_p])

if rows:
    # عرض الجدول
    st.table([
        {
            "المرحلة": r[0],
            "عدد الأشهر": r[1],
            "الفرق الاسمي": r[2],
            "الفرق العام (المستحق)": r[3],
            "طريقة الحساب": r[4]
        }
        for r in rows
    ])
    
    # حساب المجاميع النهائية
    total_nominal_final = val1_nom + val2_nom + val3_nom + val_p_nom
    total_general_final = val1_gen + val2_gen + val3_gen + val_p_gen
    
    st.markdown("---")
    
    # عرض المجاميع بشكل منفصل وواضح
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.info("💵 المجموع الاسمي الكلي")
        st.metric("Total Nominal", f"{total_nominal_final:,.0f}")
        
    with res_col2:
        st.success("💰 المجموع الكلي المستحق (العام)")
        st.metric("Total General", f"{total_general_final:,.1f}")
        
else:
    st.warning("⚠️ يرجى إدخال التواريخ لعرض النتائج.")
