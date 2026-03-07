import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة والطباعة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات الجماعي - مصطفى حسن", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, .stApp {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        font-family: 'Cairo', sans-serif !important;
    }

    /* تنسيق القائمة الجانبية */
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* تنسيق المدخلات */
    div[data-baseweb="input"], .stNumberInput input, .stTextInput input, .stSelectbox div {
        background-color: #000000 !important;
        color: #ffffff !important;
        direction: rtl !important;
    }
    
    label p { color: #000000 !important; font-weight: bold; font-size: 16px; }

    /* تنسيق التقرير للطباعة */
    .printable-report {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 30px;
        border: 2px solid #000000;
        margin-bottom: 50px;
        direction: rtl !important;
        page-break-after: always; /* كل موظف في صفحة */
    }

    .report-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .report-table th, .report-table td {
        border: 1px solid #000000 !important;
        padding: 10px;
        text-align: center !important;
        color: #000000 !important;
    }
    .report-table th { background-color: #eeeeee !important; }

    @media print {
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], button, .stButton {
            display: none !important;
        }
        .printable-report { border: 1px solid #000 !important; margin: 0 !important; width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة مخزن البيانات (Session State)
# ---------------------------------------------------------
if 'all_employees' not in st.session_state:
    st.session_state.all_employees = []
if 'current_actions' not in st.session_state:
    st.session_state.current_actions = []

# ---------------------------------------------------------
# القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ إدارة النظام")
    calc_mode = st.radio(
        "طريقة الاحتساب:",
        options=["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكم مستمر)"],
        index=1
    )
    st.write("---")
    st.write(f"👥 عدد الموظفين في القائمة: {len(st.session_state.all_employees)}")
    if st.button("🗑️ مسح جميع البيانات والبدء من جديد"):
        st.session_state.all_employees = []
        st.session_state.current_actions = []
        st.rerun()
    st.markdown("---")
    st.markdown("**إعداد المستشار:** مصطفى حسن")

# ---------------------------------------------------------
# واجهة الإدخال للموظف الحالي
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - م. مصطفى حسن</h1>', unsafe_allow_html=True)

with st.expander("👤 إدخال بيانات موظف جديد", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("اسم الموظف")
        base_sal = st.number_input("الراتب القديم (آلاف)", value=0) * 1000
    with c2:
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        end_date = st.date_input("تاريخ غلق الاحتساب", value=date.today())

    st.write("---")
    st.markdown("##### ➕ إضافة حركة (علاوة / ترفيع)")
    cc1, cc2, cc3 = st.columns(3)
    with cc1: n_type = st.selectbox("النوع", ["علاوة سنوية", "ترفيع وظيفي"])
    with cc2: n_sal = st.number_input("الراتب الجديد (آلاف)", value=0) * 1000
    with cc3: n_date = st.date_input("التاريخ", value=None)

    if st.button("📥 إضافة الحركة للموظف الحالي"):
        if n_sal > 0 and n_date:
            st.session_state.current_actions.append({"type": n_type, "salary": n_sal, "date": n_date})
            st.session_state.current_actions = sorted(st.session_state.current_actions, key=lambda x: x['date'])
            st.rerun()

    if st.session_state.current_actions:
        st.markdown("**حركات الموظف الحالية:**")
        st.table(st.session_state.current_actions)
        if st.button("💾 حفظ الموظف المكتمل إلى القائمة العامة"):
            if emp_name:
                emp_data = {
                    "name": emp_name,
                    "degree": degree,
                    "base": base_sal,
                    "end": end_date,
                    "actions": st.session_state.current_actions.copy(),
                    "mode": calc_mode
                }
                st.session_state.all_employees.append(emp_data)
                st.session_state.current_actions = [] # تصفير الحركات للموظف القادم
                st.success(f"تم حفظ بيانات {emp_name} بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم الموظف قبل الحفظ")

# ---------------------------------------------------------
# دالة الحساب (نفس المنطق الأصلي الخاص بك)
# ---------------------------------------------------------
def calculate_employee_report(emp):
    def adjust_date(d): return d.replace(day=1) + timedelta(days=31) if d.day >= 25 else d
    def get_months(s, e):
        s = adjust_date(s)
        return (e.year - s.year) * 12 + (e.month - s.month) if s < e else 0

    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    curr_rate = rates.get(emp['degree'], 0)
    
    rows_html = ""
    total_nominal = 0
    cum_diff = 0
    p_sal = emp['base']
    p_year = None

    for i, curr in enumerate(emp['actions']):
        b_diff = curr['salary'] - p_sal
        if p_year is None:
            eff_diff = b_diff; note = "بداية"
        else:
            is_new_year = (curr['date'].year > p_year)
            if emp['mode'] == "المضاعفة دائماً (تراكم مستمر)" or is_new_year:
                eff_diff = b_diff + cum_diff; note = "تراكمي"
            else:
                eff_diff = b_diff; note = "نفس السنة"

        cum_diff += b_diff
        e_date = emp['actions'][i+1]['date'] if i < len(emp['actions'])-1 else emp['end']
        months = get_months(curr['date'], e_date)
        if i == len(emp['actions'])-1: months += 1

        if months > 0:
            sub = eff_diff * months
            total_nominal += sub
            rows_html += f"<tr><td>{i+1}</td><td>{curr['type']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub:,}</td><td>{note}</td></tr>"
        p_sal, p_year = curr['salary'], curr['date'].year
    
    return rows_html, total_nominal, total_nominal * curr_rate

# ---------------------------------------------------------
# عرض ومعاينة القائمة الجماعية
# ---------------------------------------------------------
if st.session_state.all_employees:
    st.markdown("---")
    st.markdown('<h3 class="no-print">📋 كشف الموظفين المنجزين</h3>', unsafe_allow_html=True)
    
    # عرض ملخص بسيط للموظفين المضافين
    summary_data = [{"الاسم": e['name'], "الشهادة": e['degree'], "عدد الحركات": len(e['actions'])} for e in st.session_state.all_employees]
    st.table(summary_data)

    if st.button("🖨️ طباعة كافة التقارير (A4)", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    # توليد التقارير للطباعة
    for emp in st.session_state.all_employees:
        rows, t_nominal, t_net = calculate_employee_report(emp)
        report_html = f"""
        <div class="printable-report">
            <div style="text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 20px;">
                <h3 style="margin:0;">المديرية العامة لتربية محافظة الديوانية</h3>
                <p style="margin:5px;">كشف فروقات الرواتب - م. مصطفى حسن</p>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom: 10px; font-weight:bold;">
                <span>اسم الموظف: {emp['name']}</span>
                <span>الشهادة: {emp['degree']}</span>
            </div>
            <table class="report-table">
                <thead>
                    <tr><th>ت</th><th>نوع الحركة</th><th>أشهر</th><th>الفرق الشهري</th><th>الاسمي الكلي</th><th>الملاحظة</th></tr>
                </thead>
                <tbody>
                    {rows}
                    <tr style="background-color: #f0f0f0; font-weight:bold;">
                        <td colspan="4">مجموع الفرق الاسمي</td><td colspan="2">{t_nominal:,} د.ع</td>
                    </tr>
                    <tr style="background-color: #e0e0e0; font-weight:bold;">
                        <td colspan="4">المستحق الصافي للقبض</td><td colspan="2">{t_net:,.0f} د.ع</td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:40px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
                <div>منظم الجدول<br><br>__________</div>
                <div>التدقيق<br><br>__________</div>
                <div>مدير القسم<br><br>__________</div>
            </div>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
