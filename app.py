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
        body { background-color: white !important; color: black !important; }
    }
    .report-header { text-align: center; border: 2px solid #000; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
    .center-title { text-align: center; color: #1E3A8A; font-size: 26px; font-weight: bold; margin-bottom: 10px; text-decoration: underline; }
    .signature-section { margin-top: 60px; display: flex; justify-content: space-around; text-align: center; font-weight: bold; }
    th { background-color: #f2f2f2 !important; color: black !important; border: 1px solid #000 !important; font-weight: bold; text-align: center !important; }
    td { border: 1px solid #000 !important; padding: 8px !important; text-align: center !important; }
    .total-row { background-color: #f9f9f9; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛡️ شعبة حسابات الثانوي")
    st.write("**مصطفى حسن صكبان**")
    st.write("📍 محافظة الديوانية")
    st.write("📞 07702360003")
    st.divider()
    st.info("النسخة المطورة: جدول شامل ومجاميع نهائية (V22)")

def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

# دالة لتنسيق التاريخ بدون أصفار بادئة
def format_date_simple(d):
    if d:
        return f"{d.day}/{d.month}/{d.year}"
    return ""

# ---------------------------------------------------------
# 1️⃣ واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.title("⚖️ حاسبة الفروقات (الإدخال السريع)")
c1, c2 = st.columns(2)
with c1:
    emp_name = st.text_input("اسم الموظف الكامل", "")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
    s1, s2, s3 = st.number_input("راتب علاوة 1", 0)*1000, st.number_input("راتب علاوة 2", 0)*1000, st.number_input("راتب علاوة 3", 0)*1000
    sp = st.number_input("راتب الترفيع الوظيفي", value=0) * 1000
with c2:
    degree = st.selectbox("التحصيل العلمي (الشهادة)", ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)
    d1 = st.date_input("تاريخ العلاوة 1", value=None, format="DD/MM/YYYY")
    d2 = st.date_input("تاريخ العلاوة 2", value=None, format="DD/MM/YYYY")
    d3 = st.date_input("تاريخ العلاوة 3", value=None, format="DD/MM/YYYY")
    dp = st.date_input("تاريخ الترفيع", value=None, format="DD/MM/YYYY")
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2️⃣ العمليات الحسابية
# ---------------------------------------------------------
rows = []
total_nom = 0
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
rate = rates.get(degree, 0)

end1, end2, end3 = (d2 or d3 or dp or de), (d3 or dp or de), (dp or de)

def calc_logic(curr, prev, d_curr, d_prev):
    if not curr or not d_curr: return 0, ""
    diff = curr - (prev if prev else 0)
    note = "سنة جديدة (×2)" if (d_prev and d_curr.year > d_prev.year) else "نفس السنة"
    return (diff * 2 if note == "سنة جديدة (×2)" else diff), note

if s1 > 0 and d1:
    df, note = calc_logic(s1, base_sal, d1, None)
    m = get_months(d1, end1)
    if m > 0: total_nom += (df * m); rows.append([1, "علاوة سنوية رقم (1)", m, f"{df:,.0f}", f"{df*m:,.0f}", note])

if s2 > 0 and d2:
    df, note = calc_logic(s2, s1, d2, d1)
    m = get_months(d2, end2)
    if m > 0: total_nom += (df * m); rows.append([2, "علاوة سنوية رقم (2)", m, f"{df:,.0f}", f"{df*m:,.0f}", note])

if s3 > 0 and d3:
    ps, pd = (s2, d2) if s2 > 0 else (s1, d1)
    df, note = calc_logic(s3, ps, d3, pd)
    m = get_months(d3, end3)
    if m > 0: total_nom += (df * m); rows.append([3, "علاوة سنوية رقم (3)", m, f"{df:,.0f}", f"{df*m:,.0f}", note])

if sp > 0 and dp:
    ps, pd = (s3, d3) if s3 > 0 else ((s2, d2) if s2 > 0 else (s1, d1))
    diff_calc = sp - base_sal if (pd and dp.year > pd.year) else sp - ps
    m = get_months(dp, de)
    if m > 0: total_nom += (diff_calc * m); rows.append([4, "الترفيع الوظيفي", m, f"{diff_calc:,.0f}", f"{diff_calc*m:,.0f}", "سنة جديدة (أساس)" if (pd and dp.year > pd.year) else "نفس السنة"])

# ---------------------------------------------------------
# 3️⃣ التقرير النهائي للطباعة
# ---------------------------------------------------------
if rows:
    total_gen = total_nom * rate
    st.markdown(f"""
    <div class="report-header">
        <h3 style="margin:0;">المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h3>
        <p style="margin:5px;">شعبة حسابات الثانوي</p>
    </div>
    <div class="center-title">كشف احتساب الفروقات المالية</div>
    <div style="display: flex; justify-content: space-between; margin-bottom:10px;">
        <span><b>اسم الموظف:</b> {emp_name if emp_name else '................'}</span>
        <span><b>التحصيل العلمي:</b> {degree}</span>
        <span><b>تاريخ الاستخراج:</b> {format_date_simple(date.today())}</span>
    </div>
    <table style="width:100%;">
        <thead>
            <tr>
                <th style="width:5%;">ت</th>
                <th style="width:30%;">تفاصيل الاستحقاق</th>
                <th style="width:10%;">الأشهر</th>
                <th style="width:20%;">الفرق الشهري</th>
                <th style="width:20%;">الاسمي الكلي</th>
                <th style="width:15%;">الملاحظة</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for r in rows:
        st.markdown(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>", unsafe_allow_html=True)
    
    # صفوف المجاميع مدمجة في أسفل الجدول كما في التصميم السابق
    st.markdown(f"""
            <tr class="total-row">
                <td colspan="4" style="text-align:left; padding-left:20px;">المجموع الكلي للفرق الاسمي</td>
                <td colspan="2">{total_nom:,.0f} دينار</td>
            </tr>
            <tr class="total-row" style="color:#1E3A8A; font-size:18px;">
                <td colspan="4" style="text-align:left; padding-left:20px;">المجموع الكلي للفرق العام (بعد النسبة {int(rate*100)}%)</td>
                <td colspan="2">{total_gen:,.0f} دينار</td>
            </tr>
        </tbody>
    </table>
    <div class="signature-section">
        <div><p>منظم الجدول</p><br><p>________________</p></div>
        <div><p>التدقيق</p><br><p>________________</p></div>
        <div><p>المصادقة / مدير القسم</p><br><p>________________</p></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="no-print" style="text-align:center; margin-top:20px;"><button onclick="window.print()">🖨️ طباعة التقرير الفوري</button></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    st.info("الرجاء إدخال الرواتب والتواريخ ليتم توليد جدول الفروقات.")
    st.markdown('</div>', unsafe_allow_html=True)
