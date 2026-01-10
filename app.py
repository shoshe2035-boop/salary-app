import streamlit as st
from datetime import date, datetime
import io

# ---------------------------------------------------------
# إعدادات الصفحة والتنسيق المتجاوب للموبايل
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .main {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* تحسين العرض على الموبايل */
    @media (max-width: 640px) {
        .stTable { display: block; overflow-x: auto; }
        .main-title { font-size: 20px !important; }
        .report-header { font-size: 12px !important; }
    }

    .report-header { text-align: center; border: 1px solid #000; padding: 10px; margin-bottom: 15px; background: #fff; color: #000; }
    .center-title { text-align: center; color: #1E3A8A; font-size: 22px; font-weight: bold; margin-bottom: 10px; }
    
    /* تنسيق الجدول الرسمي */
    table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; color: black; }
    th, td { border: 1px solid black !important; padding: 6px; text-align: center !important; font-size: 14px; }
    th { background-color: #f2f2f2 !important; }

    .signature-box { margin-top: 30px; display: flex; justify-content: space-around; text-align: center; font-weight: bold; color: black; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<h2 class="center-title">حاسبة الفروقات (الإدخال السريع)</h2>', unsafe_allow_html=True)

with st.expander("📝 إدخال البيانات (اضغط للفتح/الإغلاق)", expanded=True):
    emp_name = st.text_input("اسم الموظف الكامل", "")
    base_sal = st.number_input("الراتب الاسمي القديم", value=0) * 1000
    
    col_sal1, col_sal2 = st.columns(2)
    with col_sal1:
        s1 = st.number_input("راتب علاوة 1", 0) * 1000
        s2 = st.number_input("راتب علاوة 2", 0) * 1000
    with col_sal2:
        s3 = st.number_input("راتب علاوة 3", 0) * 1000
        sp = st.number_input("راتب الترفيع", 0) * 1000

    degree = st.selectbox("التحصيل العلمي", ["دكتوراه", "ماجستير", "دبلوم", "بكالوريوس", "اعدادية", "متوسطة", "ابتدائية", "أمية"], index=3)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        d1 = st.date_input("تاريخ علاوة 1", value=None, format="D/M/YYYY")
        d2 = st.date_input("تاريخ علاوة 2", value=None, format="D/M/YYYY")
    with col_d2:
        d3 = st.date_input("تاريخ علاوة 3", value=None, format="D/M/YYYY")
        dp = st.date_input("تاريخ الترفيع", value=None, format="D/M/YYYY")
    
    de = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="D/M/YYYY")

# ---------------------------------------------------------
# منطق الحساب
# ---------------------------------------------------------
rows = []
total_nom = 0
rates = {"دكتوراه": 1.0, "ماجستير": 0.75, "دبلوم": 0.55, "بكالوريوس": 0.45, "اعدادية": 0.25, "متوسطة": 0.15, "ابتدائية": 0.15, "أمية": 0.15}
rate = rates.get(degree, 0)

def get_m(s, e):
    if not s or not e or s >= e: return 0
    return (e.year - s.year) * 12 + (e.month - s.month)

end1 = (d2 or d3 or dp or de)
end2 = (d3 or dp or de)
end3 = (dp or de)

# حساب العلاوات والترفيع (نفس المنطق المعتمد)
if s1 > 0 and d1:
    m = get_m(d1, end1); diff = s1 - base_sal
    if m > 0: total_nom += (diff * m); rows.append([1, "علاوة 1", m, f"{diff:,.0f}", f"{diff*m:,.0f}"])

if s2 > 0 and d2:
    m = get_m(d2, end2); diff = s2 - s1
    if m > 0: total_nom += (diff * m); rows.append([2, "علاوة 2", m, f"{diff:,.0f}", f"{diff*m:,.0f}"])

if sp > 0 and dp:
    m = get_m(dp, de); diff = sp - (s3 or s2 or s1 or base_sal)
    if m > 0: total_nom += (diff * m); rows.append([4, "ترفيع", m, f"{diff:,.0f}", f"{diff*m:,.0f}"])

# ---------------------------------------------------------
# عرض التقرير بصيغة متوافقة مع الموبايل
# ---------------------------------------------------------
if rows:
    st.markdown("---")
    st.markdown(f"""
    <div class="report-header">
        <h4 style="margin:0;">المديرية العامة لتربية محافظة الديوانية</h4>
        <p style="margin:5px;">قسم الشؤون المالية - شعبة حسابات الثانوي</p>
    </div>
    <div class="center-title">كشف احتساب الفروقات المالية</div>
    <p style="text-align:right;"><b>الموظف:</b> {emp_name} | <b>التاريخ:</b> {de.day}/{de.month}/{de.year}</p>
    """, unsafe_allow_html=True)

    # عرض الجدول
    st.write(f"**التحصيل:** {degree}")
    html_table = "<table><thead><tr><th>ت</th><th>التفاصيل</th><th>أشهر</th><th>الفرق</th><th>الاسمي</th></tr></thead><tbody>"
    for r in rows:
        html_table += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
    
    total_gen = total_nom * rate
    html_table += f"<tr style='font-weight:bold; background:#eee;'><td colspan='4'>المجموع الاسمي</td><td>{total_nom:,.0f}</td></tr>"
    html_table += f"<tr style='font-weight:bold; color:blue;'><td colspan='4'>الصافي المستحق</td><td>{total_gen:,.0f}</td></tr>"
    html_table += "</tbody></table>"
    
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("""
    <div class="signature-box">
        <div>منظم الجدول</div>
        <div>التدقيق</div>
        <div>مدير القسم</div>
    </div>
    """, unsafe_allow_html=True)

    # زر التحميل كبديل للطباعة المباشرة ليعمل على الموبايل
    st.download_button(
        label="📥 حفظ الكشف (PDF/Text) للطباعة",
        data=f"كشف فروقات الموظف: {emp_name}\nالمجموع الاسمي: {total_nom:,.0f}\nالمستحق الصافي: {total_gen:,.0f}",
        file_name=f"فروقات_{emp_name}.txt",
        mime="text/plain"
    )
else:
    st.info("الرجاء إدخال البيانات لعرض الكشف.")
