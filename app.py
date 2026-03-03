import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="centered")

# CSS لتخصيص الواجهة (القوائم سوداء) والتقرير (أبيض للطباعة)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* 1. إعدادات الخط العام */
    * { font-family: 'Cairo', sans-serif !important; }

    /* 2. تخصيص القائمة الجانبية (خلفية سوداء) */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: white !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 3. تخصيص حقول الإدخال والقوائم المنسدلة (خلفية سوداء) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    label { color: #000000 !important; font-weight: bold; } /* عناوين الحقول بالأسود لتظهر على الخلفية البيضاء للتطبيق */

    /* 4. تنسيق التقرير (أبيض ثابت للطباعة) */
    .printable-report {
        background-color: white !important;
        color: black !important;
        padding: 20px;
        border: 2px solid black;
        margin-top: 20px;
    }
    .report-table {
        width: 100%;
        border-collapse: collapse;
        color: black !important;
    }
    .report-table th, .report-table td {
        border: 1px solid black !important;
        padding: 8px;
        text-align: center !important;
        color: black !important;
    }
    .report-table th { background-color: #f0f0f0 !important; }

    /* 5. إعدادات الطباعة A4 */
    @media print {
        @page { size: A4; margin: 10mm; }
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton {
            display: none !important;
        }
        .printable-report { border: none !important; width: 100% !important; }
        body, .stApp { background-color: white !important; }
        * { color: black !important; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ القائمة الجانبية (الافتراضي: المضاعفة دائماً)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ إعدادات الحساب")
    calc_mode = st.radio(
        "اختر طريقة المضاعفة:",
        options=["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكم مستمر)"],
        index=1  # جعل الخيار الثاني هو الافتراضي
    )
    st.write("---")
    st.write("تم ضبط 'المضاعفة دائماً' كخيار افتراضي بناءً على طلبك.")

# ---------------------------------------------------------
# 2️⃣ إدارة البيانات والواجهة
# ---------------------------------------------------------
if 'actions' not in st.session_state:
    st.session_state.actions = []

st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#000;">نظام احتساب الفروقات</h2>', unsafe_allow_html=True)

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("اسم الموظف", "")
        base_sal = st.number_input("الراتب الاسمي القديم (بالآلاف)", value=0) * 1000
    with c2:
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        end_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today())

    st.write("---")
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc1: n_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with cc2: n_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0) * 1000
    with cc3: n_date = st.date_input("تاريخ الاستحقاق", value=None)
    
    if st.button("✅ إضافة الحركة للقائمة", use_container_width=True):
        if n_sal > 0 and n_date:
            st.session_state.actions.append({"type": n_type, "salary": n_sal, "date": n_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()

    if st.session_state.actions:
        if st.button("🗑️ مسح البيانات"):
            st.session_state.actions = []; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3️⃣ المنطق الحسابي
# ---------------------------------------------------------
def adjust_date(d):
    return d.replace(day=1) + timedelta(days=31) if d.day >= 25 else d

def get_months(s, e):
    s = adjust_date(s)
    if s >= e: return 0
    return (e.year - s.year) * 12 + (e.month - s.month)

rows_html = ""
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
current_rate = rates.get(degree, 0)

if st.session_state.actions:
    cum_diff = 0
    p_sal = base_sal
    p_year = None

    for i, curr in enumerate(st.session_state.actions):
        b_diff = curr['salary'] - p_sal
        
        if p_year is None:
            eff_diff = b_diff; note = "بداية"
        else:
            is_new_year = (curr['date'].year > p_year)
            # تطبيق وضع الحساب المختار
            if calc_mode == "المضاعفة دائماً (تراكم مستمر)" or is_new_year:
                eff_diff = b_diff + cum_diff; note = "تراكمي"
            else:
                eff_diff = b_diff; note = "نفس السنة"

        cum_diff += b_diff
        e_date = st.session_state.actions[i+1]['date'] if i < len(st.session_state.actions)-1 else end_date
        months = get_months(curr['date'], e_date)
        if i == len(st.session_state.actions)-1: months += 1

        if months > 0:
            sub_total = eff_diff * months
            total_nominal += sub_total
            rows_html += f"<tr><td>{i+1}</td><td>{curr['type']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub_total:,}</td><td>{note}</td></tr>"
        
        p_sal = curr['salary']; p_year = curr['date'].year

# ---------------------------------------------------------
# 4️⃣ التقرير المطبوع (أبيض/أسود ثابت)
# ---------------------------------------------------------
if st.session_state.actions:
    total_net = total_nominal * current_rate
    report_content = f"""
    <div class="printable-report">
        <div style="text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 20px;">
            <h3 style="margin:0; color:black;">المديرية العامة لتربية محافظة الديوانية</h3>
            <p style="margin:5px; color:black;">كشف فروقات الرواتب - شعبة حسابات الثانوي</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 10px; font-weight:bold; color:black;">
            <span>اسم الموظف: {emp_name if emp_name else '................'}</span>
            <span>الشهادة: {degree} ({int(current_rate*100)}%)</span>
        </div>
        <table class="report-table">
            <thead>
                <tr>
                    <th>ت</th><th>نوع الحركة</th><th>أشهر</th><th>الفرق</th><th>الاسمي</th><th>ملاحظة</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
                <tr style="background-color: #f0f0f0 !important; font-weight:bold;">
                    <td colspan="4" style="text-align:left;">مجموع الفرق الاسمي</td>
                    <td colspan="2" style="color:black;">{total_nominal:,} دينار</td>
                </tr>
                <tr style="background-color: #e0e0e0 !important; font-weight:bold;">
                    <td colspan="4" style="text-align:left;">الصافي المستحق</td>
                    <td colspan="2" style="color:black;">{total_net:,.0f} دينار</td>
                </tr>
            </tbody>
        </table>
        <div style="margin-top:50px; display:flex; justify-content:space-around; text-align:center; font-weight:bold; color:black;">
            <div>منظم الجدول<br><br>__________</div>
            <div>التدقيق<br><br>__________</div>
            <div>مدير القسم<br><br>__________</div>
        </div>
    </div>
    <div class="no-print" style="text-align:center; margin-top:30px;">
        <button onclick="window.print()" style="padding:15px 40px; font-size:18px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer;">
            🖨️ طباعة الكشف (A4)
        </button>
    </div>
    """
    st.markdown(report_content.replace('\n', ''), unsafe_allow_html=True)
