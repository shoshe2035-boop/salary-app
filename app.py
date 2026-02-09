import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات", layout="centered")

# دالة لتنظيف HTML وإزالة المسافات التي تسبب المشكلة
def render_html(html_string):
    # إزالة الأسطر الجديدة والمسافات الزائدة لتحويلها لسطر واحد
    clean_string = html_string.replace("\n", "").strip()
    st.markdown(clean_string, unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #f4f4f9;
    }
    
    /* تنسيق الورقة البيضاء للتقرير */
    .report-box {
        background-color: white !important;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
        color: black !important;
        margin-top: 10px;
    }
    
    /* تنسيق الجدول الصارم */
    table {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
        border: 1px solid black;
    }
    th {
        background-color: #eee !important;
        color: black !important;
        border: 1px solid black !important;
        padding: 5px;
        text-align: center;
        font-weight: bold;
    }
    td {
        color: black !important;
        border: 1px solid black !important;
        padding: 5px;
        text-align: center;
    }
    
    /* إخفاء العناصر عند الطباعة */
    @media print {
        .no-print { display: none !important; }
        .stApp { background-color: white !important; }
        .report-box { border: none; padding: 0; margin: 0; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h3 style="text-align:center; color:#1E3A8A;">نظام الفروقات (V40)</h3>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1️⃣ البيانات والحركات
# ---------------------------------------------------------
if 'actions' not in st.session_state:
    st.session_state.actions = []

def delete_action(index):
    st.session_state.actions.pop(index)
    st.rerun()

with st.container():
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    
    with st.expander("بيانات الموظف", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("اسم الموظف", "")
            base_sal = st.number_input("الراتب الاسمي القديم (الأساس)", value=0) * 1000
        with c2:
            degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
            end_calc_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")

    st.write("---")
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
            
    if st.session_state.actions:
        st.write("🔻 القائمة:")
        for i, act in enumerate(st.session_state.actions):
            col_a, col_b, col_c = st.columns([1, 2, 4])
            with col_a:
                if st.button("X", key=f"del_{i}"): delete_action(i)
            with col_b: st.write(f"{act['salary']:,.0f}")
            with col_c: st.write(f"{act['type']} - {act['date'].strftime('%d/%m/%Y')}")
            
    if st.button("تصفير 🔄"):
        st.session_state.actions = []; st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2️⃣ الحسابات (المنطق المعتمد)
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
        
        # السابق
        if i == 0:
            prev_sal = base_sal; prev_year = curr['date'].year 
        else:
            prev_sal = st.session_state.actions[i-1]['salary']; prev_year = st.session_state.actions[i-1]['date'].year
        
        # المدة
        if i < actions_count - 1:
            end_date = st.session_state.actions[i+1]['date']
            months = get_months_diff(curr['date'], end_date)
        else:
            end_date = end_calc_date
            months = get_months_diff(curr['date'], end_date) + 1 # +1 للأخيرة
            
        if months > 0:
            is_new_year = (curr['date'].year > prev_year)
            # القواعد
            if is_new_year and curr['type'] == "ترفيع وظيفي":
                diff = curr['salary'] - base_sal; note = "سنة جديدة (فرق عن الأساس)"
            elif is_new_year and curr['type'] != "ترفيع وظيفي":
                diff = (curr['salary'] - prev_sal) * 2; note = "سنة جديدة (×2)"
            else:
                diff = curr['salary'] - prev_sal; note = "نفس السنة"
            
            row_total = diff * months; total_nominal += row_total
            rows.append({"t": i+1, "type": curr['type'], "m": months, "diff": diff, "total": row_total, "note": note})

# ---------------------------------------------------------
# 3️⃣ بناء الجدول (بدون مسافات فارغة)
# ---------------------------------------------------------
if rows:
    total_gen = total_nominal * current_rate
    
    # بناء نص HTML كسطر واحد لتجنب مشكلة الكود
    # لاحظ أنني أجمع النصوص بدقة
    
    table_rows = ""
    for r in rows:
        table_rows += f"<tr><td>{r['t']}</td><td>{r['type']}</td><td>{r['m']}</td><td>{r['diff']:,.0f}</td><td>{r['total']:,.0f}</td><td style='font-size:11px'>{r['note']}</td></tr>"
    
    # القالب الكامل
    final_html = f"""
    <div class="report-box">
        <div style="text-align:center; border-bottom:2px solid black; padding-bottom:10px; margin-bottom:10px;">
            <h4 style="margin:0; color:black;">المديرية العامة لتربية محافظة الديوانية</h4>
            <p style="margin:0; font-size:12px; color:black;">شعبة حسابات الثانوي - كشف الفروقات</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:black;">
            <span>الاسم: {emp_name}</span>
            <span>الشهادة: {degree}</span>
        </div>
        <table>
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
                {table_rows}
                <tr style="background-color:#fff9c4; font-weight:bold;">
                    <td colspan="4" style="text-align:left; padding-left:10px;">المجموع الاسمي</td>
                    <td colspan="2">{total_nominal:,.0f}</td>
                </tr>
                <tr style="background-color:#e1f5fe; font-weight:bold; color:#01579b;">
                    <td colspan="4" style="text-align:left; padding-left:10px;">الصافي المستحق ({int(current_rate*100)}%)</td>
                    <td colspan="2">{total_gen:,.0f}</td>
                </tr>
            </tbody>
        </table>
        <div style="margin-top:30px; display:flex; justify-content:space-between; text-align:center; color:black; font-weight:bold; font-size:12px;">
            <div style="width:30%">المنظم<br><br>___</div>
            <div style="width:30%">التدقيق<br><br>___</div>
            <div style="width:30%">المدير<br><br>___</div>
        </div>
    </div>
    <div class="no-print" style="text-align:center; margin-top:15px;">
        <button onclick="window.print()" style="background:#28a745; color:white; padding:8px 15px; border:none; border-radius:4px; cursor:pointer;">🖨️ طباعة</button>
    </div>
    """
    
    # استخدام الدالة لتنظيف الكود قبل العرض
    render_html(final_html)

else:
    st.info("الرجاء إضافة بيانات.")
