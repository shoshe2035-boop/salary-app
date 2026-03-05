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

    /* حل مشكلة ألوان المدخلات ورؤوس الجداول */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #111111 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    label p { color: #000000 !important; font-weight: bold; font-size: 16px; }

    /* تنسيق الجداول لمنع اختفاء النصوص (أسود على أسود) */
    table { width: 100%; border-collapse: collapse; color: black !important; }
    th { 
        background-color: #e0e0e0 !important; 
        color: black !important; 
        font-weight: bold !important;
        border: 1px solid black !important;
    }
    td { border: 1px solid black !important; color: black !important; padding: 8px; text-align: center; }

    /* كارت الطباعة A4 */
    .employee-card {
        background-color: white !important;
        padding: 30px;
        border: 2px solid black;
        margin-bottom: 40px;
        page-break-after: always;
    }

    @media print {
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], button { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة البيانات - مسح شامل لتفادي KeyError
# ---------------------------------------------------------
if 'all_employees' not in st.session_state: st.session_state.all_employees = []
if 'temp_actions' not in st.session_state: st.session_state.temp_actions = []

with st.sidebar:
    st.header("⚙️ الخيارات")
    if st.button("🔄 تصفير النظام بالكامل (حل مشكلة KeyError)"):
        st.session_state.all_employees = []
        st.session_state.temp_actions = []
        st.rerun()
    st.write("---")
    calc_mode = st.radio("الاحتساب:", ["المضاعفة في سنة جديدة", "المضاعفة دائماً"], index=1)
    st.markdown("**إعداد:** م. مصطفى حسن")

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - مصطفى حسن</h1>', unsafe_allow_html=True)

with st.expander("👤 إدخال بيانات الموظف", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("اسم الموظف")
        b_sal = st.number_input("الراتب القديم (بالآلاف)", value=0) * 1000
    with c2:
        deg = st.selectbox("الشهادة", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        e_date = st.date_input("نهاية الاحتساب", value=date.today())

    st.write("---")
    st.markdown("##### ➕ إضافة حركة (علاوة / ترفيع)")
    ac1, ac2, ac3, ac4 = st.columns([2, 2, 2, 2])
    with ac1: a_type = st.selectbox("النوع", ["علاوة سنوية", "ترفيع وظيفي"])
    with ac2: a_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0) * 1000
    with ac3: a_date = st.date_input("تاريخ الاستحقاق", value=None)
    with ac4: a_order = st.text_input("رقم الأمر")

    if st.button("✅ إضافة الحركة"):
        if a_sal > 0 and a_date:
            # استخدام مفاتيح إنجليزية داخلياً لتجنب الأخطاء
            st.session_state.temp_actions.append({
                "type": a_type, "order": a_order if a_order else "---",
                "salary": a_sal, "date": a_date
            })
            st.session_state.temp_actions = sorted(st.session_state.temp_actions, key=lambda x: x['date'])
            st.rerun()

    if st.session_state.temp_actions:
        st.markdown("**المعاينة قبل الحفظ:**")
        # تحويل الأسماء للعرض فقط لتظل واضحة
        display_list = [{"النوع": x['type'], "الأمر": x['order'], "التاريخ": x['date'], "الراتب": x['salary']} for x in st.session_state.temp_actions]
        st.table(display_list)
        
        if st.button("💾 حفظ الموظف نهائياً"):
            if name:
                st.session_state.all_employees.append({
                    "name": name, "degree": deg, "base": b_sal, "end": e_date, 
                    "actions": st.session_state.temp_actions.copy(), "mode": calc_mode
                })
                st.session_state.temp_actions = []; st.rerun()

# ---------------------------------------------------------
# معالجة التقارير
# ---------------------------------------------------------
def process_data(emp):
    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    rate = rates.get(emp['degree'], 0)
    def adj(d): return d.replace(day=1) + timedelta(days=31) if d.day >= 25 else d
    def diff_m(s, e):
        s, e = adj(s), adj(e)
        return (e.year - s.year) * 12 + (e.month - s.month) if e > s else 0

    rows, total_nom, cum_diff, p_sal, p_year = [], 0, 0, emp['base'], None
    for i, curr in enumerate(emp['actions']):
        # الوصول الآمن للبيانات لتجنب KeyError
        curr_sal = curr.get('salary', 0)
        curr_date = curr.get('date', date.today())
        
        b_diff = curr_sal - p_sal
        if p_year is None: eff_diff, note = b_diff, "بداية"
        else:
            if emp['mode'] == "المضاعفة دائماً" or curr_date.year > p_year:
                eff_diff, note = b_diff + cum_diff, "تراكمي"
            else: eff_diff, note = b_diff, "نفس السنة"
        
        cum_diff += b_diff
        next_d = emp['actions'][i+1].get('date', emp['end']) if i < len(emp['actions'])-1 else emp['end']
        months = diff_m(curr_date, next_d) + (1 if i == len(emp['actions'])-1 else 0)
        
        if months > 0:
            sub = eff_diff * months
            total_nom += sub
            rows.append(f"<tr><td>{curr.get('type')}</td><td>{curr.get('order')}</td><td>{curr_date}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub:,}</td><td>{note}</td></tr>")
        p_sal, p_year = curr_sal, curr_date.year
    return rows, total_nom, total_nom * rate

if st.session_state.all_employees:
    st.markdown("---")
    if st.button("🖨️ طباعة التقارير (A4)", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    for emp in st.session_state.all_employees:
        rows, t_nom, t_net = process_data(emp)
        st.markdown(f"""
        <div class="employee-card">
            <h2 style="text-align:center;">مديرية تربية الديوانية - كشف فروقات</h2>
            <h4 style="text-align:center;">إعداد: م. مصطفى حسن</h4>
            <div style="display:flex; justify-content:space-between; font-weight:bold; margin-bottom:10px; border-bottom:1px solid black;">
                <span>الموظف: {emp['name']}</span>
                <span>الشهادة: {emp['degree']}</span>
                <span>تاريخ الغلق: {emp['end']}</span>
            </div>
            <table>
                <thead>
                    <tr><th>الحركة</th><th>رقم الأمر</th><th>تاريخ الاستحقاق</th><th>أشهر</th><th>الفرق</th><th>الاسمي</th><th>ملاحظات</th></tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                    <tr style="background-color:#eee; font-weight:bold;"><td colspan="5">المجموع الاسمي</td><td colspan="2">{t_nom:,}</td></tr>
                    <tr style="background-color:#ccc; font-weight:bold;"><td colspan="5">الصافي المستحق</td><td colspan="2">{t_net:,.0f}</td></tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
