import streamlit as st
from datetime import date, datetime

# ---------------------------------------------------------
# إعدادات التنسيق والواجهة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الحركات المالية - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, .main { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .report-header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }
    th, td { border: 1px solid black !important; padding: 8px; text-align: center !important; }
    th { background-color: #f2f2f2 !important; font-weight: bold; }
    .col-t { width: 5%; } .col-desc { width: 30%; } .col-months { width: 10%; } 
    .col-diff { width: 15%; } .col-total { width: 15%; } .col-note { width: 25%; }
    .no-print { background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#1E3A8A;">نظام احتساب الفروقات (نظام الحركات المرن)</h2>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ إدخال البيانات الأساسية
# ---------------------------------------------------------
if 'actions' not in st.session_state:
    st.session_state.actions = []

with st.container():
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    emp_name = st.text_input("اسم الموظف الكامل", "")
    base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
    degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
    end_calc_date = st.date_input("تاريخ نهاية الفترة (نهاية الاحتساب)", value=date.today(), format="DD/MM/YYYY")
    
    st.divider()
    st.subheader("➕ إضافة حركات (علاوة / ترفيع)")
    
    # نموذج إضافة حركة جديدة
    col_type, col_sal, col_date = st.columns([2, 2, 3])
    with col_type:
        new_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with col_sal:
        new_sal = st.number_input("الراتب الجديد", value=0) * 1000
    with col_date:
        new_date = st.date_input("تاريخ الحركة", value=None, format="DD/MM/YYYY")
    
    if st.button("إضافة الحركة إلى القائمة"):
        if new_sal > 0 and new_date:
            st.session_state.actions.append({"type": new_type, "salary": new_sal, "date": new_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()
        else:
            st.error("يرجى إدخال الراتب والتاريخ بشكل صحيح.")

    if st.button("تصفير القائمة"):
        st.session_state.actions = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2️⃣ منطق المعالجة الحسابية الديناميكي
# ---------------------------------------------------------
def get_m(start, end):
    if not start or not end or start >= end: return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

rows = []
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
current_rate = rates.get(degree, 0)

if st.session_state.actions:
    actions_count = len(st.session_state.actions)
    
    for i in range(actions_count):
        current_act = st.session_state.actions[i]
        
        # تحديد الراتب السابق وتاريخه
        if i == 0:
            prev_salary = base_sal
            prev_date = None
        else:
            prev_salary = st.session_state.actions[i-1]['salary']
            prev_date = st.session_state.actions[i-1]['date']
        
        # تحديد تاريخ نهاية هذه الحركة (تاريخ الحركة التالية أو نهاية الفترة)
        if i < actions_count - 1:
            end_date = st.session_state.actions[i+1]['date']
        else:
            end_date = end_calc_date
        
        months = get_m(current_act['date'], end_date)
        
        if months > 0:
            diff_val = current_act['salary'] - prev_salary
            note = "نفس السنة"
            
            # تطبيق القوانين الخاصة بك
            if prev_date and current_act['date'].year > prev_date.year:
                if current_act['type'] == "ترفيع وظيفي":
                    # معادلة الترفيع: (الترفيع - الراتب السابق) * 2
                    diff_val = diff_val * 2
                    note = "سنة جديدة (ترفيع ×2)"
                else:
                    # معادلة العلاوة: الفرق * 2
                    diff_val = diff_val * 2
                    note = "سنة جديدة (علاوة ×2)"
            
            total_nominal += (diff_val * months)
            rows.append({
                "ت": i + 1,
                "نوع": current_act['type'],
                "أشهر": months,
                "فرق": f"{diff_val:,.0f}",
                "اسمي": f"{diff_val * months:,.0f}",
                "ملاحظة": note
            })

# ---------------------------------------------------------
# 3️⃣ عرض النتائج للطباعة
# ---------------------------------------------------------
if rows:
    st.markdown(f"""
    <div class="report-header">
        <h3>المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h3>
        <p>اسم الموظف: {emp_name if emp_name else '................'}</p>
    </div>
    <table>
        <thead>
            <tr>
                <th class="col-t">ت</th><th class="col-desc">تفاصيل الاستحقاق</th><th class="col-months">الأشهر</th>
                <th class="col-diff">الفرق الشهري</th><th class="col-total">الاسمي الكلي</th><th class="col-note">الملاحظة</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for r in rows:
        st.markdown(f"<tr><td>{r['ت']}</td><td>{r['نوع']}</td><td>{r['أشهر']}</td><td>{r['فرق']}</td><td>{r['اسمي']}</td><td>{r['ملاحظة']}</td></tr>", unsafe_allow_html=True)
    
    total_gen = total_nominal * current_rate
    st.markdown(f"""
            <tr style="font-weight:bold; background:#f9f9f9;">
                <td colspan="4" style="text-align:left; padding-left:15px;">مجموع الفرق الاسمي</td>
                <td>{total_nominal:,.0f}</td><td>دينار</td>
            </tr>
            <tr style="font-weight:bold; color:blue;">
                <td colspan="4" style="text-align:left; padding-left:15px;">المستحق الصافي ({int(current_rate*100)}%)</td>
                <td>{total_gen:,.0f}</td><td>دينار</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top:50px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
        <div>منظم الجدول<br><br>__________</div>
        <div>التدقيق<br><br>__________</div>
        <div>مدير القسم<br><br>__________</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="no-print" style="text-align:center; margin-top:20px;"><button onclick="window.print()">🖨️ طباعة الكشف النهائي</button></div>', unsafe_allow_html=True)
else:
    st.info("قم بإضافة حركات (علاوة أو ترفيع) ليظهر جدول الاحتساب هنا.")
