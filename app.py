import streamlit as st
from datetime import date, datetime

# ---------------------------------------------------------
# إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, .main { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .report-header { text-align: center; border: 2px solid #000; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
    .center-title { text-align: center; color: #1E3A8A; font-size: 24px; font-weight: bold; text-decoration: underline; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid black !important; padding: 10px; text-align: center !important; }
    th { background-color: #f2f2f2 !important; font-weight: bold; }
    .total-row { background-color: #f9f9f9; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="center-title">كشف احتساب الفروقات المالية النهائي</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
with st.expander("📝 إدخال البيانات السريع", expanded=True):
    emp_name = st.text_input("اسم الموظف الكامل", "")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس - مثلاً 173)", value=0) * 1000
    
    col1, col2 = st.columns(2)
    with col1:
        s1 = st.number_input("راتب علاوة 1", value=0) * 1000
        s2 = st.number_input("راتب علاوة 2", value=0) * 1000
    with col2:
        s3 = st.number_input("راتب علاوة 3", value=0) * 1000
        sp = st.number_input("راتب الترفيع (مثلاً 210)", value=0) * 1000

    degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
    
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        d1 = st.date_input("تاريخ علاوة 1", value=None, format="DD/MM/YYYY")
        d2 = st.date_input("تاريخ علاوة 2", value=None, format="DD/MM/YYYY")
    with c_d2:
        d3 = st.date_input("تاريخ علاوة 3", value=None, format="DD/MM/YYYY")
        dp = st.date_input("تاريخ الترفيع", value=None, format="DD/MM/YYYY")
    
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")

# ---------------------------------------------------------
# منطق الحساب المعتمد (معادلة الترفيع المستحدثة)
# ---------------------------------------------------------
def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

rows = []
total_nominal_sum = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25}
rate = rates.get(degree, 0)

end1 = (d2 or d3 or dp or de)
end2 = (d3 or dp or de)
end3 = (dp or de)

# 1. حساب العلاوات
if s1 > 0 and d1:
    m = get_months(d1, end1); diff = s1 - base_sal
    total_nominal_sum += (diff * m); rows.append(["1", "علاوة سنوية رقم (1)", m, f"{diff:,.0f}", f"{diff*m:,.0f}", "نفس السنة"])

if s2 > 0 and d2:
    m = get_months(d2, end2); diff = s2 - s1
    total_nominal_sum += (diff * m); rows.append(["2", "علاوة سنوية رقم (2)", m, f"{diff:,.0f}", f"{diff*m:,.0f}", "نفس السنة"])

# 2. حساب الترفيع (تطبيق: الترفيع - الأساس القديم عند السنة الجديدة)
if sp > 0 and dp:
    last_action_date = (d3 or d2 or d1)
    # التحقق من شرط السنة الجديدة
    if last_action_date and dp.year > last_action_date.year:
        final_diff = sp - base_sal  # الفرق عن الأساس كما طلبت
        note = "سنة جديدة (الفرق عن الأساس)"
    else:
        prev_s = (s3 or s2 or s1 or base_sal)
        final_diff = sp - prev_s
        note = "نفس السنة"
    
    m = get_months(dp, de)
    if m > 0:
        total_nominal_sum += (final_diff * m)
        rows.append(["4", "الترفيع الوظيفي", m, f"{final_diff:,.0f}", f"{final_diff*m:,.0f}", note])

# ---------------------------------------------------------
# 3. عرض النتائج والمجاميع الكلية
# ---------------------------------------------------------
if rows:
    total_general_sum = total_nominal_sum * rate
    
    st.markdown(f"""
    <div class="report-header">
        <h3>المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h3>
        <p>اسم الموظف: {emp_name if emp_name else '................'}</p>
    </div>
    <table>
        <thead>
            <tr>
                <th>ت</th><th>تفاصيل الاستحقاق</th><th>الأشهر</th><th>الفرق الشهري</th><th>الاسمي الكلي</th><th>الملاحظة</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for r in rows:
        st.markdown(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>", unsafe_allow_html=True)
    
    # صفوف المجاميع مدمجة في أسفل الجدول
    st.markdown(f"""
            <tr class="total-row">
                <td colspan="4" style="text-align:right; padding-right:20px;">المجموع الكلي للفرق الاسمي</td>
                <td colspan="2">{total_nominal_sum:,.0f} دينار</td>
            </tr>
            <tr class="total-row" style="color:#1E3A8A;">
                <td colspan="4" style="text-align:right; padding-right:20px;">المجموع الكلي للفرق العام (المستحق الصافي)</td>
                <td colspan="2">{total_general_sum:,.0f} دينار</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top:40px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
        <div>منظم الجدول<br><br>__________</div>
        <div>التدقيق<br><br>__________</div>
        <div>مدير القسم<br><br>__________</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align:center; margin-top:30px;"><button onclick="window.print()">🖨️ طباعة التقرير النهائي</button></div>', unsafe_allow_html=True)
else:
    st.info("الرجاء إدخال البيانات أعلاه ليظهر الجدول والمجاميع.")
