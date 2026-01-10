import streamlit as st
from datetime import date, datetime

# ---------------------------------------------------------
# 1. إعدادات التصميم المتجاوب (Responsive Design)
# ---------------------------------------------------------
st.set_page_config(page_title="حاسبة الفروقات - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .main {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* تحسين العرض على شاشات الموبايل */
    @media (max-width: 600px) {
        .stTable { display: block; overflow-x: auto; }
        div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }

    .report-header { 
        text-align: center; border: 2px solid #000; padding: 15px; 
        margin-bottom: 20px; border-radius: 8px; background-color: #ffffff;
    }
    
    .center-title { 
        text-align: center; color: #1E3A8A; font-size: 24px; 
        font-weight: bold; text-decoration: underline; margin-bottom: 15px;
    }

    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid black !important; padding: 10px; text-align: center !important; }
    th { background-color: #f2f2f2 !important; font-weight: bold; }
    
    .signature-section { 
        margin-top: 40px; display: flex; justify-content: space-around; 
        text-align: center; font-weight: bold; 
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. واجهة الإدخال (منظمة للموبايل)
# ---------------------------------------------------------
st.markdown('<div class="center-title">حاسبة الفروقات (مصطفى حسن صكبان)</div>', unsafe_allow_html=True)

with st.expander("📝 إدخال البيانات (اضغط هنا)", expanded=True):
    emp_name = st.text_input("اسم الموظف الكامل", "")
    
    # استخدام أعمدة تترتب عمودياً تلقائياً في الموبايل
    col1, col2 = st.columns(2)
    with col1:
        base_sal = st.number_input("الراتب الاسمي القديم", value=0) * 1000
        s1 = st.number_input("راتب علاوة 1", value=0) * 1000
        s2 = st.number_input("راتب علاوة 2", value=0) * 1000
    with col2:
        s3 = st.number_input("راتب علاوة 3", value=0) * 1000
        sp = st.number_input("راتب الترفيع", value=0) * 1000
        degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)

    st.markdown("---")
    st.write("📅 **التواريخ (يوم/شهر/سنة)**")
    
    c_date1, c_date2 = st.columns(2)
    with c_date1:
        # تم إصلاح التنسيق هنا لحل مشكلة الخطأ
        d1 = st.date_input("تاريخ علاوة 1", value=None, format="DD/MM/YYYY")
        d2 = st.date_input("تاريخ علاوة 2", value=None, format="DD/MM/YYYY")
    with c_date2:
        d3 = st.date_input("تاريخ علاوة 3", value=None, format="DD/MM/YYYY")
        dp = st.date_input("تاريخ الترفيع", value=None, format="DD/MM/YYYY")
    
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")

# ---------------------------------------------------------
# 3. منطق الحساب المعتمد
# ---------------------------------------------------------
def get_months(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

rows = []
total_nom = 0
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
rate = rates.get(degree, 0)

end1 = (d2 or d3 or dp or de)
end2 = (d3 or dp or de)
end3 = (dp or de)

# الحسابات
if s1 > 0 and d1:
    m = get_months(d1, end1); diff = s1 - base_sal
    if m > 0: total_nom += (diff * m); rows.append(["1", "علاوة سنوية 1", m, f"{diff:,.0f}", f"{diff*m:,.0f}"])

if s2 > 0 and d2:
    m = get_months(d2, end2); diff = s2 - s1
    if m > 0: total_nom += (diff * m); rows.append(["2", "علاوة سنوية 2", m, f"{diff:,.0f}", f"{diff*m:,.0f}"])

if sp > 0 and dp:
    m = get_months(dp, de); ps = (s3 or s2 or s1 or base_sal); diff = sp - ps
    if m > 0: total_nom += (diff * m); rows.append(["4", "الترفيع الوظيفي", m, f"{diff:,.0f}", f"{diff*m:,.0f}"])

# ---------------------------------------------------------
# 4. عرض كشف الطباعة (A4)
# ---------------------------------------------------------
if rows:
    st.markdown("---")
    st.markdown(f"""
    <div class="report-header">
        <h3 style="margin:0;">المديرية العامة لتربية محافظة الديوانية</h3>
        <p style="margin:5px;">قسم الشؤون المالية - شعبة حسابات الثانوي</p>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom:10px; font-weight:bold;">
        <span>الموظف: {emp_name if emp_name else '................'}</span>
        <span>الشهادة: {degree}</span>
    </div>
    <table>
        <thead>
            <tr>
                <th>ت</th><th>التفاصيل</th><th>أشهر</th><th>الفرق</th><th>الاسمي</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)

    for r in rows:
        st.markdown(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>", unsafe_allow_html=True)

    total_gen = total_nom * rate
    st.markdown(f"""
            <tr style="background:#f9f9f9; font-weight:bold;">
                <td colspan="4">مجموع الفرق الاسمي الكلي</td>
                <td>{total_nom:,.0f}</td>
            </tr>
            <tr style="background:#f0f7ff; font-weight:bold; color:#1E3A8A;">
                <td colspan="4">المجموع العام (المستحق الصافي)</td>
                <td>{total_gen:,.0f}</td>
            </tr>
        </tbody>
    </table>
    <div class="signature-section">
        <div><p>منظم الجدول</p><p>__________</p></div>
        <div><p>التدقيق</p><p>__________</p></div>
        <div><p>مدير القسم</p><p>__________</p></div>
    </div>
    <div style="margin-top:20px; text-align:left; font-size:12px;">تاريخ الاستخراج: {de.day}/{de.month}/{de.year}</div>
    """, unsafe_allow_html=True)

    # زر الطباعة (يعمل في المتصفحات التي تدعم الطباعة)
    st.markdown('<div style="text-align:center; margin-top:30px;" class="no-print"><button onclick="window.print()" style="padding:10px 20px; cursor:pointer;">🖨️ طباعة التقرير (A4)</button></div>', unsafe_allow_html=True)
else:
    st.info("الرجاء إدخال البيانات (الرواتب والتواريخ) ليتم توليد كشف الفروقات.")
