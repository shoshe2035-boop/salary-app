import streamlit as st
from datetime import date, timedelta

# إعدادات الصفحة
st.set_page_config(page_title="نظام فروقات الرواتب - مصطفى حسن", layout="wide")

# CSS المحدث لتصحيح الألوان ومنع التداخل
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* ضبط الصفحة */
    html, body, .stApp {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        font-family: 'Cairo', sans-serif !important;
        color: #000000 !important;
    }

    /* حقول الإدخال: خلفية رمادي غامق ونصوص بيضاء */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #2b2b2b !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    label p { color: #000000 !important; font-weight: bold; font-size: 16px; }

    /* الجداول: فرض خلفية فاتحة ونصوص سوداء */
    table { width: 100%; border-collapse: collapse; color: black !important; }
    th { 
        background-color: #d1d1d1 !important; 
        color: black !important; 
        font-weight: bold !important;
        border: 1px solid black !important;
        padding: 10px;
    }
    td { border: 1px solid black !important; color: black !important; padding: 8px; text-align: center; }

    /* كارت الطباعة */
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
# إدارة البيانات - استخدام مفاتيح موحدة لتجنب KeyError
# ---------------------------------------------------------
if 'all_employees' not in st.session_state: st.session_state.all_employees = []
if 'temp_actions' not in st.session_state: st.session_state.temp_actions = []

with st.sidebar:
    st.header("⚙️ الخيارات")
    if st.button("🔄 تصفير البيانات (إصلاح الأخطاء)"):
        st.session_state.all_employees = []
        st.session_state.temp_actions = []
        st.rerun()
    st.write("---")
    calc_mode = st.radio("طريقة احتساب الفروقات:", ["المضاعفة في سنة جديدة", "المضاعفة دائماً"], index=1)

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - مصطفى حسن</h1>', unsafe_allow_html=True)

with st.expander("👤 إدخال الموظف", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("اسم الموظف")
        b_sal = st.number_input("الراتب القديم (بالآلاف)", value=0) * 1000
    with c2:
        deg = st.selectbox("الشهادة", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        e_date = st.date_input("نهاية الاحتساب", value=date.today())

    st.write("---")
    # مدخلات الحركة
    ac1, ac2, ac3, ac4 = st.columns([2, 2, 2, 2])
    with ac1: a_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with ac2: a_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0) * 1000
    with ac3: a_date = st.date_input("التاريخ", value=None)
    with ac4: a_order = st.text_input("رقم الأمر")

    if st.button("✅ إضافة الحركة"):
        if a_sal > 0 and a_date:
            st.session_state.temp_actions.append({
                "type": a_type, "order": a_order if a_order else "---",
                "salary": a_sal, "date": a_date
            })
            # ترتيب الحركات لضمان دقة الحساب التراكمي
            st.session_state.temp_actions = sorted(st.session_state.temp_actions, key=lambda x: x['date'])
            st.rerun()

    if st.session_state.temp_actions:
        st.markdown("**المعاينة الحالية:**")
        # عرض البيانات بأسماء مفهومة
        display = [{"النوع": x['type'], "الأمر": x['order'], "التاريخ": x['date'], "الراتب": x['salary']} for x in st.session_state.temp_actions]
        st.table(display)
        
        if st.button("💾 حفظ الموظف"):
            if name:
                st.session_state.all_employees.append({
                    "name": name, "degree": deg, "base": b_sal, "end": e_date, 
                    "actions": st.session_state.temp_actions.copy(), "mode": calc_mode
                })
                st.session_state.temp_actions = []; st.rerun()

# ---------------------------------------------------------
# محرك الحسابات (المنطق المصحح)
# ---------------------------------------------------------
def calculate(emp):
    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    rate = rates.get(emp['degree'], 0)
    
    rows, total_nom, cum_diff, p_sal, p_year = [], 0, 0, emp['base'], None
    
    for i, curr in enumerate(emp['actions']):
        # الفرق المباشر بين هذا الراتب والسابق
        b_diff = curr['salary'] - p_sal
        
        # التراكمي: نجمع الفروقات دائماً
        cum_diff += b_diff
        
        # المنطق الشرطي (سنة جديدة أو دائماً)
        if p_year is None:
            eff_diff = b_diff
            note = "بداية"
        else:
            if emp['mode'] == "المضاعفة دائماً":
                eff_diff = cum_diff
                note = "تراكمي"
            elif curr['date'].year > p_year:
                eff_diff = cum_diff
                note = "سنة جديدة"
            else:
                eff_diff = b_diff
                note = "نفس السنة"
        
        # حساب المدة (بسيط)
        next_date = emp['actions'][i+1]['date'] if i < len(emp['actions'])-1 else emp['end']
        months = ((next_date.year - curr['date'].year) * 12 + (next_date.month - curr['date'].month))
        if i == len(emp['actions'])-1: months += 1
        
        if months > 0:
            total_nom += (eff_diff * months)
            rows.append(f"<tr><td>{curr['type']}</td><td>{curr['order']}</td><td>{curr['date']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{eff_diff * months:,}</td><td>{note}</td></tr>")
        
        p_sal = curr['salary']
        p_year = curr['date'].year
        
    return rows, total_nom, total_nom * rate

# ---------------------------------------------------------
# عرض النتائج
# ---------------------------------------------------------
if st.session_state.all_employees:
    st.markdown("---")
    if st.button("🖨️ طباعة التقارير"):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    for emp in st.session_state.all_employees:
        rows, t_nom, t_net = calculate(emp)
        st.markdown(f"""
        <div class="employee-card">
            <h3 style="text-align:center;">كشف فروقات الرواتب </h3>
            <div style="display:flex; justify-content:space-between; font-weight:bold; border-bottom:1px solid black; padding:10px;">
                <span>الموظف: {emp['name']}</span>
                <span>الشهادة: {emp['degree']}</span>
            </div>
            <table>
                <thead><tr><th>الحركة</th><th>الأمر</th><th>التاريخ</th><th>الأشهر</th><th>الفرق</th><th>المجموع</th><th>ملاحظات</th></tr></thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
            <p style="font-weight:bold;">مجموع الفرق الاسمي: {t_nom:,} | الصافي: {t_net:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
