import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة - م. مصطفى حسن
# ---------------------------------------------------------
st.set_page_config(page_title="نظام فروقات الرواتب - مصطفى حسن", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, .stApp {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        font-family: 'Cairo', sans-serif !important;
    }

    /* القائمة الجانبية والمدخلات (ستايل داكن) */
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    div[data-baseweb="input"], div[data-baseweb="select"], .stSelectbox div, .stNumberInput input, .stTextInput input {
        background-color: #000000 !important;
        color: #ffffff !important;
        text-align: right !important;
    }
    label p { color: #000000 !important; font-weight: bold; }

    /* تنسيق كارت الموظف للطباعة الرسمية */
    .employee-card {
        background-color: white !important;
        color: black !important;
        padding: 40px;
        border: 2px solid black;
        margin-bottom: 50px;
        page-break-after: always;
        direction: rtl !important;
    }

    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    .report-table th, .report-table td {
        border: 1px solid black !important;
        padding: 12px;
        text-align: center !important;
        color: black !important;
        font-size: 15px;
    }
    .report-table th { background-color: #f2f2f2 !important; font-weight: bold; }

    /* تعديل محاذاة أسطر المجموع */
    .total-row td {
        text-align: left !important;
        padding-left: 20px;
        font-weight: bold;
    }

    @media print {
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], button { display: none !important; }
        .employee-card { border: 1px solid black !important; margin: 0; padding: 15mm; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة البيانات
# ---------------------------------------------------------
if 'all_employees' not in st.session_state: st.session_state.all_employees = []
if 'temp_actions' not in st.session_state: st.session_state.temp_actions = []

with st.sidebar:
    st.header("👤 خيارات النظام")
    calc_mode = st.radio("طريقة الاحتساب:", ["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكم مستمر)"], index=1)
    if st.button("🗑️ تفريغ القائمة"): 
        st.session_state.all_employees = []; st.rerun()
    st.write("---")
    st.markdown("**المبرمج:** م. مصطفى حسن")

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - مصطفى حسن</h1>', unsafe_allow_html=True)

with st.expander("➕ إضافة بيانات موظف جديد", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم الموظف")
        b_sal = st.number_input("الراتب القديم (آلاف)", value=0, step=250) * 1000
    with col2:
        deg = st.selectbox("الشهادة", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        e_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today())

    st.write("---")
    st.markdown("##### 📝 إضافة حركة (علاوة / ترفيع)")
    ac1, ac2, ac3, ac4 = st.columns([2, 2, 2, 2])
    with ac1: a_type = st.selectbox("النوع", ["علاوة سنوية", "ترفيع وظيفي"])
    with ac2: a_sal = st.number_input("الراتب الجديد (آلاف)", value=0, step=250) * 1000
    with ac3: a_date = st.date_input("تاريخ الاستحقاق", value=None)
    with ac4: a_order = st.text_input("رقم الأمر الإداري")

    if st.button("➕ إضافة الحركة"):
        if a_sal > 0 and a_date:
            st.session_state.temp_actions.append({
                "type": a_type, "salary": a_sal, "date": a_date, "order_no": a_order if a_order else "---"
            })
            st.session_state.temp_actions = sorted(st.session_state.temp_actions, key=lambda x: x['date'])
            st.rerun()

    if st.session_state.temp_actions:
        st.write("الحركات المضافة لهذا الموظف:")
        st.table(st.session_state.temp_actions)
        if st.button("💾 حفظ الموظف في القائمة النهائية"):
            if name:
                st.session_state.all_employees.append({
                    "name": name, "degree": deg, "base": b_sal, "end": e_date, 
                    "actions": st.session_state.temp_actions.copy(), "mode": calc_mode
                })
                st.session_state.temp_actions = []; st.success("تم الحفظ!"); st.rerun()
            else: st.error("أدخل الاسم!")

# ---------------------------------------------------------
# معالجة وعرض التقارير
# ---------------------------------------------------------
def process(emp):
    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    rate = rates.get(emp['degree'], 0)
    def adj(d): return d.replace(day=1) + timedelta(days=31) if d.day >= 25 else d
    def diff_m(s, e):
        s, e = adj(s), adj(e)
        return (e.year - s.year) * 12 + (e.month - s.month) if e > s else 0

    rows, total_nom, cum_diff, p_sal, p_year = [], 0, 0, emp['base'], None
    for i, curr in enumerate(emp['actions']):
        b_diff = curr['salary'] - p_sal
        if p_year is None: eff_diff, note = b_diff, "بداية"
        else:
            if emp['mode'] == "المضاعفة دائماً (تراكم مستمر)" or curr['date'].year > p_year:
                eff_diff, note = b_diff + cum_diff, "تراكمي"
            else: eff_diff, note = b_diff, "نفس السنة"
        
        cum_diff += b_diff
        next_d = emp['actions'][i+1]['date'] if i < len(emp['actions'])-1 else emp['end']
        months = diff_m(curr['date'], next_d) + (1 if i == len(emp['actions'])-1 else 0)
        
        if months > 0:
            sub = eff_diff * months
            total_nom += sub
            rows.append(f"<tr><td>{curr['type']}</td><td>{curr['order_no']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub:,}</td><td>{note}</td></tr>")
        p_sal, p_year = curr['salary'], curr['date'].year
    return rows, total_nom, total_nom * rate

if st.session_state.all_employees:
    st.markdown("---")
    if st.button("🖨️ طباعة جميع الكشوفات (A4)", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    for emp in st.session_state.all_employees:
        rows, t_nom, t_net = process(emp)
        st.markdown(f"""
        <div class="employee-card">
            <div style="text-align: center; border: 2px solid black; padding: 15px; margin-bottom: 25px;">
                <h2 style="margin:0;">المديرية العامة لتربية محافظة الديوانية</h2>
                <h3 style="margin:5px;">كشف فروقات الرواتب - م. مصطفى حسن</h3>
            </div>
            <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:18px; border-bottom:1px solid #000; padding-bottom:10px;">
                <span>الاسم: {emp['name']}</span>
                <span>الشهادة: {emp['degree']}</span>
                <span>تاريخ الغلق: {emp['end']}</span>
            </div>
            <table class="report-table">
                <thead>
                    <tr><th>نوع الحركة</th><th>رقم الأمر</th><th>الأشهر</th><th>الفرق الشهري</th><th>الاسمي الكلي</th><th>ملاحظات</th></tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                    <tr class="total-row" style="background-color:#f2f2f2;">
                        <td colspan="4">مجموع الفرق الاسمي</td>
                        <td colspan="2" style="text-align:center !important;">{t_nom:,} دينار</td>
                    </tr>
                    <tr class="total-row" style="background-color:#e6e6e6;">
                        <td colspan="4">الصافي المستحق (بعد نسبة الشهادة)</td>
                        <td colspan="2" style="text-align:center !important;">{t_net:,.0f} دينار</td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:60px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
                <div>منظم الجدول<br><br>__________</div>
                <div>التدقيق<br><br>__________</div>
                <div>مدير القسم<br><br>__________</div>
            </div>
            <div style="margin-top:30px; font-size:10px; text-align:left; color:#666;">تاريخ الطباعة: {date.today()}</div>
        </div>
        """, unsafe_allow_html=True)
