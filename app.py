import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة - م. مصطفى حسن
# ---------------------------------------------------------
st.set_page_config(page_title="نظام فروقات الرواتب - مصطفى حسن", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* 1. ضبط الصفحة الأساسية بالكامل */
    html, body, .stApp {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        font-family: 'Cairo', sans-serif !important;
        color: #000000 !important;
    }

    /* 2. القائمة الجانبية: أسود ملكي */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    [data-testid="stSidebar"] * { 
        color: #ffffff !important; 
    }

    /* 3. حل مشكلة ألوان المدخلات (أبيض على أبيض) */
    /* جعل خلفية الحقول رمادي غامق جداً والنص أبيض ناصع */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    /* العناوين فوق الحقول: أسود غامق */
    label p { 
        color: #000000 !important; 
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* 4. حل مشكلة تضليل العناوين في الجداول (أسود على أسود) */
    .report-table th {
        background-color: #e0e0e0 !important; /* خلفية رمادية فاتحة */
        color: #000000 !important; /* نص أسود */
        font-weight: bold !important;
        border: 1px solid #000000 !important;
    }

    /* 5. جدول المعاينة أثناء الإضافة */
    [data-testid="stTable"] {
        background-color: #ffffff !important;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }

    /* 6. كارت التقرير النهائي للطباعة A4 */
    .employee-card {
        background-color: white !important;
        color: black !important;
        padding: 30px;
        border: 2px solid black;
        margin-bottom: 40px;
        page-break-after: always;
        direction: rtl !important;
    }
    .report-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .report-table td {
        border: 1px solid black !important;
        padding: 8px;
        text-align: center !important;
        color: black !important;
        font-size: 14px;
    }

    @media print {
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], button { display: none !important; }
        .employee-card { border: 1px solid black !important; margin: 0; padding: 10mm; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة البيانات
# ---------------------------------------------------------
if 'all_employees' not in st.session_state: st.session_state.all_employees = []
if 'temp_actions' not in st.session_state: st.session_state.temp_actions = []

with st.sidebar:
    st.header("⚙️ الخيارات")
    calc_mode = st.radio("طريقة الاحتساب المعتمدة:", ["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكم مستمر)"], index=1)
    if st.button("🗑️ مسح جميع البيانات"): 
        st.session_state.all_employees = []; st.session_state.temp_actions = []; st.rerun()
    st.write("---")
    st.markdown("**المبرمج المستشار:** م. مصطفى حسن")

# ---------------------------------------------------------
# واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<h1 class="no-print" style="text-align:center; color:#1E3A8A;">نظام الفروقات الجماعي - مصطفى حسن</h1>', unsafe_allow_html=True)

with st.expander("👤 إدخال بيانات الموظف والحركات الإدارية", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم الموظف الموقر")
        b_sal = st.number_input("الراتب الاسمي السابق (بالآلاف)", value=0, step=250) * 1000
    with col2:
        deg = st.selectbox("التحصيل الدراسي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        e_date = st.date_input("تاريخ غلق فترة الاحتساب", value=date.today())

    st.write("---")
    st.markdown("<h5 style='color:black;'>➕ إضافة استحقاق جديد (علاوة / ترفيع):</h5>", unsafe_allow_html=True)
    ac1, ac2, ac3, ac4 = st.columns([2, 2, 2, 2])
    with ac1: a_type = st.selectbox("نوع الاستحقاق", ["علاوة سنوية", "ترفيع وظيفي"])
    with ac2: a_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0, step=250) * 1000
    with ac3: a_date = st.date_input("تاريخ الاستحقاق", value=None)
    with ac4: a_order = st.text_input("رقم الأمر الإداري")

    if st.button("✅ إضافة الحركة الحالية للموظف"):
        if a_sal > 0 and a_date:
            st.session_state.temp_actions.append({
                "نوع الحركة": a_type, 
                "رقم الأمر": a_order if a_order else "---",
                "الراتب الجديد": a_sal,
                "التاريخ": a_date
            })
            st.session_state.temp_actions = sorted(st.session_state.temp_actions, key=lambda x: x['التاريخ'])
            st.rerun()

    if st.session_state.temp_actions:
        st.markdown("<p style='color:black; font-weight:bold;'>قائمة الحركات المضافة حالياً:</p>", unsafe_allow_html=True)
        st.table(st.session_state.temp_actions)
        
        if st.button("💾 حفظ الموظف وكافة حركاته في التقرير النهائي"):
            if name:
                st.session_state.all_employees.append({
                    "name": name, "degree": deg, "base": b_sal, "end": e_date, 
                    "actions": st.session_state.temp_actions.copy(), "mode": calc_mode
                })
                st.session_state.temp_actions = []; st.success("تم الحفظ في القائمة بنجاح!"); st.rerun()
            else: st.error("يرجى تزويدنا باسم الموظف")

# ---------------------------------------------------------
# معالجة البيانات والتقارير
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
        b_diff = curr['الراتب الجديد'] - p_sal
        if p_year is None: eff_diff, note = b_diff, "بداية الاحتساب"
        else:
            if emp['mode'] == "المضاعفة دائماً (تراكم مستمر)" or curr['التاريخ'].year > p_year:
                eff_diff, note = b_diff + cum_diff, "تراكمي"
            else: eff_diff, note = b_diff, "نفس السنة"
        
        cum_diff += b_diff
        next_d = emp['actions'][i+1]['التاريخ'] if i < len(emp['actions'])-1 else emp['end']
        months = diff_m(curr['التاريخ'], next_d) + (1 if i == len(emp['actions'])-1 else 0)
        
        if months > 0:
            sub = eff_diff * months
            total_nom += sub
            # إضافة عمود التاريخ هنا في التقرير النهائي
            rows.append(f"<tr><td>{curr['نوع الحركة']}</td><td>{curr['رقم الأمر']}</td><td>{curr['التاريخ']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub:,}</td><td>{note}</td></tr>")
        p_sal, p_year = curr['الراتب الجديد'], curr['التاريخ'].year
    return rows, total_nom, total_nom * rate

if st.session_state.all_employees:
    st.markdown("---")
    if st.button("🖨️ طباعة كافة كشوفات الموظفين (A4)", use_container_width=True):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    for emp in st.session_state.all_employees:
        rows, t_nom, t_net = process_data(emp)
        st.markdown(f"""
        <div class="employee-card">
            <div style="text-align: center; border: 2px solid black; padding: 15px; margin-bottom: 25px;">
                <h2 style="margin:0;">المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h2>
                <h3 style="margin:5px;">كشف فروقات الرواتب - إعداد: م. مصطفى حسن</h3>
            </div>
            <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:18px; border-bottom:1px solid #000; padding-bottom:10px;">
                <span>الاسم: {emp['name']}</span>
                <span>الشهادة: {emp['degree']}</span>
                <span>تاريخ الغلق: {emp['end']}</span>
            </div>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>نوع الحركة</th>
                        <th>رقم الأمر</th>
                        <th>التاريخ</th>
                        <th>أشهر</th>
                        <th>الفرق الشهري</th>
                        <th>الاسمي الكلي</th>
                        <th>ملاحظات</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                    <tr style="background-color:#f2f2f2; font-weight:bold;">
                        <td colspan="5" style="text-align:left; padding-left:20px;">مجموع الفرق الاسمي المستحق</td>
                        <td colspan="2">{t_nom:,} دينار</td>
                    </tr>
                    <tr style="background-color:#e6e6e6; font-weight:bold;">
                        <td colspan="5" style="text-align:left; padding-left:20px;">المستحق الصافي (نسبة {int(rates.get(emp['degree'],0)*100)}%)</td>
                        <td colspan="2">{t_net:,.0f} دينار</td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:60px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
                <div>منظم الجدول<br><br>__________</div>
                <div>التدقيق والمطابقة<br><br>__________</div>
                <div>مدير القسم المالي<br><br>__________</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
