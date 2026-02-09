import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة والتصميم المحسن
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات - مصطفى حسن", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* 1. ضبط الخط والاتجاه العام للتطبيق */
    html, body, .stApp {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* 2. تحسين السلاسة في الموبايل */
    .stApp {
        touch-action: pan-y; /* تحسين الاستجابة للمس */
        overflow-x: hidden; /* منع الحركة الجانبية المزعجة */
    }

    /* 3. تصميم "ورقة التقرير" لتكون بيضاء دائماً مع خط أسود */
    .report-container {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }

    /* 4. تنسيق الجدول داخل التقرير */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        font-size: 14px;
        color: #000000 !important; /* إجبار النص على اللون الأسود */
    }

    .report-table th {
        background-color: #f0f0f0 !important; /* خلفية رصاصي فاتح للعناوين */
        color: #000000 !important; /* نص أسود للعناوين */
        font-weight: bold;
        border: 1px solid #000 !important;
        padding: 8px;
        text-align: center !important;
    }

    .report-table td {
        border: 1px solid #000 !important;
        padding: 8px;
        text-align: center !important;
        color: #000000 !important;
    }

    /* 5. تنسيق صفوف المجاميع */
    .total-row-nominal {
        background-color: #fffbe6 !important; /* لون خلفية مميز */
        font-weight: bold;
    }
    .total-row-final {
        background-color: #e6f7ff !important; /* لون سماوي فاتح */
        font-weight: bold;
        color: #0050b3 !important;
    }

    /* 6. إخفاء العناصر غير الضرورية عند الطباعة */
    @media print {
        .no-print { display: none !important; }
        .report-container { box-shadow: none; border: none; margin: 0; padding: 0; }
        .stApp { background-color: white !important; }
    }
    
    /* تنسيق حاوية الإدخال */
    .input-box {
        background-color: #262730; /* لون داكن مريح للعين في الإدخال */
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#4FA4F4;">نظام الفروقات (الإصدار الذهبي)</h2>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ إدارة البيانات
# ---------------------------------------------------------
if 'actions' not in st.session_state:
    st.session_state.actions = []

def delete_action(index):
    st.session_state.actions.pop(index)
    st.rerun()

# ---------------------------------------------------------
# 2️⃣ واجهة الإدخال (تصميم عصري)
# ---------------------------------------------------------
with st.container():
    # حاوية الإدخال (تظهر فقط في الشاشة وتختفي عند الطباعة)
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    
    with st.expander("بيانات الموظف والراتب الأساسي", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("اسم الموظف", "")
            base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
        with c2:
            degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
            end_calc_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")

    st.write("---")
    
    st.markdown("##### ➕ إضافة حركة جديدة")
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

    # عرض قائمة الحركات للحذف
    if st.session_state.actions:
        st.write("🔻 الحركات المضافة:")
        for i, act in enumerate(st.session_state.actions):
            col_a, col_b, col_c, col_d = st.columns([1, 2, 2, 4])
            with col_a:
                if st.button("🗑", key=f"del_{i}"): delete_action(i)
            with col_b: st.write(f"{act['salary']:,.0f}")
            with col_c: st.write(f"{act['date'].strftime('%d/%m/%Y')}")
            with col_d: st.write(f"{act['type']}")

    if st.button("تصفير القائمة 🔄"):
        st.session_state.actions = []
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3️⃣ المنطق الحسابي (V37 - الدقيق)
# ---------------------------------------------------------

def adjust_date(d):
    # جبر التاريخ: إذا يوم 25 أو أكثر -> بداية الشهر القادم
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
        
        # تحديد الراتب السابق
        if i == 0:
            prev_sal = base_sal
            prev_year = curr['date'].year 
        else:
            prev_sal = st.session_state.actions[i-1]['salary']
            prev_year = st.session_state.actions[i-1]['date'].year
        
        # تحديد تاريخ النهاية
        if i < actions_count - 1:
            end_date = st.session_state.actions[i+1]['date']
            # فترة وسطية (الفرق فقط)
            months = get_months_diff(curr['date'], end_date)
        else:
            end_date = end_calc_date
            # الفترة الأخيرة (+1 شهر)
            months = get_months_diff(curr['date'], end_date) + 1
            
        if months > 0:
            is_new_year = (curr['date'].year > prev_year)
            
            # --- المنطق الحسابي ---
            if is_new_year and curr['type'] == "ترفيع وظيفي":
                diff = curr['salary'] - base_sal
                note = "سنة جديدة (الفرق عن الأساس)"
            
            elif is_new_year and curr['type'] != "ترفيع وظيفي":
                diff = (curr['salary'] - prev_sal) * 2
                note = "سنة جديدة (مضاعفة ×2)"
                
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
# 4️⃣ عرض التقرير (تصميم الورقة البيضاء)
# ---------------------------------------------------------
if rows:
    # حاوية التقرير البيضاء
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    
    # الترويسة
    st.markdown(f"""
    <div style="text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 20px;">
        <h3 style="margin:0; color:black;">المديرية العامة لتربية محافظة الديوانية / الشؤون المالية</h3>
        <p style="margin:5px; color:black;">شعبة حسابات الثانوي - كشف الفروقات</p>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:black;">
        <span><b>اسم الموظف:</b> {emp_name if emp_name else '................'}</span>
        <span><b>الشهادة:</b> {degree}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # بناء الجدول HTML
    table_html = """
    <table class="report-table">
        <thead>
            <tr>
                <th width="5%">ت</th>
                <th width="25%">نوع الحركة</th>
                <th width="10%">الأشهر</th>
                <th width="15%">الفرق الشهري</th>
                <th width="20%">الاسمي الكلي</th>
                <th width="25%">الملاحظة</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for r in rows:
        table_html += f"""
        <tr>
            <td>{r['ت']}</td>
            <td>{r['نوع']}</td>
            <td>{r['أشهر']}</td>
            <td>{r['فرق']}</td>
            <td>{r['اسمي']}</td>
            <td>{r['ملاحظة']}</td>
        </tr>
        """
        
    total_gen = total_nominal * current_rate
    
    # إضافة صفوف المجاميع
    table_html += f"""
        <tr class="total-row-nominal">
            <td colspan="4" style="text-align:left !important; padding-left:20px;">مجموع الفرق الاسمي</td>
            <td colspan="2">{total_nominal:,.0f} دينار</td>
        </tr>
        <tr class="total-row-final">
            <td colspan="4" style="text-align:left !important; padding-left:20px;">المستحق الصافي ({int(current_rate*100)}%)</td>
            <td colspan="2">{total_gen:,.0f} دينار</td>
        </tr>
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # التواقيع
    st.markdown("""
    <div style="margin-top:50px; display:flex; justify-content:space-around; text-align:center; color:black; font-weight:bold;">
        <div>منظم الجدول<br><br>__________</div>
        <div>التدقيق<br><br>__________</div>
        <div>مدير القسم<br><br>__________</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # إغلاق حاوية التقرير
    
    # زر الطباعة
    st.markdown('<div class="no-print" style="text-align:center; margin-top:20px;"><button onclick="window.print()" style="padding:10px 20px; font-size:16px; cursor:pointer; background:#4CAF50; color:white; border:none; border-radius:5px;">🖨️ طباعة الكشف</button></div>', unsafe_allow_html=True)

else:
    st.info("الرجاء إضافة حركات من القائمة أعلاه لعرض كشف الفروقات.")
