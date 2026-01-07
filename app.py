import streamlit as st
from datetime import date

# ---------------------------------------------------------
# إعدادات الصفحة والتنسيق الجمالي
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    @media print {
        .no-print { display: none !important; }
        .stTable { width: 100% !important; }
        .report-header { border: 2px solid #000; padding: 10px; }
    }
    .report-header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
    .center-title { text-align: center; color: #1E3A8A; font-size: 28px; font-weight: bold; margin-bottom: 10px; }
    .signature-section { margin-top: 50px; display: flex; justify-content: space-around; text-align: center; font-weight: bold; }
    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #000 !important; }
    td { border: 1px solid #000 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ الهوية الشخصية")
    st.write("**مصطفى حسن صكبان**")
    st.write("🏢 شعبة حسابات الثانوي")
    st.write("📍 محافظة الديوانية")
    st.write("📞 07702360003")
    st.divider()
    st.info("ملاحظة: المبالغ تُدخل بالألوف (مثال: اكتب 296 بدلاً من 296000)")

def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# قسم الإدخال
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.warning("💡 ملاحظة: أدخل الراتب بالألوف (مثلاً: 296، 320، 550...) وسيقوم النظام بحسابها بالآلاف.")
c1, c2 = st.columns(2)
with c1:
    emp_name = st.text_input("اسم الموظف الكامل", "................................")
    # ضرب المدخلات بـ 1000 لتحويلها للرقم الفعلي
    base_sal = st.number_input("الراتب الاسمي القديم (بالألوف)", value=0) * 1000
    s1 = st.number_input("راتب علاوة 1 (بالألوف)", value=0) * 1000
    s2 = st.number_input("راتب علاوة 2 (بالألوف)", value=0) * 1000
    s3 = st.number_input("راتب علاوة 3 (بالألوف)", value=0) * 1000
    sp = st.number_input("راتب الترفيع (بالألوف)", value=0) * 1000
with c2:
    degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)
    d1 = st.date_input("تاريخ علاوة 1", value=None)
    d2, d3, dp = st.date_input("تاريخ علاوة 2", value=None), st.date_input("تاريخ علاوة 3", value=None), st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today())
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# العمليات الحسابية
# ---------------------------------------------------------
rows = []
total_nom = 0
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
rate = rates.get(degree, 0)

end1, end2, end3 = (d2 or d3 or dp or de), (d3 or dp or de), (dp or de)

# وظائف منطق الفرق (نفس القواعد السابقة)
def calc_diff(curr, prev, date_curr, date_prev):
    if not curr or not date_curr: return 0, ""
    diff = curr - (prev if prev else 0)
    if date_prev and date_curr.year > date_prev.year:
        return diff * 2, "سنة جديدة (×2)"
    return diff, "نفس السنة"

if s1 > 0 and d1:
    diff, note = calc_diff(s1, base_sal, d1, None)
    m = get_months(d1, end1)
    if m > 0: total_nom += (diff * m); rows.append({"ت": "1", "التفاصيل": "علاوة سنوية 1", "الأشهر": m, "الفرق الشهري": f"{diff:,.0f}", "الاسمي الكلي": f"{diff*m:,.0f}", "ملاحظة": note})

if s2 > 0 and d2:
    diff, note = calc_diff(s2, s1 or base_sal, d2, d1 if s1 > 0 else None)
    m = get_months(d2, end2)
    if m > 0: total_nom += (diff * m); rows.append({"ت": "2", "التفاصيل": "علاوة سنوية 2", "الأشهر": m, "الفرق الشهري": f"{diff:,.0f}", "الاسمي الكلي": f"{diff*m:,.0f}", "ملاحظة": note})

if s3 > 0 and d3:
    ps, pd = (s2, d2) if s2 > 0 else ((s1, d1) if s1 > 0 else (base_sal, None))
    diff, note = calc_diff(s3, ps, d3, pd)
    m = get_months(d3, end3)
    if m > 0: total_nom += (diff * m); rows.append({"ت": "3", "التفاصيل": "علاوة سنوية 3", "الأشهر": m, "الفرق الشهري": f"{diff:,.0f}", "الاسمي الكلي": f"{diff*m:,.0f}", "ملاحظة": note})

if sp > 0 and dp:
    ps, pd = (s3, d3) if s3 > 0 else ((s2, d2) if s2 > 0 else ((s1, d1) if s1 > 0 else (base_sal, None)))
    check_year = pd.year if pd else dp.year
    if dp.year > check_year:
        diff_show = sp - (ps if ps else base_sal)
        diff_calc = sp - base_sal
        note = "سنة جديدة (عودة للأساس)"
    else:
        diff_calc = sp - (ps if ps else base_sal)
        diff_show = diff_calc
        note = "نفس السنة"
    m = get_months(dp, de)
    if m > 0: total_nom += (diff_calc * m); rows.append({"ت": "4", "التفاصيل": "الترفيع الوظيفي", "الأشهر": m, "الفرق الشهري": f"{diff_show:,.0f}", "الاسمي الكلي": f"{diff_calc*m:,.0f}", "ملاحظة": note})

# ---------------------------------------------------------
# عرض التقرير النهائي للطباعة
# ---------------------------------------------------------
if rows:
    st.markdown("---")
    st.markdown(f"""
    <div class="report-header">
        <h3>وزارة التربية - المديرية العامة لتربية محافظة الديوانية</h3>
        <p>قسم الشؤون المالية - شعبة حسابات الثانوي</p>
    </div>
    <div class="center-title">جدول احتساب الفروقات المالية (A4)</div>
    <p style='text-align:right;'><b>اسم الموظف:</b> {emp_name} &nbsp;&nbsp;&nbsp; <b>التحصيل:</b> {degree}</p>
    """, unsafe_allow_html=True)
    
    st.table(rows)
    
    total_gen = total_nom * rate
    st.markdown(f"""
    <div style='border: 1px solid #000; padding: 10px; background-color: #f9f9f9;'>
        <p><b>إجمالي الفرق الاسمي الكلي:</b> {total_nom:,.0f} دينار عراقي</p>
        <p><b>المبلغ المستحق النهائي (صافي العام):</b> <span style='font-size: 20px; color: #1E3A8A;'>{total_gen:,.0f} دينار</span></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="signature-section">
        <div><p>منظم الجدول</p><br><p>________________</p></div>
        <div><p>التدقيق</p><br><p>________________</p></div>
        <div><p>مصادقة مدير القسم</p><br><p>________________</p></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="no-print" style="margin-top:20px;">', unsafe_allow_html=True)
    st.info("للتحميل أو الطباعة: اضغط Ctrl + P")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("أدخل المبالغ (مثال: 296) والتواريخ لعرض التقرير.")
