import streamlit as st
from datetime import date, timedelta

# إعدادات الصفحة
st.set_page_config(page_title="نظام فروقات الرواتب", layout="wide")

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; }
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stDateInput input { background-color: #2b2b2b; color: white; -webkit-text-fill-color: white; }
    table { width: 100%; border-collapse: collapse; color: black; }
    th { background-color: #d1d1d1; border: 1px solid black; padding: 10px; }
    td { border: 1px solid black; padding: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة البيانات (مع زر التصفير)
# ---------------------------------------------------------
if 'all_employees' not in st.session_state: st.session_state.all_employees = []
if 'temp_actions' not in st.session_state: st.session_state.temp_actions = []

with st.sidebar:
    st.header("⚙️ الخيارات")
    if st.button("🔄 تصفير البيانات"):
        st.session_state.all_employees = []
        st.session_state.temp_actions = []
        st.rerun()
    calc_mode = st.radio("طريقة الاحتساب:", ["المضاعفة في سنة جديدة", "المضاعفة دائماً"], index=1)

# ---------------------------------------------------------
# الواجهة
# ---------------------------------------------------------
st.title("نظام فروقات الرواتب")

with st.expander("إضافة موظف جديد", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("اسم الموظف")
        b_sal = st.number_input("الراتب القديم", value=0) * 1000
    with c2:
        deg = st.selectbox("الشهادة", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        e_date = st.date_input("نهاية الاحتساب", value=date.today())

    a1, a2, a3, a4 = st.columns(4)
    with a1: a_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with a2: a_sal = st.number_input("الراتب الجديد", value=0) * 1000
    with a3: a_date = st.date_input("التاريخ", value=date.today())
    with a4: a_order = st.text_input("رقم الأمر")

    if st.button("✅ إضافة الحركة"):
        # إضافة آمنة
        st.session_state.temp_actions.append({"type": a_type, "order": a_order, "salary": a_sal, "date": a_date})
        st.rerun()

    if st.session_state.temp_actions:
        st.table(st.session_state.temp_actions)
        if st.button("💾 حفظ الموظف"):
            st.session_state.all_employees.append({"name": name, "degree": deg, "base": b_sal, "end": e_date, "actions": st.session_state.temp_actions, "mode": calc_mode})
            st.session_state.temp_actions = []; st.rerun()

# ---------------------------------------------------------
# الحسابات (مع استخدام .get لحماية الكود)
# ---------------------------------------------------------
def calculate(emp):
    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    rate = rates.get(emp['degree'], 0)
    
    rows, total_nom, cum_diff, p_sal, p_year = [], 0, 0, emp['base'], None
    
    # التأكد من الترتيب
    actions = sorted(emp['actions'], key=lambda x: x['date'])
    
    for i, curr in enumerate(actions):
        # استخدام .get لتجنب KeyError
        curr_sal = curr.get('salary', 0)
        curr_date = curr.get('date', date.today())
        curr_type = curr.get('type', '---')
        curr_order = curr.get('order', '---')
        
        b_diff = curr_sal - p_sal
        cum_diff += b_diff
        
        if p_year is None: 
            eff_diff = b_diff
            note = "بداية"
        else:
            if emp['mode'] == "المضاعفة دائماً":
                eff_diff = cum_diff
                note = "تراكمي"
            elif curr_date.year > p_year:
                eff_diff = cum_diff
                note = "سنة جديدة"
            else:
                eff_diff = b_diff
                note = "نفس السنة"
        
        next_d = actions[i+1]['date'] if i < len(actions)-1 else emp['end']
        months = ((next_d.year - curr_date.year) * 12 + (next_d.month - curr_date.month))
        if i == len(actions)-1: months += 1
        
        if months > 0:
            total_nom += (eff_diff * months)
            # تم استخدام .get هنا لحماية السطر الذي كان يسبب الخطأ
            rows.append(f"<tr><td>{curr_type}</td><td>{curr_order}</td><td>{curr_date}</td><td>{months}</td><td>{eff_diff:,}</td><td>{eff_diff * months:,}</td><td>{note}</td></tr>")
        
        p_sal = curr_sal
        p_year = curr_date.year
        
    return rows, total_nom, total_nom * rate

if st.session_state.all_employees:
    for emp in st.session_state.all_employees:
        rows, t_nom, t_net = calculate(emp)
        st.markdown(f"### {emp['name']}")
        st.markdown(f"<table><tr><th>الحركة</th><th>الأمر</th><th>التاريخ</th><th>أشهر</th><th>الفرق</th><th>المجموع</th><th>ملاحظات</th></tr>{''.join(rows)}</table>", unsafe_allow_html=True)
        st.write(f"المجموع الاسمي: {t_nom:,} | الصافي: {t_net:,.0f}")
