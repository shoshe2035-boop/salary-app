import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة والطباعة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات الجماعي - مصطفى حسن", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, .stApp { direction: rtl !important; text-align: right !important; background-color: #ffffff !important; font-family: 'Cairo', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; text-align: right !important; }
    div[data-baseweb="input"], .stNumberInput input, .stTextInput input, .stSelectbox div, .stDateInput input {
        background-color: #000000 !important; color: #ffffff !important; direction: rtl !important; text-align: right !important;
    }
    label p { color: #000000 !important; font-weight: bold; font-size: 16px; }
    .printable-report { background-color: white !important; padding: 30px; border: 2px solid black; margin-bottom: 50px; page-break-after: always; color: black !important; }
    .report-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .report-table th, .report-table td { border: 1px solid black !important; padding: 10px; text-align: center !important; color: black !important; }
    .report-table th { background-color: #eeeeee !important; }
    @media print {
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], button, .stButton { display: none !important; }
        .printable-report { border: 1px solid #000 !important; margin: 0 !important; width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة الحالة (Session State)
# ---------------------------------------------------------
if 'all_employees' not in st.session_state: st.session_state.all_employees = []
if 'current_actions' not in st.session_state: st.session_state.current_actions = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

def reset_form():
    st.session_state.current_actions = []
    st.session_state.form_id += 1

# ---------------------------------------------------------
# القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ خيارات النظام")
    calc_mode = st.radio("طريقة الاحتساب:", ["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكم مستمر)"], index=1)
    st.write("---")
    st.subheader(f"👥 الموظفين المضافين: {len(st.session_state.all_employees)}")
    if st.button("🔄 تصفير النظام بالكامل"):
        st.session_state.all_employees = []
        reset_form()
        st.rerun()
    st.markdown("---")
    st.write("**المبرمج المستشار:** مصطفى حسن")

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - م. مصطفى حسن</h1>', unsafe_allow_html=True)

f_id = st.session_state.form_id
with st.expander("👤 إدخال بيانات موظف جديد", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("اسم الموظف", key=f"name_{f_id}")
        base_sal = st.number_input("الراتب القديم (آلاف)", value=0, key=f"base_{f_id}") * 1000
    with c2:
        deg = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], key=f"deg_{f_id}")
        e_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), key=f"end_{f_id}")

    st.write("---")
    st.markdown("##### ➕ إضافة حركة (علاوة / ترفيع)")
    cc1, cc2, cc3, cc4 = st.columns([2, 2, 2, 2])
    with cc1: a_type = st.selectbox("النوع", ["علاوة سنوية", "ترفيع وظيفي"], key=f"atype_{f_id}")
    with cc2: a_order = st.text_input("رقم الأمر الإداري", key=f"aord_{f_id}")
    with cc3: a_sal = st.number_input("الراتب الجديد (آلاف)", value=0, key=f"asal_{f_id}") * 1000
    with cc4: a_date = st.date_input("التاريخ", value=None, key=f"adate_{f_id}")

    if st.button("📥 إضافة الحركة للموظف الحالي", use_container_width=True):
        if a_sal > 0 and a_date:
            st.session_state.current_actions.append({"type": a_type, "order": a_order, "salary": a_sal, "date": a_date})
            st.session_state.current_actions = sorted(st.session_state.current_actions, key=lambda x: x['date'])
            st.rerun()
        else:
            st.warning("يرجى التأكد من إدخال الراتب والتاريخ بشكل صحيح!")

    if st.session_state.current_actions:
        st.markdown("**حركات الموظف المعاينة قبل الحفظ:**")
        st.table(st.session_state.current_actions)
        
        if st.button("💾 حفظ الموظف وعرض النتائج بالأسفل", use_container_width=True):
            if name and st.session_state.current_actions:
                st.session_state.all_employees.append({
                    "name": name, "degree": deg, "base": base_sal, "end": e_date,
                    "actions": st.session_state.current_actions.copy(), "mode": calc_mode
                })
                reset_form()
                st.rerun()
            elif not name:
                st.error("يرجى كتابة اسم الموظف!")
            elif not st.session_state.current_actions:
                st.error("يجب إضافة حركة واحدة على الأقل قبل الحفظ!")

# ---------------------------------------------------------
# الحسابات والتقرير (المنطق المصحح)
# ---------------------------------------------------------
def process_calc(emp):
    rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
    curr_rate = rates.get(emp['degree'], 0)
    rows, total_nom, cum_diff, p_sal, p_year = "", 0, 0, emp['base'], None
    
    for i, curr in enumerate(emp['actions']):
        b_diff = curr['salary'] - p_sal
        if p_year is None: 
            eff_diff, note = b_diff, "بداية"
        else:
            is_new_year = (curr['date'].year > p_year)
            # منطق المضاعفة دائماً
            if emp['mode'] == "المضاعفة دائماً (تراكم مستمر)" or is_new_year:
                eff_diff, note = b_diff + cum_diff, "تراكمي"
            else: 
                eff_diff, note = b_diff, "نفس السنة"

        cum_diff += b_diff
        next_d = emp['actions'][i+1]['date'] if i < len(emp['actions'])-1 else emp['end']
        # حساب الأشهر
        m = (next_d.year - curr['date'].year) * 12 + (next_d.month - curr['date'].month)
        if i == len(emp['actions'])-1: m += 1 # إضافة شهر الغلق
        
        if m > 0:
            total_nom += (eff_diff * m)
            rows += f"<tr><td>{curr['type']}</td><td>{curr['order']}</td><td>{m}</td><td>{eff_diff:,}</td><td>{eff_diff*m:,}</td><td>{note}</td></tr>"
        p_sal, p_year = curr['salary'], curr['date'].year
    return rows, total_nom, total_nom * curr_rate

# ---------------------------------------------------------
# عرض النتائج النهائية
# ---------------------------------------------------------
if st.session_state.all_employees:
    st.markdown("---")
    st.subheader("📋 كشوفات الموظفين المنجزة")
    
    for idx, emp in enumerate(st.session_state.all_employees):
        c1, c2 = st.columns([6, 1])
        c1.markdown(f"**{idx+1}. الموظف: {emp['name']}**")
        if c2.button("🗑️ حذف", key=f"del_{idx}"):
            st.session_state.all_employees.pop(idx)
            st.rerun()

    if st.button("🖨️ طباعة التقارير النهائية (A4)", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    for emp in st.session_state.all_employees:
        r, tn, tnet = process_calc(emp)
        st.markdown(f"""
        <div class="printable-report">
            <h3 style="text-align:center;">مديرية تربية الديوانية - كشف فروقات</h3>
            <div style="display:flex; justify-content:space-between; font-weight:bold; border-bottom:1px solid black; padding-bottom:5px;">
                <span>الموظف: {emp['name']}</span><span>الشهادة: {emp['degree']}</span><span>تاريخ الغلق: {emp['end']}</span>
            </div>
            <table class="report-table">
                <thead><tr><th>الحركة</th><th>رقم الأمر</th><th>أشهر</th><th>الفرق</th><th>الاسمي الكلي</th><th>ملاحظات</th></tr></thead>
                <tbody>{r}
                <tr style="background:#eee; font-weight:bold;"><td colspan="4">مجموع الفرق الاسمي</td><td colspan="2">{tn:,} د.ع</td></tr>
                <tr style="background:#ddd; font-weight:bold;"><td colspan="4">المستحق الصافي للقبض</td><td colspan="2">{tnet:,.0f} د.ع</td></tr>
                </tbody>
            </table>
            <div style="margin-top:30px; display:flex; justify-content:space-around; font-weight:bold; text-align:center;">
                <div>المنظم<br><br>_______</div><div>التدقيق<br><br>_______</div><div>مدير القسم<br><br>_______</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
