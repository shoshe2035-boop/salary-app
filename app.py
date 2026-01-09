import streamlit as st
from datetime import date, datetime

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
        .stTable { width: 100% !important; border-collapse: collapse; }
        .report-header { border: 2px solid #000; padding: 10px; margin-bottom: 20px; }
        body { padding: 0; margin: 0; }
    }
    .report-header { text-align: center; border: 2px solid #000; padding: 15px; margin-bottom: 20px; border-radius: 5px; background-color: #fcfcfc; }
    .center-title { text-align: center; color: #1E3A8A; font-size: 26px; font-weight: bold; margin-bottom: 10px; text-decoration: underline; }
    .signature-section { margin-top: 60px; display: flex; justify-content: space-around; text-align: center; font-weight: bold; }
    th { background-color: #f2f2f2 !important; color: black !important; border: 1px solid #000 !important; font-weight: bold; }
    td { border: 1px solid #000 !important; padding: 8px !important; }
    .stNumberInput, .stDateInput { margin-bottom: -10px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# الهوية الشخصية (Sidebar)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ شعبة حسابات الثانوي")
    st.write("**مصطفى حسن صكبان**")
    st.write("📍 محافظة الديوانية")
    st.write("📞 07702360003")
    st.divider()
    st.success("نظام الإدخال السريع مفعّل ✅")

def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# ---------------------------------------------------------
# واجهة الإدخال السريع (تختفي عند الطباعة)
# ---------------------------------------------------------
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.info("💡 ملاحظة: المبالغ تُدخل مختصرة (مثال: 302) والتواريخ يمكن كتابتها يدوياً بصيغة يوم/شهر/سنة.")

c1, c2 = st.columns(2)
with c1:
    emp_name = st.text_input("اسم الموظف الكامل", "")
    base_sal = st.number_input("الراتب الاسمي القديم", value=0) * 1000
    s1 = st.number_input("راتب العلاوة 1", value=0) * 1000
    s2 = st.number_input("راتب العلاوة 2", value=0) * 1000
    s3 = st.number_input("راتب العلاوة 3", value=0) * 1000
    sp = st.number_input("راتب الترفيع", value=0) * 1000

with c2:
    degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)
    # استخدام format="DD/MM/YYYY" للسماح بالكتابة اليدوية السهلة
    d1 = st.date_input("تاريخ العلاوة 1", value=None, format="DD/MM/YYYY")
    d2 = st.date_input("تاريخ العلاوة 2", value=None, format="DD/MM/YYYY")
    d3 = st.date_input("تاريخ العلاوة 3", value=None, format="DD/MM/YYYY")
    dp = st.date_input("تاريخ الترفيع", value=None, format="DD/MM/YYYY")
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# منطق الحساب المعتمد
# ---------------------------------------------------------
rows = []
total_nom = 0
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
rate = rates.get(degree, 0)

end1, end2, end3 = (d2 or d3 or dp or de), (d3 or dp or de), (dp or de)

def calc_diff_logic(curr, prev, date_curr, date_prev):
    if not curr or not date_curr: return 0, ""
    diff = curr - (prev if prev else 0)
    if date_prev and date_curr.year > date_prev.year:
        return diff * 2, "سنة جديدة (×2)"
    return diff, "نفس السنة"

# تطبيق الحسابات
if s1 > 0 and d1:
    diff, note = calc_diff_logic(s1, base_sal, d1, None)
    m = get_months(d1, end1)
    if m > 0: 
        total_nom += (diff * m)
        rows.append({"ت": "1", "تفاصيل الاستحقاق": "علاوة سنوية رقم (1)", "الأشهر": m, "الفرق الشهري": f"{diff:,.0f}", "الاسمي": f"{diff*m:,.0f}", "الملاحظة": note})

if s2 > 0 and d2:
    diff, note = calc_diff_logic(s2, s1, d2, d1)
    m = get_months(d2, end2)
    if m > 0:
        total_nom += (diff * m)
        rows.append({"ت": "2", "تفاصيل الاستحقاق": "علاوة سنوية رقم (2)", "الأشهر": m, "الفرق الشهري": f"{diff:,.0f}", "الاسمي": f"{diff*m:,.0f}", "الملاحظة": note})

if s3 > 0 and d3:
    ps, pd = (s2, d2) if s2 > 0 else (s1, d1)
    diff, note = calc_diff_logic(s3, ps, d3, pd)
    m = get_months(d3, end3)
    if m > 0:
        total_nom += (diff * m)
        rows.append({"ت": "3", "تفاصيل الاستحقاق": "علاوة سنوية رقم (3)", "الأشهر": m, "الفرق الشهري": f"{diff:,.0f}", "الاسمي": f"{diff*m:,.0f}", "الملاحظة": note})

if sp > 0 and dp:
    ps, pd = (s3, d3) if s3 > 0 else ((s2, d2) if s2 > 0 else (s1, d1))
    check_year = pd.year if pd else dp.year
    if dp.year > check_year:
        diff_calc = sp - base_sal
        diff_disp = sp - ps
        note = "سنة جديدة (أساس)"
    else:
        diff_calc = sp - ps
        diff_disp = diff_calc
        note = "نفس السنة"
    m = get_months(dp, de)
    if m > 0:
        total_nom += (diff_calc * m)
        rows.append({"ت": "4", "تفاصيل الاستحقاق": "الترفيع الوظيفي", "الأشهر": m, "الفرق الشهري": f"{diff_disp:,.0f}", "الاسمي": f"{diff_calc*m:,.0f}", "الملاحظة": note})

# ---------------------------------------------------------
# تقرير الطباعة الرسمي A4
# ---------------------------------------------------------
if rows:
    st.markdown(f"""
    <div class="report-header">
        <h3 style="margin:0;">جمهورية العراق - وزارة التربية</h3>
        <h4 style="margin:5px;">المديرية العامة لتربية محافظة الديوانية</h4>
        <p style="margin:0;">الشؤون المالية - شعبة حسابات الثانوي</p>
    </div>
    <div class="center-title">كشف احتساب الفروقات المالية</div>
    <table style="width:100%; margin-bottom:10px; border:none;">
        <tr style="border:none;">
            <td style="border:none; text-align:right;"><b>اسم الموظف:</b> {emp_name if emp_name else '................................'}</td>
            <td style="border:none; text-align:left;"><b>التحصيل العلمي:</b> {degree}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.table(rows)
    
    total_gen = total_nom * rate
    st.markdown(f"""
    <div style='border: 1px solid #000; padding: 10px; background-color: #f9f9f9; line-height: 1.6;'>
        <div style="display: flex; justify-content: space-between;">
            <span><b>مجموع الفرق الاسمي الكلي:</b> {total_nom:,.0f} دينار</span>
            <span><b>المبلغ المستحق الصافي (العام):</b> {total_gen:,.0f} دينار</span>
        </div>
        <p style="margin-top:10px; font-size:12px;">* احتُسب المبلغ الصافي بناءً على نسبة الشهادة المعتمدة ({int(rate*100)}%).</p>
    </div>
    <div class="signature-section">
        <div><p>منظم الجدول</p><br><p>________________</p></div>
        <div><p>التدقيق</p><br><p>________________</p></div>
        <div><p>المصادقة / مدير القسم</p><br><p>________________</p></div>
    </div>
    <p style="font-size:10px; text-align:left; margin-top:20px;">تاريخ استخراج الكشف: {datetime.now().strftime('%d/%m/%Y')}</p>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="no-print" style="text-align:center; margin-top:20px;">', unsafe_allow_html=True)
    st.button("🖨️ جاهز للطباعة (Ctrl + P)")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    st.warning("الرجاء إدخال البيانات أعلاه (الرواتب والتواريخ) ليظهر كشف الطباعة.")
    st.markdown('</div>', unsafe_allow_html=True)
