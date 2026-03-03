import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - طباعة A4", layout="centered")

# CSS احترافي لإصلاح الألوان والطباعة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* 1. إعدادات الألوان العامة (إجبار النص الأسود) */
    html, body, .stApp {
        font-family: 'Cairo', sans-serif !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 2. حاوية التقرير - تظهر كأنها ورقة */
    .printable-report {
        background-color: white !important;
        color: black !important;
        padding: 10px;
        width: 100%;
        margin: 0 auto;
    }

    /* 3. تنسيق الجدول للطباعة اليدوية */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        border: 1px solid black !important;
    }
    .report-table th, .report-table td {
        border: 1px solid black !important;
        padding: 8px;
        text-align: center !important;
        color: black !important;
        font-size: 14px;
    }
    .report-table th {
        background-color: #eeeeee !important;
    }

    /* 4. إعدادات ورق A4 عند الطباعة */
    @media print {
        @page {
            size: A4;
            margin: 15mm;
        }
        .no-print, [data-testid="stSidebar"], .stButton {
            display: none !important;
        }
        .stApp {
            background-color: white !important;
        }
        .printable-report {
            border: none !important;
            box-shadow: none !important;
            width: 100% !important;
        }
        body {
            color: black !important;
        }
    }

    /* تحسين شكل المدخلات في الشاشة فقط */
    .input-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ إعدادات الحساب")
    calc_mode = st.radio(
        "طريقة مضاعفة الفروقات:",
        options=["المضاعفة في سنة جديدة فقط", "المضاعفة دائماً (تراكمي مستمر)"]
    )

# ---------------------------------------------------------
# 2️⃣ إدارة البيانات
# ---------------------------------------------------------
if 'actions' not in st.session_state:
    st.session_state.actions = []

def delete_action(index):
    st.session_state.actions.pop(index)
    st.rerun()

# ---------------------------------------------------------
# 3️⃣ واجهة الإدخال (تختفي عند الطباعة)
# ---------------------------------------------------------
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#1E3A8A;">نظام فروقات الرواتب</h2>', unsafe_allow_html=True)

with st.expander("👤 بيانات الموظف الأساسية", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        emp_name = st.text_input("اسم الموظف", "")
        base_sal = st.number_input("الاسم القديم (بالآلاف)", value=0) * 1000
    with col2:
        degree = st.selectbox("الشهادة", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"])
        end_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today())

with st.container():
    st.markdown("##### ➕ إضافة حركة")
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc1: n_type = st.selectbox("النوع", ["علاوة سنوية", "ترفيع وظيفي"])
    with cc2: n_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0) * 1000
    with cc3: n_date = st.date_input("التاريخ", value=None)
    
    if st.button("إضافة الحركة للقائمة"):
        if n_sal > 0 and n_date:
            st.session_state.actions.append({"type": n_type, "salary": n_sal, "date": n_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()

if st.session_state.actions:
    if st.button("🔄 تصفير البيانات"):
        st.session_state.actions = []; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 4️⃣ المنطق الحسابي
# ---------------------------------------------------------
def adjust_date(d):
    return d.replace(day=1) + timedelta(days=31) if d.day >= 25 else d

def get_months(s, e):
    s = adjust_date(s)
    if s >= e: return 0
    return (e.year - s.year) * 12 + (e.month - s.month)

rows = []
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
            eff_diff = b_diff; note = "بداية الاحتساب"
        else:
            is_new_year = (curr['date'].year > p_year)
            if calc_mode == "المضاعفة دائماً (تراكمي مستمر)" or is_new_year:
                eff_diff = b_diff + cum_diff; note = "مضاعفة/تراكم"
            else:
                eff_diff = b_diff; note = "نفس السنة"

        cum_diff += b_diff
        e_date = st.session_state.actions[i+1]['date'] if i < len(st.session_state.actions)-1 else end_date
        months = get_months(curr['date'], e_date)
        if i == len(st.session_state.actions)-1: months += 1

        if months > 0:
            sub_total = eff_diff * months
            total_nominal += sub_total
            rows.append(f"<tr><td>{i+1}</td><td>{curr['type']}</td><td>{months}</td><td>{eff_diff:,}</td><td>{sub_total:,}</td><td>{note}</td></tr>")
        
        p_sal = curr['salary']; p_year = curr['date'].year

# ---------------------------------------------------------
# 5️⃣ عرض التقرير النهائي (A4 Ready)
# ---------------------------------------------------------
if rows:
    total_net = total_nominal * current_rate
    report_html = f"""
    <div class="printable-report">
        <div style="text-align: center; border: 2px solid black; padding: 10px;">
            <h3 style="margin:0;">المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h3>
            <p style="margin:5px;">كشف فروقات الرواتب - شعبة حسابات الثانوي</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin: 15px 0; font-weight:bold;">
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
                {''.join(rows)}
                <tr style="background-color:#f2f2f2; font-weight:bold;">
                    <td colspan="4">مجموع الفرق الاسمي</td>
                    <td colspan="2">{total_nominal:,} دينار</td>
                </tr>
                <tr style="background-color:#e2e2e2; font-weight:bold;">
                    <td colspan="4">المستحق الصافي المستلم</td>
                    <td colspan="2">{total_net:,} دينار</td>
                </tr>
            </tbody>
        </table>
        <div style="margin-top:40px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
            <div>منظم الجدول<br><br>__________</div>
            <div>التدقيق<br><br>__________</div>
            <div>مدير القسم<br><br>__________</div>
        </div>
    </div>
    <div class="no-print" style="text-align:center; margin-top:30px;">
        <button onclick="window.print()" style="padding:15px 30px; font-size:18px; background:#28a745; color:white; border:none; border-radius:8px; cursor:pointer;">
            🖨️ اضغط هنا لطباعة الكشف (A4)
        </button>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)
else:
    st.info("الرجاء إضافة حركات لبدء الاحتساب.")
