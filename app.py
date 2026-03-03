import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="centered")

# CSS دقيق لفصل الألوان (الخلفية بيضاء، السايدبار أسود، المدخلات سوداء)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* 1. إجبار خلفية التطبيق الرئيسية على اللون الأبيض */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    /* 2. القائمة الجانبية: سوداء بالكامل مع نص أبيض */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* 3. صناديق الإدخال والقوائم: خلفية سوداء ونص أبيض */
    div[data-baseweb="input"], div[data-baseweb="select"], .stSelectbox div, .stNumberInput input, .stTextInput input {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* لون النص التوضيحي داخل الصناديق */
    input::placeholder { color: #aaaaaa !important; }

    /* 4. عناوين الحقول (Labels) خارج الصناديق: سوداء لتظهر على الخلفية البيضاء */
    label p {
        color: #000000 !important;
        font-weight: bold;
        font-size: 16px;
    }

    /* 5. التقرير (الورقة A4): خلفية بيضاء ونص أسود ثابت */
    .printable-report {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px;
        border: 2px solid #000000;
        margin-top: 20px;
        direction: rtl;
    }
    
    .printable-report h3, .printable-report p, .printable-report span {
        color: #000000 !important;
    }

    /* 6. جداول التقرير */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    .report-table th, .report-table td {
        border: 1px solid #000000 !important;
        padding: 8px;
        text-align: center !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    .report-table th {
        background-color: #eeeeee !important;
        font-weight: bold;
    }

    /* 7. إعدادات الطباعة */
    @media print {
        @page { size: A4; margin: 10mm; }
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton {
            display: none !important;
        }
        .printable-report { border: none !important; width: 100% !important; margin: 0 !important; }
        * { color: #000000 !important; -webkit-print-color-adjust: exact; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ القائمة الجانبية (الافتراضي: المضاعفة دائماً)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ إعدادات الحساب")
    calc_mode = st.radio(
        "طريقة الاحتساب:",
        options=["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكم مستمر)"],
        index=1  # المضاعفة دائماً هي الافتراضية
    )
    st.write("---")
    st.info("الخلفية بيضاء للتقرير وسوداء للمدخلات.")

# ---------------------------------------------------------
# 2️⃣ واجهة الإدخال
# ---------------------------------------------------------
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#1E3A8A;">نظام احتساب الفروقات</h2>', unsafe_allow_html=True)

if 'actions' not in st.session_state:
    st.session_state.actions = []

def delete_action(index):
    st.session_state.actions.pop(index); st.rerun()

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("اسم الموظف", placeholder="أدخل الاسم هنا...")
        base_sal = st.number_input("الراتب الاسمي القديم (بالآلاف)", value=0) * 1000
    with c2:
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        end_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today())

    st.write("---")
    st.markdown("<h5 style='color:black;'>➕ إضافة حركة استحقاق:</h5>", unsafe_allow_html=True)
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
        if st.button("🗑️ مسح الكل"):
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
# 4️⃣ عرض التقرير
# ---------------------------------------------------------
if st.session_state.actions:
    total_net = total_nominal * current_rate
    report_content = f"""
    <div class="printable-report">
        <div style="text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 20px;">
            <h3 style="margin:0;">المديرية العامة لتربية محافظة الديوانية</h3>
            <p style="margin:5px;">كشف فروقات الرواتب - شعبة حسابات الثانوي</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 10px; font-weight:bold;">
            <span>اسم الموظف: {emp_name if emp_name else '................'}</span>
            <span>الشهادة: {degree} ({int(current_rate*100)}%)</span>
        </div>
        <table class="report-table">
            <thead>
                <tr>
                    <th>ت</th><th>نوع الحركة</th><th>شهر</th><th>الفرق</th><th>الاسمي</th><th>ملاحظة</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
                <tr style="background-color: #f0f0f0 !important; font-weight:bold;">
                    <td colspan="4" style="text-align:left;">مجموع الفرق الاسمي</td>
                    <td colspan="2">{total_nominal:,} د.ع</td>
                </tr>
                <tr style="background-color: #e0e0e0 !important; font-weight:bold;">
                    <td colspan="4" style="text-align:left;">الصافي المستحق</td>
                    <td colspan="2">{total_net:,.0f} د.ع</td>
                </tr>
            </tbody>
        </table>
        <div style="margin-top:60px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
            <div>منظم الجدول<br><br>__________</div>
            <div>التدقيق<br><br>__________</div>
            <div>مدير القسم<br><br>__________</div>
        </div>
    </div>
    <div class="no-print" style="text-align:center; margin-top:30px;">
        <button onclick="window.print()" style="padding:15px 45px; font-size:18px; background-color:#1E3A8A; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">
            🖨️ طباعة التقرير (A4)
        </button>
    </div>
    """
    st.markdown(report_content.replace('\n', ''), unsafe_allow_html=True)
