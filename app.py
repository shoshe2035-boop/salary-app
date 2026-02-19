import streamlit as st
from datetime import date, timedelta
import uuid

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - موظفين متعددين", layout="wide")

# CSS ثابت
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, .main {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
        color: #000000;
    }
    
    h1, h2, h3 {
        color: #1E3A8A;
    }
    
    .report-header {
        text-align: center;
        border: 2px solid #000000;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        table-layout: fixed;
    }
    
    th, td {
        border: 1px solid #000000 !important;
        padding: 8px;
        text-align: center !important;
    }
    
    th {
        background-color: #f2f2f2 !important;
        font-weight: bold;
    }
    
    .no-print {
        background-color: #f4f4f9;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    
    button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        cursor: pointer;
        border: none;
    }
    
    .total-row {
        background-color: #1E3A8A !important;
        color: white !important;
        font-weight: bold;
    }
    .total-row td {
        background-color: #1E3A8A !important;
        color: white !important;
        border-color: #000000 !important;
    }
    
    /* تنسيق الجدول النهائي */
    .summary-table th {
        background-color: #1E3A8A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center;">نظام الفروقات (موظفين متعددين)</h1>', unsafe_allow_html=True)

# ---------------------------------------------------------
# إدارة حالة الموظفين
# ---------------------------------------------------------
if 'employees' not in st.session_state:
    st.session_state.employees = []

# دوال مساعدة
def delete_employee(emp_id):
    st.session_state.employees = [e for e in st.session_state.employees if e['id'] != emp_id]
    st.rerun()

def delete_action(emp_id, action_index):
    for emp in st.session_state.employees:
        if emp['id'] == emp_id:
            emp['actions'].pop(action_index)
            break
    st.rerun()

# ---------------------------------------------------------
# الشريط الجانبي: إضافة موظف جديد
# ---------------------------------------------------------
with st.sidebar:
    st.header("➕ إضافة موظف جديد")
    with st.form("new_employee_form"):
        new_name = st.text_input("اسم الموظف", "")
        new_school = st.text_input("المدرسة", "")
        new_degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
        new_base_sal = st.number_input("الراتب الاسمي القديم (بالآلاف)", value=0, step=1, format="%d") * 1000
        new_end_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")
        
        if st.form_submit_button("إضافة الموظف"):
            if new_name and new_school:
                emp_id = str(uuid.uuid4())
                st.session_state.employees.append({
                    'id': emp_id,
                    'name': new_name,
                    'school': new_school,
                    'degree': new_degree,
                    'base_sal': new_base_sal,
                    'end_date': new_end_date,
                    'actions': []  # قائمة الحركات
                })
                st.rerun()
            else:
                st.error("الرجاء إدخال اسم الموظف والمدرسة")

# ---------------------------------------------------------
# دوال الحساب (نفس المنطق السابق)
# ---------------------------------------------------------
def adjust_date(d):
    if d.day >= 25:
        next_month = d.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1)
    return d

def get_months(start, end):
    adj_start = adjust_date(start)
    if adj_start >= end:
        return 0
    return (end.year - adj_start.year) * 12 + (end.month - adj_start.month)

rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}

def calculate_employee(emp):
    """تحسب النتائج لموظف معين وتعطي (rows, total_nominal, total_gen)"""
    rows = []
    total_nominal = 0
    rate = rates.get(emp['degree'], 0)
    
    if not emp['actions']:
        return rows, total_nominal, 0
    
    cumulative_diff = 0
    prev_salary = emp['base_sal']
    prev_year = None
    
    for i, act in enumerate(emp['actions']):
        base_diff = act['salary'] - prev_salary
        
        if prev_year is None:
            is_new_year = False
        else:
            is_new_year = (act['date'].year > prev_year)
        
        if is_new_year:
            effective_diff = base_diff + cumulative_diff
        else:
            effective_diff = base_diff
        
        cumulative_diff += base_diff
        
        # تاريخ النهاية لهذه الحركة
        if i < len(emp['actions']) - 1:
            end_date = emp['actions'][i+1]['date']
        else:
            end_date = emp['end_date']
        
        months = get_months(act['date'], end_date)
        
        if months > 0:
            row_total = effective_diff * months
            total_nominal += row_total
            rows.append({
                "ت": i+1,
                "نوع": act['type'],
                "أشهر": months,
                "فرق": f"{effective_diff:,}",
                "اسمي": f"{row_total:,}",
                "ملاحظة": "سنة جديدة (بتراكم)" if is_new_year else "نفس السنة"
            })
        
        prev_salary = act['salary']
        prev_year = act['date'].year
    
    total_gen = total_nominal * rate
    return rows, total_nominal, total_gen

# ---------------------------------------------------------
# الصفحة الرئيسية
# ---------------------------------------------------------
if not st.session_state.employees:
    st.info("👈 أضف موظفين من القائمة الجانبية")
else:
    # إنشاء تبويبات لكل موظف
    tab_names = [f"{emp['name']} - {emp['school']}" for emp in st.session_state.employees]
    tabs = st.tabs(tab_names)
    
    summary_data = []  # لتجميع بيانات الجدول النهائي
    
    for tab_idx, emp in enumerate(st.session_state.employees):
        with tabs[tab_idx]:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 0.5])
            with col1: st.write(f"**الموظف:** {emp['name']}")
            with col2: st.write(f"**المدرسة:** {emp['school']}")
            with col3: st.write(f"**الشهادة:** {emp['degree']}")
            with col4: st.write(f"**الراتب الأساسي:** {emp['base_sal']:,}")
            with col5:
                if st.button("🗑️ حذف", key=f"del_emp_{emp['id']}"):
                    delete_employee(emp['id'])
            
            st.divider()
            
            # إدارة الحركات
            st.subheader("الحركات الوظيفية")
            
            # نموذج إضافة حركة
            with st.form(key=f"add_action_{emp['id']}"):
                ca1, ca2, ca3 = st.columns(3)
                with ca1:
                    act_type = st.selectbox("النوع", ["علاوة سنوية", "ترفيع وظيفي"], key=f"type_{emp['id']}")
                with ca2:
                    act_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0, step=1, format="%d", key=f"sal_{emp['id']}") * 1000
                with ca3:
                    act_date = st.date_input("التاريخ", value=None, format="DD/MM/YYYY", key=f"date_{emp['id']}")
                
                if st.form_submit_button("➕ إضافة حركة"):
                    if act_sal > 0 and act_date:
                        emp['actions'].append({"type": act_type, "salary": act_sal, "date": act_date})
                        emp['actions'] = sorted(emp['actions'], key=lambda x: x['date'])
                        st.rerun()
                    else:
                        st.error("أدخل جميع البيانات")
            
            # عرض الحركات الحالية
            if emp['actions']:
                st.write("---")
                for i, act in enumerate(emp['actions']):
                    cola, colb, colc, cold = st.columns([0.5, 2, 2, 2])
                    with cola:
                        if st.button("❌", key=f"del_act_{emp['id']}_{i}"):
                            delete_action(emp['id'], i)
                    with colb: st.write(f"**{act['type']}**")
                    with colc: st.write(f"{act['salary']:,}")
                    with cold: st.write(f"{act['date'].strftime('%d/%m/%Y')}")
                
                # حساب وعرض النتائج لهذا الموظف
                rows, total_nominal, total_gen = calculate_employee(emp)
                if rows:
                    st.subheader("نتائج الحساب")
                    # عرض جدول النتائج التفصيلية
                    result_table = "<table><tr><th>ت</th><th>نوع</th><th>أشهر</th><th>الفرق</th><th>الاسمي</th><th>ملاحظة</th></tr>"
                    for r in rows:
                        result_table += f"<tr><td>{r['ت']}</td><td>{r['نوع']}</td><td>{r['أشهر']}</td><td>{r['فرق']}</td><td>{r['اسمي']}</td><td>{r['ملاحظة']}</td></tr>"
                    result_table += f"<tr class='total-row'><td colspan='4' style='text-align:left'>المجموع الاسمي</td><td>{total_nominal:,}</td><td></td></tr>"
                    result_table += f"<tr class='total-row'><td colspan='4' style='text-align:left'>المستحق الصافي ({int(rates[emp['degree']]*100)}%)</td><td>{total_gen:,}</td><td></td></tr>"
                    result_table += "</table>"
                    st.markdown(result_table, unsafe_allow_html=True)
                    
                    # تجميع بيانات الملخص
                    summary_data.append({
                        "الموظف": emp['name'],
                        "المدرسة": emp['school'],
                        "الشهادة": emp['degree'],
                        "المجموع الاسمي": total_nominal,
                        "المستحق الصافي": total_gen
                    })
            else:
                st.info("لا توجد حركات بعد. أضف حركة.")
    
    # ---------------------------------------------------------
    # الجدول النهائي (ملخص جميع الموظفين)
    # ---------------------------------------------------------
    if summary_data:
        st.divider()
        st.header("📊 النتائج النهائية لجميع الموظفين")
        
        # تحويل البيانات إلى جدول
        summary_table = "<table class='summary-table'><tr><th>الموظف</th><th>المدرسة</th><th>الشهادة</th><th>المجموع الاسمي</th><th>المستحق الصافي</th></tr>"
        for d in summary_data:
            summary_table += f"<tr><td>{d['الموظف']}</td><td>{d['المدرسة']}</td><td>{d['الشهادة']}</td><td>{d['المجموع الاسمي']:,}</td><td>{d['المستحق الصافي']:,}</td></tr>"
        summary_table += "</table>"
        st.markdown(summary_table, unsafe_allow_html=True)
        
        # زر طباعة (للملخص)
        st.markdown("""
        <div style="text-align:center; margin-top:20px;">
            <button onclick="window.print()">🖨️ طباعة الكشف النهائي</button>
        </div>
        """, unsafe_allow_html=True)