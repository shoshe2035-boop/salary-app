import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة والتنسيق الجمالي المتطور
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تنسيق الشاشة والطباعة */
    html, body, [data-testid="stSidebar"], .main {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* تحسين شكل الورقة عند الطباعة */
    @media print {
        .no-print { display: none !important; }
        .stTable { width: 100% !important; font-size: 12pt !important; }
        .center-title { font-size: 24pt !important; }
        .footer { position: relative !important; border: none !important; }
    }

    .report-header {
        text-align: center;
        border: 2px solid #000;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 5px;
    }

    .center-title {
        text-align: center;
        color: #1E3A8A;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .signature-section {
        margin-top: 50px;
        display: flex;
        justify-content: space-around;
        text-align: center;
        font-weight: bold;
    }

    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #000 !important; }
    td { border: 1px solid #000 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# واجهة الإدخال (تختفي عند الطباعة)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ الهوية الشخصية")
    st.write("**مصطفى حسن صكبان**")
    st.write("🏢 شعبة حسابات الثانوي")
    st.write("📍 محافظة الديوانية")
    st.write("📞 07702360003")
    st.divider()
    st.caption("نسخة الطباعة المعتمدة A4")

# دوال الحساب
def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def calculate_allowance_logic(current_sal, current_date, prev_sal, prev_date):
    if not current_sal or not current_date: return 0, 0, ""
    ref_sal = prev_sal if prev_sal else 0
    step_diff = current_sal - ref_sal
    if not prev_date: return step_diff, step_diff, "بداية"
    if current_date.year > prev_date.year: return step_diff, step_diff * 2, "سنة جديدة"
    return step_diff, step_diff, "نفس السنة"

def calculate_promotion_logic(current_sal, current_date, prev_sal, prev_date, base_sal):
    if not current_sal or not current_date: return 0, 0, ""
    check_year = prev_date.year if prev_date else current_date.year
    if current_date.year > check_year:
        return (current_sal - (prev_sal if prev_sal else base_sal)), (current_sal - base_sal), "سنة جديدة (أساس)"
    return (current_sal - (prev_sal if prev_sal else base_sal)), (current_sal - (prev_sal if prev_sal else base_sal)), "نفس السنة"

# قسم الإدخال
st.markdown('<div class="no-print">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    emp_name = st.text_input("اسم الموظف الكامل", "................................")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0)
    s1, s2, s3, sp = st.number_input("علاوة 1", 0), st.number_input("علاوة 2", 0), st.number_input("علاوة 3", 0), st.number_input("الترفيع", 0)
with c2:
    degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)
    d1 = st.date_input("تاريخ علاوة 1", value=None)
    d2, d3, dp = st.date_input("تاريخ علاوة 2", value=None), st.date_input("تاريخ علاوة 3", value=None), st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today())
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# قسم المعاينة والطباعة
# ---------------------------------------------------------
rows = []
total_nom = 0
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
rate = rates.get(degree, 0)

# الحسابات (نفس منطق V17)
end1, end2, end3 = (d2 or d3 or dp or de), (d3 or dp or de), (dp or de)
if s1 > 0 and d1:
    dr, df, note = calculate_allowance_logic(s1, d1, base_sal, None)
    m = get_months(d1, end1)
    if m > 0: total_nom += (df * m); rows.append({"ت": "1", "تفاصيل الاستحقاق": "علاوة سنوية أولى", "الأشهر": m, "الفرق": df, "الاسمي": df*m, "ملاحظة": note})

if s2 > 0 and d2:
    dr, df, note = calculate_allowance_logic(s2, d2, s1 or base_sal, d1 if s1 > 0 else None)
    m = get_months(d2, end2)
    if m > 0: total_nom += (df * m); rows.append({"ت": "2", "تفاصيل الاستحقاق": "علاوة سنوية ثانية", "الأشهر": m, "الفرق": df, "الاسمي": df*m, "ملاحظة": note})

if s3 > 0 and d3:
    ps, pd = (s2, d2) if s2 > 0 else ((s1, d1) if s1 > 0 else (base_sal, None))
    dr, df, note = calculate_allowance_logic(s3, d3, ps, pd)
    m = get_months(d3, end3)
    if m > 0: total_nom += (df * m); rows.append({"ت": "3", "تفاصيل الاستحقاق": "علاوة سنوية ثالثة", "الأشهر": m, "الفرق": df, "الاسمي": df*m, "ملاحظة": note})

if sp > 0 and dp:
    ps, pd = (s3, d3) if s3 > 0 else ((s2, d2) if s2 > 0 else ((s1, d1) if s1 > 0 else (base_sal, None)))
    dr, df, note = calculate_promotion_logic(sp, dp, ps, pd, base_sal)
    m = get_months(dp, de)
    if m > 0: total_nom += (df * m); rows.append({"ت": "4", "تفاصيل الاستحقاق": "ترقية / ترفيع وظيفي", "الأشهر": m, "الفرق": df, "الاسمي": df*m, "ملاحظة": note})

if rows:
    st.markdown("---")
    # الترويسة الرسمية
    st.markdown(f"""
    <div class="report-header">
        <h3>جمهورية العراق - وزارة التربية</h3>
        <h4>المديرية العامة للتربية في محافظة الديوانية</h4>
        <p>قسم الشؤون المالية - شعبة حسابات الثانوي</p>
    </div>
    <div class="center-title">جدول احتساب الفروقات المالية</div>
    <p style='text-align:right;'><b>اسم الموظف:</b> {emp_name} &nbsp;&nbsp;&nbsp; <b>التحصيل العلمي:</b> {degree}</p>
    """, unsafe_allow_html=True)
    
    st.table(rows)
    
    total_gen = total_nom * rate
    st.markdown(f"""
    <div style='background-color: #f9f9f9; padding: 15px; border: 1px solid #000;'>
        <p><b>مجموع الفرق الاسمي الكلي:</b> {total_nom:,.0f} دينار</p>
        <p><b>المبلغ المستحق النهائي (بعد النسبة {int(rate*100)}%):</b> <span style='font-size: 18px; color: #1E3A8A;'>{total_gen:,.1f} دينار</span></p>
    </div>
    """, unsafe_allow_html=True)

    # التواقيع
    st.markdown(f"""
    <div class="signature-section">
        <div><p>منظم الجدول</p><br><p>________________</p></div>
        <div><p>التدقيق</p><br><p>________________</p></div>
        <div><p>مدير القسم</p><br><p>________________</p></div>
    </div>
    <div style='margin-top: 30px; text-align: left; font-size: 10px;'>تاريخ الطبع: {date.today()}</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="no-print" style="margin-top:20px;">', unsafe_allow_html=True)
    st.button("🖨️ اضغط Ctrl + P للطباعة المباشرة")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("أدخل البيانات لعرض التقرير.")
