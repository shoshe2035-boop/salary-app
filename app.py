import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة والتصميم (CSS)
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* ضبط الخط والاتجاه */
    html, body, .stApp {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #f0f2f6; /* خلفية عامة رمادية فاتحة جداً */
    }

    /* تحسين السلاسة في الموبايل */
    .stApp {
        touch-action: pan-y;
        overflow-x: hidden;
    }

    /* حاوية التقرير (الورقة البيضاء) */
    .report-container {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ccc;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-top: 20px;
        width: 100%;
        overflow-x: auto; /* للسماح بالتمرير الأفقي للجدول إذا ضاق */
    }

    /* تنسيق الجدول */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 13px; /* تصغير الخط قليلاً للموبايل */
        direction: rtl;
    }

    .report-table th {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
        font-weight: bold;
        border: 1px solid #000 !important;
        padding: 6px;
        text-align: center !important;
        white-space: nowrap; /* منع التفاف العناوين */
    }

    .report-table td {
        border: 1px solid #000 !important;
        padding: 6px;
        text-align: center !important;
        color: #000000 !important;
    }

    /* ألوان صفوف المجاميع */
    .total-row-nominal { background-color: #fff9c4 !important; font-weight: bold; }
    .total-row-final { background-color: #e1f5fe !important; font-weight: bold; color: #01579b !important; }

    /* إخفاء العناصر عند الطباعة */
    @media print {
        .no-print { display: none !important; }
        .report-container { box-shadow: none; border: none; margin: 0; padding: 0; width: 100%; }
        .stApp { background-color: white !important; }
    }
    
    /* تنسيق أزرار الحذف */
    .delete-btn {
        color: red;
        font-weight: bold;
        border: 1px solid red;
        border-radius: 5px;
        padding: 0px 5px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h3 style="text-align:center; color:#1E3A8A;">نظام الفروقات (الإصدار المستقر)</h3>', unsafe_allow_html=True)

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
    
    with st.expander("👤 بيانات الموظف والراتب الأساسي", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("اسم الموظف", "")
            base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
        with c2:
            degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
            end_calc_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")

    st.write("---")
    st.markdown("##### ➕ إدخال الحركات (علاوة / ترفيع)")
    
    cc1, cc2, cc3 = st.columns([1.5, 1.5, 2])
    with cc1:
        new_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with cc2:
        new_sal = st.number_input("الراتب الجديد", value=0) * 1000
    with cc3:
        new_date = st.date_input("تاريخ الاستحقاق", value=None, format="DD/MM/YYYY")
    
    if st.button("إضافة للقائمة ✅", use_container_width=True):
        if new_sal > 0 and new_date:
            st.session_state.actions.append({"type": new_type, "salary": new_sal, "date": new_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()
        else:
            st.warning("يرجى إدخال الراتب والتاريخ.")

    # عرض الحركات
    if st.session_state.actions:
        st.write("🔻 القائمة الحالية:")
        for i, act in enumerate(st.session_state.actions):
            col_a, col_b, col_c, col_d = st.columns([0.5, 2, 2, 3])
            with col_a:
                if st.button("X", key=f"del_{i}", help="حذف الحركة"): delete_action(i)
            with col_b: st.write(f"{act['salary']:,.0f}")
            with col_c: st.write(f"{act['date'].strftime('%d/%m/%Y')}")
            with col_d: st.write(f"{act['type']}")

    if st.button("تصفير القائمة 🔄"):
        st.session_state.actions = []
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3️⃣ المنطق الحسابي
# ---------------------------------------------------------
def adjust_date(d):
    if d.day >= 25:
        next_month = d.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1)
    return d

def get_months_diff(start, end):
    adj_start = adjust_date(start)
    if adj_start >= end: return 0
    return (end.year - adj_start.year) * 12 + (end.month - adj_start.month)

rows = []
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
current_rate = rates.get(degree, 0)

if st.session_state.actions:
    actions_count = len(st.session_state.actions)
    
    for i in range(actions_count):
        curr = st.session_state.actions[i]
        
        # الراتب السابق
        if i == 0:
            prev_sal = base_sal
            prev_year = curr['date'].year 
        else:
            prev_sal = st.session_state.actions[i-1]['salary']
            prev_year = st.session_state.actions[i-1]['date'].year
        
        # تاريخ النهاية
        if i < actions_count - 1:
            end_date = st.session_state.actions[i+1]['date']
            months = get_months_diff(curr['date'], end_date) # فترة وسطية
        else:
            end_date = end_calc_date
            months = get_months_diff(curr['date'], end_date) + 1 # فترة أخيرة (+1)
            
        if months > 0:
            is_new_year = (curr['date'].year > prev_year)
            
            # --- القواعد ---
            if is_new_year and curr['type'] == "ترفيع وظيفي":
                diff = curr['salary'] - base_sal
                note = "سنة جديدة (فرق عن الأساس)"
            
            elif is_new_year and curr['type'] != "ترفيع وظيفي":
                diff = (curr['salary'] - prev_sal) * 2
                note = "سنة جديدة (×2)"
                
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
# 4️⃣ بناء جدول التقرير (HTML صافي)
# ---------------------------------------------------------
if rows:
    total_gen = total_nominal * current_rate
    
    # بناء كود HTML كقطعة واحدة لتجنب الأخطاء
    html_content = f"""
    <div class="report-container">
        <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px;">
            <h4 style="margin:0; color:#000;">المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h4>
            <p style="margin:5px; font-size:12px; color:#000;">شعبة حسابات الثانوي - كشف الفروقات</p>
        </div>
        
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:13px; color:#000;">
            <span><b>الاسم:</b> {emp_name}</span>
            <span><b>الشهادة:</b> {degree}</span>
        </div>

        <table class="report-table">
            <thead>
                <tr>
                    <th width="5%">ت</th>
                    <th width="25%">نوع الحركة</th>
                    <th width="10%">شهر</th>
                    <th width="20%">الفرق</th>
                    <th width="20%">الاسمي</th>
                    <th width="20%">ملاحظة</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # إضافة الصفوف
    for r in rows:
        html_content += f"""
        <tr>
            <td>{r['ت']}</td>
            <td>{r['نوع']}</td>
            <td>{r['أشهر']}</td>
            <td>{r['فرق']}</td>
            <td>{r['اسمي']}</td>
            <td style="font-size:11px;">{r['ملاحظة']}</td>
        </tr>
        """
        
    # إضافة المجاميع
    html_content += f"""
        <tr class="total-row-nominal">
            <td colspan="4" style="text-align:left; padding-left:10px;">المجموع الاسمي</td>
            <td colspan="2">{total_nominal:,.0f}</td>
        </tr>
        <tr class="total-row-final">
            <td colspan="4" style="text-align:left; padding-left:10px;">الصافي المستحق ({int(current_rate*100)}%)</td>
            <td colspan="2">{total_gen:,.0f}</td>
        </tr>
            </tbody>
        </table>

        <div style="margin-top:40px; display:flex; justify-content:space-between; text-align:center; font-size:12px; color:#000; font-weight:bold;">
            <div style="width:30%;">منظم الجدول<br><br>__________</div>
            <div style="width:30%;">التدقيق<br><br>__________</div>
            <div style="width:30%;">مدير القسم<br><br>__________</div>
        </div>
    </div>
    """
    
    # عرض الجدول
    st.markdown(html_content, unsafe_allow_html=True)
    
    # زر الطباعة
    st.markdown('<div class="no-print" style="text-align:center; margin-top:20px;"><button onclick="window.print()" style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">🖨️ طباعة الكشف</button></div>', unsafe_allow_html=True)

else:
    st.info("الرجاء إضافة حركات لعرض الكشف.")
