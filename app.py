import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة والبراندينج
# ---------------------------------------------------------
st.set_page_config(page_title="نظام فروقات الموظفين - مصطفى حسن", layout="wide")

# CSS متقدم للتعامل مع القائمة الجماعية وطباعة A4
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, .stApp {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        font-family: 'Cairo', sans-serif !important;
    }

    /* القائمة الجانبية السوداء */
    [data-testid="stSidebar"] { background-color: #000000 !important; color: white !important; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* المدخلات السوداء */
    div[data-baseweb="input"], div[data-baseweb="select"], .stSelectbox div, .stNumberInput input, .stTextInput input {
        background-color: #000000 !important;
        color: #ffffff !important;
        direction: rtl !important;
    }
    label p { color: #000000 !important; font-weight: bold; }

    /* تنسيق كشف الموظف للطباعة */
    .employee-card {
        background-color: white !important;
        color: black !important;
        padding: 20px;
        border: 2px solid black;
        margin-bottom: 30px;
        page-break-after: always; /* كل موظف في صفحة جديدة عند الطباعة */
    }

    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .report-table th, .report-table td {
        border: 1px solid black !important;
        padding: 8px;
        text-align: center !important;
        color: black !important;
    }
    .report-table th { background-color: #f0f0f0 !important; }

    /* إعدادات الطباعة A4 */
    @media print {
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], button {
            display: none !important;
        }
        .employee-card { border: 1px solid black !important; margin: 0; }
        body { background-color: white !important; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة مخزن البيانات
# ---------------------------------------------------------
if 'all_employees' not in st.session_state:
    st.session_state.all_employees = []
if 'temp_actions' not in st.session_state:
    st.session_state.temp_actions = []

# ---------------------------------------------------------
# القائمة الجانبية (الإعدادات)
# ---------------------------------------------------------
with st.sidebar:
    st.header("👤 إدارة النظام")
    calc_mode = st.radio("وضع الاحتساب الافتراضي:", 
                        ["المضاعفة في سنة جديدة", "المضاعفة دائماً (تراكمي)"], index=1)
    
    st.write("---")
    if st.button("🗑️ مسح قائمة الموظفين بالكامل"):
        st.session_state.all_employees = []
        st.rerun()
    
    st.write("---")
    st.markdown("👨‍💻 **المبرمج:** مصطفى حسن")

# ---------------------------------------------------------
# واجهة الإدخال (إضافة موظف جديد)
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - مصطفى حسن</h1>', unsafe_allow_html=True)

with st.expander("➕ إضافة موظف جديد للقائمة", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم الموظف")
        b_sal = st.number_input("الراتب الاسمي القديم", value=0, step=250)
    with col2:
        deg = st.selectbox("الشهادة", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        e_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today())

    st.markdown("---")
    st.subheader("📋 حركات الموظف (علاوات/ترفييع)")
    ac1, ac2, ac3 = st.columns([2, 2, 2])
    with ac1: a_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with ac2: a_sal = st.number_input("الراتب الجديد", value=0, step=250)
    with ac3: a_date = st.date_input("تاريخ الاستحقاق", value=None)

    if st.button("➕ إضافة هذه الحركة للموظف"):
        if a_sal > 0 and a_date:
            st.session_state.temp_actions.append({"type": a_type, "salary": a_sal, "date": a_date})
            st.session_state.temp_actions = sorted(st.session_state.temp_actions, key=lambda x: x['date'])
    
    # عرض الحركات المضافة حالياً للموظف قبل حفظه
    if st.session_state.temp_actions:
        st.table(st.session_state.temp_actions)
        if st.button("💾 حفظ الموظف وحركاته في القائمة"):
            if name:
                new_emp = {
                    "name": name, "degree": deg, "base": b_sal, 
                    "end": e_date, "actions": st.session_state.temp_actions.copy(),
                    "mode": calc_mode
                }
                st.session_state.all_employees.append(new_emp)
                st.session_state.temp_actions = [] # تصفير الحركات للموظف القادم
                st.success(f"تمت إضافة {name} بنجاح!")
                st.rerun()
            else: st.error("يرجى كتابة اسم الموظف")

# ---------------------------------------------------------
# عرض ومعالجة البيانات
# ---------------------------------------------------------
def calculate_diffs(emp):
    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    rate = rates.get(emp['degree'], 0)
    
    def adjust_date(d): return d.replace(day=1) + timedelta(days=31) if d.day >= 25 else d
    def get_months(s, e):
        s = adjust_date(s); e = adjust_date(e)
        if s >= e: return 0
        return (e.year - s.year) * 12 + (e.month - s.month)

    rows = []; total_nom = 0; cum_diff = 0; p_sal = emp['base']; p_year = None
    
    for i, curr in enumerate(emp['actions']):
        b_diff = curr['salary'] - p_sal
        if p_year is None: eff_diff = b_diff; note = "بداية"
        else:
            is_new_year = (curr['date'].year > p_year)
            if emp['mode'] == "المضاعفة دائماً (تراكمي)" or is_new_year:
                eff_diff = b_diff + cum_diff; note = "تراكمي"
            else:
                eff_diff = b_diff; note = "سنة واحدة"
        
        cum_diff += b_diff
        next_d = emp['actions'][i+1]['date'] if i < len(emp['actions'])-1 else emp['end']
        months = get_months(curr['date'], next_d)
        if i == len(emp['actions'])-1: months += 1
        
        if months > 0:
            sub = eff_diff * months
            total_nom += sub
            rows.append(f"<tr><td>{curr['type']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub:,}</td><td>{note}</td></tr>")
        p_sal = curr['salary']; p_year = curr['date'].year
    
    return rows, total_nom, total_nom * rate

# ---------------------------------------------------------
# منطقة الطباعة الكبرى
# ---------------------------------------------------------
if st.session_state.all_employees:
    st.markdown("---")
    st.markdown(f'<h3 class="no-print">👥 الموظفون المضافون حالياً: ({len(st.session_state.all_employees)})</h3>', unsafe_allow_html=True)
    
    # زر الطباعة الجماعي
    st.markdown('<div class="no-print" style="text-align:center; margin: 20px 0;">', unsafe_allow_html=True)
    if st.button("🖨️ طباعة كشوفات جميع الموظفين (A4)", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # توليد التقارير
    all_reports_html = ""
    for emp in st.session_state.all_employees:
        rows, t_nom, t_net = calculate_diffs(emp)
        report = f"""
        <div class="employee-card">
            <div style="text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 15px;">
                <h3 style="margin:0;">المديرية العامة لتربية محافظة الديوانية</h3>
                <p style="margin:5px;">كشف فروقات الموظف: {emp['name']} | م. مصطفى حسن</p>
            </div>
            <div style="display:flex; justify-content:space-between; font-weight:bold; margin-bottom:10px;">
                <span>الشهادة: {emp['degree']}</span>
                <span>تاريخ الغلق: {emp['end']}</span>
            </div>
            <table class="report-table">
                <thead>
                    <tr><th>الحركة</th><th>أشهر</th><th>الفرق</th><th>الاسمي</th><th>ملاحظة</th></tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                    <tr style="background-color:#eee; font-weight:bold;">
                        <td colspan="3">المجموع الاسمي</td>
                        <td colspan="2">{t_nom:,} دينار</td>
                    </tr>
                    <tr style="background-color:#ddd; font-weight:bold;">
                        <td colspan="3">الصافي المستحق للقبض</td>
                        <td colspan="2">{t_net:,.0f} دينار</td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:30px; display:flex; justify-content:space-around; text-align:center; font-size:12px;">
                <div>منظم الجدول<br>__________</div>
                <div>التدقيق والمراجعة<br>__________</div>
                <div>مدير الحسابات<br>__________</div>
            </div>
        </div>
        """
        all_reports_html += report
    
    st.markdown(all_reports_html, unsafe_allow_html=True)

else:
    st.info("القائمة فارغة حالياً. ابدأ بإضافة الموظفين من الأعلى.")
