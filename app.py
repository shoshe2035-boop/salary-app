import streamlit as st
from datetime import date, timedelta
import calendar

# ---------------------------------------------------------
# إعدادات التنسيق
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات الشامل - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, .main { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .report-header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }
    th, td { border: 1px solid black !important; padding: 8px; text-align: center !important; }
    th { background-color: #f2f2f2 !important; font-weight: bold; }
    
    .no-print { background-color: #f4f4f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px; }
    .note-text { font-size: 12px; color: #666; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#1E3A8A;">نظام الفروقات (المقارنة بالأساس + جبر التواريخ)</h2>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ إدارة البيانات (Session State)
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
    st.subheader("1. الثوابت (بداية الاحتساب)")
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("اسم الموظف", "")
        # الراتب الأساسي هو المقياس لكل الحركات اللاحقة
        base_sal = st.number_input("الراتب الاسمي القديم (الأساس المقبوض)", value=0) * 1000
    with c2:
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
        end_calc_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")
    
    st.divider()
    st.subheader("2. إضافة الحركات (علاوات / ترفيعات)")
    st.markdown("<p class='note-text'>* ملاحظة: سيقوم النظام بجبر التاريخ تلقائياً (إذا كان اليوم 25 فما فوق، يُحسب من الشهر التالي).</p>", unsafe_allow_html=True)
    
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc1:
        new_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي", "إضافة خدمة", "تعديل راتب"])
    with cc2:
        new_sal = st.number_input("راتب الحركة الجديد", value=0) * 1000
    with cc3:
        new_date = st.date_input("تاريخ الاستحقاق", value=None, format="DD/MM/YYYY")
    
    if st.button("➕ إضافة للقائمة"):
        if new_sal > 0 and new_date:
            st.session_state.actions.append({"type": new_type, "salary": new_sal, "date": new_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()
        else:
            st.error("تأكد من إدخال الراتب والتاريخ.")

    # عرض القائمة
    if st.session_state.actions:
        st.write("---")
        for i, act in enumerate(st.session_state.actions):
            c_show1, c_show2, c_show3, c_show4 = st.columns([0.5, 3, 2, 2])
            with c_show1:
                if st.button("❌", key=f"del_{i}"): delete_action(i)
            with c_show2: st.write(f"**{act['type']}**")
            with c_show3: st.write(f"{act['salary']:,.0f}")
            with c_show4: st.write(f"{act['date'].strftime('%d/%m/%Y')}")

    if st.button("🔄 تصفير الكل"):
        st.session_state.actions = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3️⃣ المنطق الحسابي (المعادلة الموحدة + جبر التاريخ)
# ---------------------------------------------------------

# دالة ذكية لضبط التاريخ (جبر الكسر)
def adjust_date_logic(d):
    # القاعدة: إذا كان اليوم >= 25، نعتبر البداية من أول الشهر القادم
    if d.day >= 25:
        # الانتقال للشهر التالي
        next_month = d.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1) # أول يوم من الشهر التالي
    else:
        # البقاء في نفس الشهر (يمكنك تعديل الشرط ليكون يوم 1)
        # هنا سنعتمد نفس الشهر للحساب
        return d

def get_months_diff(start_date, end_date):
    # ضبط تواريخ البداية والنهاية حسب قواعد الجبر
    adj_start = adjust_date_logic(start_date)
    
    # حساب الفرق بالأشهر الكاملة
    if adj_start >= end_date: return 0
    return (end_date.year - adj_start.year) * 12 + (end_date.month - adj_start.month)

rows = []
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
current_rate = rates.get(degree, 0)

if st.session_state.actions:
    actions_count = len(st.session_state.actions)
    
    for i in range(actions_count):
        current_act = st.session_state.actions[i]
        
        # 1. تحديد تاريخ نهاية هذه الحركة
        if i < actions_count - 1:
            raw_end_date = st.session_state.actions[i+1]['date']
        else:
            raw_end_date = end_calc_date
        
        # ضبط تواريخ البداية والنهاية للحساب
        calc_start = adjust_date_logic(current_act['date'])
        
        # التأكد من أن تاريخ النهاية أيضاً يتبع منطق الأشهر (نهاية الفترة)
        # في حساب الفروقات، عادة نحسب لغاية بداية الشهر الذي يليه أو تاريخ القطع
        months = get_months_diff(current_act['date'], raw_end_date)
        
        if months > 0:
            # -------------------------------------------------------
            # المعادلة الذهبية: (راتب الحركة الحالي - الراتب الأساسي القديم)
            # -------------------------------------------------------
            diff_val = current_act['salary'] - base_sal
            
            # تحديد الملاحظة
            date_note = ""
            if current_act['date'].day >= 25:
                date_note = f"(جبر التاريخ إلى {calc_start.month}/{calc_start.year})"
            
            note = f"مقارنة بالأساس {base_sal:,.0f} {date_note}"
            
            row_total = diff_val * months
            total_nominal += row_total
            
            rows.append({
                "ت": i + 1,
                "نوع": current_act['type'],
                "أشهر": months,
                "فرق": f"{diff_val:,.0f}",
                "اسمي": f"{row_total:,.0f}",
                "ملاحظة": note
            })

# ---------------------------------------------------------
# 4️⃣ عرض الجدول للطباعة
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
                <th width="5%">ت</th>
                <th width="25%">نوع الحركة</th>
                <th width="10%">الأشهر</th>
                <th width="15%">الفرق (عن الأساس)</th>
                <th width="15%">الاسمي الكلي</th>
                <th width="30%">الملاحظة</th>
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
    st.info("قم بإضافة الحركات من اللوحة أعلاه.")
