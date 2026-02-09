import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات (ضبط التاريخ)", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, .main { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .report-header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }
    th, td { border: 1px solid black !important; padding: 8px; text-align: center !important; }
    th { background-color: #f2f2f2 !important; font-weight: bold; }
    
    .no-print { background-color: #f4f4f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px; }
    .note { font-size: 12px; color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#1E3A8A;">نظام الفروقات (مع جبر التواريخ)</h2>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ إدارة البيانات
# ---------------------------------------------------------
if 'actions' not in st.session_state:
    st.session_state.actions = []

def delete_action(index):
    st.session_state.actions.pop(index)
    st.rerun()

# ---------------------------------------------------------
# 2️⃣ واجهة الإدخال
# ---------------------------------------------------------
with st.container():
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    
    # الثوابت
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("اسم الموظف", "")
        base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
    with c2:
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
        end_calc_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")
    
    st.divider()
    
    # إضافة الحركات
    st.markdown("<p class='note'>* ملاحظة: يوم 25 فما فوق يُحسب على الشهر القادم.</p>", unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc1:
        new_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with cc2:
        new_sal = st.number_input("الراتب الجديد", value=0) * 1000
    with cc3:
        new_date = st.date_input("تاريخ الاستحقاق", value=None, format="DD/MM/YYYY")
    
    if st.button("➕ إضافة الحركة"):
        if new_sal > 0 and new_date:
            st.session_state.actions.append({"type": new_type, "salary": new_sal, "date": new_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()
        else:
            st.error("أدخل البيانات كاملة.")

    # عرض الحركات
    if st.session_state.actions:
        st.write("---")
        for i, act in enumerate(st.session_state.actions):
            c_show1, c_show2, c_show3, c_show4 = st.columns([0.5, 3, 2, 2])
            with c_show1:
                if st.button("❌", key=f"del_{i}"): delete_action(i)
            with c_show2: st.write(f"**{act['type']}**")
            with c_show3: st.write(f"{act['salary']:,.0f}")
            with c_show4: st.write(f"{act['date'].strftime('%d/%m/%Y')}")

    if st.button("🔄 تصفير القائمة"):
        st.session_state.actions = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3️⃣ المنطق الحسابي (تعديل الجبر فقط)
# ---------------------------------------------------------

# دالة جبر التاريخ (يوم 25 فما فوق يصبح الشهر القادم)
def get_adjusted_date(d):
    if d.day >= 25:
        # إضافة أيام للانتقال للشهر التالي ثم العودة ليوم 1
        next_month = d.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1)
    else:
        # يبقى في نفس الشهر (يوم 1) لغرض الحساب
        return d.replace(day=1)

def calculate_months(start_date, end_date, is_last_period=False):
    # ضبط البداية حسب قاعدة الجبر
    adj_start = get_adjusted_date(start_date)
    # ضبط النهاية (دائماً نعتبرها نهاية شهر لغرض العد)
    adj_end = end_date.replace(day=1)
    
    if adj_start > adj_end: return 0
    
    # حساب الفرق بالأشهر
    months = (adj_end.year - adj_start.year) * 12 + (adj_end.month - adj_start.month)
    
    # إذا كانت الفترة الأخيرة، نضيف 1 ليشمل شهر النهاية
    if is_last_period:
        months += 1
        
    return months

rows = []
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
current_rate = rates.get(degree, 0)

if st.session_state.actions:
    actions_count = len(st.session_state.actions)
    
    for i in range(actions_count):
        curr = st.session_state.actions[i]
        
        # 1. تحديد الراتب السابق للمقارنة
        if i == 0:
            prev_sal = base_sal
            prev_year = curr['date'].year 
        else:
            prev_sal = st.session_state.actions[i-1]['salary']
            prev_year = st.session_state.actions[i-1]['date'].year
        
        # 2. تحديد الفترة الزمنية (الأشهر)
        if i < actions_count - 1:
            # فترة وسطية: من تاريخ الحالي إلى تاريخ التالي
            next_date = st.session_state.actions[i+1]['date']
            # هنا نستخدم get_adjusted_date للتالي أيضاً ليكون هو الحد الفاصل
            months = calculate_months(curr['date'], get_adjusted_date(next_date), is_last_period=False)
        else:
            # الفترة الأخيرة: من تاريخ الحالي إلى نهاية الاحتساب
            months = calculate_months(curr['date'], end_calc_date, is_last_period=True)
            
        if months > 0:
            # 3. منطق الفروقات (الثابت)
            is_new_year = (curr['date'].year > prev_year)
            
            # أ. ترفيع في سنة جديدة
            if is_new_year and curr['type'] == "ترفيع وظيفي":
                diff = curr['salary'] - base_sal
                note = "سنة جديدة (الفرق عن الأساس)"
            
            # ب. علاوة في سنة جديدة
            elif is_new_year and curr['type'] != "ترفيع وظيفي":
                diff = (curr['salary'] - prev_sal) * 2
                note = "سنة جديدة (مضاعفة ×2)"
                
            # ج. نفس السنة
            else:
                diff = curr['salary'] - prev_sal
                note = "نفس السنة"
            
            row_total = diff * months
            total_nominal += row_total
            
            rows.append({
                "ت": i + 1,
                "نوع": curr['type'],
                "أشهر": months,
                "فرق": f"{diff:,.0f}",
                "اسمي": f"{row_total:,.0f}",
                "ملاحظة": note
            })

# ---------------------------------------------------------
# 4️⃣ طباعة التقرير
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
                <th width="5%">ت</th><th width="25%">نوع الحركة</th><th width="10%">الأشهر</th>
                <th width="15%">الفرق الشهري</th><th width="15%">الاسمي الكلي</th><th width="30%">الملاحظة</th>
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
    
    st.markdown('<div class="no-print" style="text-align:center; margin-top:20px;"><button onclick="window.print()">🖨️ طباعة الكشف</button></div>', unsafe_allow_html=True)
else:
    st.info("أضف الحركات ليتم الاحتساب.")
