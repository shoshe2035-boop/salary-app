import streamlit as st
from datetime import date, datetime

# ---------------------------------------------------------
# إعدادات التنسيق المتقدمة
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, .main { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .report-header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 20px; }
    
    /* تنسيق الجدول ليكون متوافقاً تماماً مع الورق والنتائج */
    table { width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }
    th, td { border: 1px solid black !important; padding: 8px; text-align: center !important; overflow: hidden; }
    th { background-color: #f2f2f2 !important; font-weight: bold; }
    
    /* تحديد عرض الأعمدة لضمان المحاذاة */
    .col-t { width: 5%; }
    .col-desc { width: 35%; }
    .col-months { width: 10%; }
    .col-diff { width: 15%; }
    .col-total { width: 15%; }
    .col-note { width: 20%; }

    .total-row { background-color: #fdfdfd; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#1E3A8A; text-decoration:underline;">كشف احتساب الفروقات المالية</h2>', unsafe_allow_html=True)

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
with st.expander("📝 إدخال البيانات", expanded=True):
    emp_name = st.text_input("اسم الموظف الكامل", "")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
    
    col1, col2 = st.columns(2)
    with col1:
        s1 = st.number_input("راتب علاوة 1", value=0) * 1000
        s2 = st.number_input("راتب علاوة 2", value=0) * 1000
        s3 = st.number_input("راتب علاوة 3", value=0) * 1000
    with col2:
        sp = st.number_input("راتب الترفيع", value=0) * 1000
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
        de = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")

    st.write("---")
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        d1 = st.date_input("تاريخ علاوة 1", value=None, format="DD/MM/YYYY")
        d2 = st.date_input("تاريخ علاوة 2", value=None, format="DD/MM/YYYY")
    with c_d2:
        d3 = st.date_input("تاريخ علاوة 3", value=None, format="DD/MM/YYYY")
        dp = st.date_input("تاريخ الترفيع", value=None, format="DD/MM/YYYY")

# ---------------------------------------------------------
# منطق الحساب المحدث (V29)
# ---------------------------------------------------------
def get_m(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

rows = []
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
rate = rates.get(degree, 0)

# تحديد تواريخ النهاية لكل مرحلة بشكل متعاقب
end1 = (d2 or d3 or dp or de)
end2 = (d3 or dp or de)
end3 = (dp or de)
endp = de

# حساب العلاوة 1
if s1 > 0 and d1:
    m = get_m(d1, end1); diff = s1 - base_sal
    if m > 0: total_nominal += (diff * m); rows.append(["1", "علاوة سنوية رقم (1)", m, f"{diff:,.0f}", f"{diff*m:,.0f}", "نفس السنة"])

# حساب العلاوة 2
if s2 > 0 and d2:
    m = get_m(d2, end2); diff = s2 - s1
    if m > 0: total_nominal += (diff * m); rows.append(["2", "علاوة سنوية رقم (2)", m, f"{diff:,.0f}", f"{diff*m:,.0f}", "نفس السنة"])

# حساب العلاوة 3 (تم التأكد من تفعيلها هنا)
if s3 > 0 and d3:
    m = get_m(d3, end3); diff = s3 - s2
    if m > 0: total_nominal += (diff * m); rows.append(["3", "علاوة سنوية رقم (3)", m, f"{diff:,.0f}", f"{diff*m:,.0f}", "نفس السنة"])

# حساب الترفيع (معادلة الفرق عن الأساس في السنة الجديدة)
if sp > 0 and dp:
    last_d = (d3 or d2 or d1)
    if last_d and dp.year > last_d.year:
        f_diff = sp - base_sal # الترفيع - الأساس
        note = "سنة جديدة"
    else:
        f_diff = sp - (s3 or s2 or s1 or base_sal)
        note = "نفس السنة"
    
    m = get_m(dp, endp)
    if m > 0:
        total_nominal += (f_diff * m)
        rows.append(["4", "الترفيع الوظيفي", m, f"{f_diff:,.0f}", f"{f_diff*m:,.0f}", note])

# ---------------------------------------------------------
# عرض النتائج في جدول الطباعة
# ---------------------------------------------------------
if rows:
    st.markdown(f"""
    <div class="report-header">
        <h3>المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h3>
        <p>اسم الموظف: {emp_name if emp_name else '................'}</p>
    </div>
    <table>
        <thead>
            <tr>
                <th class="col-t">ت</th>
                <th class="col-desc">تفاصيل الاستحقاق</th>
                <th class="col-months">الأشهر</th>
                <th class="col-diff">الفرق الشهري</th>
                <th class="col-total">الاسمي الكلي</th>
                <th class="col-note">الملاحظة</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for r in rows:
        st.markdown(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>", unsafe_allow_html=True)
    
    total_gen = total_nominal * rate
    # صف المجاميع بمحاذاة الأعمدة
    st.markdown(f"""
            <tr class="total-row">
                <td colspan="4" style="text-align:left !important; padding-left:15px;">مجموع الفرق الاسمي</td>
                <td>{total_nominal:,.0f}</td>
                <td>دينار</td>
            </tr>
            <tr class="total-row" style="color:blue;">
                <td colspan="4" style="text-align:left !important; padding-left:15px;">المستحق الصافي ({int(rate*100)}%)</td>
                <td>{total_gen:,.0f}</td>
                <td>دينار</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top:50px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
        <div>منظم الجدول<br><br>__________</div>
        <div>التدقيق<br><br>__________</div>
        <div>مدير القسم<br><br>__________</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.button("🖨️ طباعة الكشف (Ctrl + P)")
else:
    st.info("أدخل البيانات ليتم عرض الكشف.")
