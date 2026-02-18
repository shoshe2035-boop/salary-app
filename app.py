import streamlit as st
from datetime import date, timedelta

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="نظام الفروقات الدقيق - مصطفى حسن", layout="centered")

# مفتاح التبديل اليدوي في الشريط الجانبي
with st.sidebar:
    st.header("الإعدادات")
    dark_mode = st.toggle("الوضع الداكن (يدوي)", value=False)
    st.caption("إذا كان غير مفعل، يعتمد على إعدادات النظام.")

# تحديد المتغيرات حسب الوضع (يدوي أو تلقائي)
if dark_mode:
    # وضع داكن يدوي
    bg_color = "#1e1e1e"
    text_color = "#e0e0e0"
    border_color = "#555"
    header_bg = "#333"
    no_print_bg = "#2d2d2d"
    no_print_border = "#444"
    button_bg = "#0a2472"
    button_text = "#ffffff"
    table_row_alt = "#2a2a2a"
    blue_bg = "#0a2472"  # خلفية زرقاء للصفوف المهمة
else:
    # الوضع الفاتح أو تلقائي (سيتم التحكم عبر prefers-color-scheme)
    # هنا نضع قيم افتراضية للفاتح، لكننا سنستخدم prefers-color-scheme للتحكم التلقائي
    bg_color = "#ffffff"
    text_color = "#000000"
    border_color = "#000000"
    header_bg = "#f2f2f2"
    no_print_bg = "#f4f4f9"
    no_print_border = "#ddd"
    button_bg = "#1E3A8A"
    button_text = "white"
    table_row_alt = "#f9f9f9"
    blue_bg = "#1E3A8A"

# CSS مخصص يدعم المفتاح اليدوي وتفضيل النظام
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* المتغيرات الأساسية (تستبدل حسب الوضع) */
    :root {{
        --bg-color: {bg_color};
        --text-color: {text_color};
        --border-color: {border_color};
        --header-bg: {header_bg};
        --no-print-bg: {no_print_bg};
        --no-print-border: {no_print_border};
        --button-bg: {button_bg};
        --button-text: {button_text};
        --table-row-alt: {table_row_alt};
        --blue-bg: {blue_bg};
    }}
    
    /* إذا كان المفتاح اليدوي غير مفعل، نعتمد على تفضيل النظام */
    {" " if dark_mode else """
    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-color: #1e1e1e;
            --text-color: #e0e0e0;
            --border-color: #555;
            --header-bg: #333;
            --no-print-bg: #2d2d2d;
            --no-print-border: #444;
            --button-bg: #0a2472;
            --button-text: #ffffff;
            --table-row-alt: #2a2a2a;
            --blue-bg: #0a2472;
        }}
    }}
    """}
    
    /* تطبيق المتغيرات */
    html, body, .main {{
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: var(--bg-color);
        color: var(--text-color);
    }}
    
    .report-header {{
        text-align: center;
        border: 2px solid var(--border-color);
        padding: 10px;
        margin-bottom: 20px;
    }}
    
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        table-layout: fixed;
    }}
    
    th, td {{
        border: 1px solid var(--border-color) !important;
        padding: 8px;
        text-align: center !important;
    }}
    
    th {{
        background-color: var(--header-bg) !important;
        font-weight: bold;
    }}
    
    .no-print {{
        background-color: var(--no-print-bg);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid var(--no-print-border);
        margin-bottom: 20px;
    }}
    
    /* تنسيق الأزرار */
    button {{
        background-color: var(--button-bg);
        color: var(--button-text);
        border-radius: 5px;
        padding: 8px 15px;
        cursor: pointer;
        border: none;
    }}
    
    /* تنسيق صفوف الإجمالي (أزرق موحد) */
    .total-row {{
        background-color: var(--blue-bg) !important;
        color: white !important;
        font-weight: bold;
    }}
    .total-row td {{
        background-color: var(--blue-bg) !important;
        color: white !important;
        border-color: var(--border-color) !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#1E3A8A;">نظام الفروقات (المنطق المزدوج: تتابع + سنوات)</h2>', unsafe_allow_html=True)

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
    
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("اسم الموظف", "")
        base_sal = st.number_input("الراتب الاسمي القديم (بالآلاف)", value=0, step=1, format="%d") * 1000
    with c2:
        degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "دبلوم", "ماجستير", "دكتوراه", "اعدادية", "متوسطة"], index=0)
    
    end_calc_date = st.date_input("تاريخ نهاية الاحتساب", value=date.today(), format="DD/MM/YYYY")
    
    st.divider()
    
    st.caption("أدخل الحركات بالتسلسل (علاوة سنوية، ترفيع وظيفي...):")
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc1:
        new_type = st.selectbox("نوع الحركة", ["علاوة سنوية", "ترفيع وظيفي"])
    with cc2:
        new_sal = st.number_input("الراتب الجديد (بالآلاف)", value=0, step=1, format="%d") * 1000
    with cc3:
        new_date = st.date_input("تاريخ الاستحقاق", value=None, format="DD/MM/YYYY")
    
    if st.button("➕ إضافة الحركة"):
        if new_sal > 0 and new_date:
            st.session_state.actions.append({"type": new_type, "salary": new_sal, "date": new_date})
            st.session_state.actions = sorted(st.session_state.actions, key=lambda x: x['date'])
            st.rerun()
        else:
            st.error("أدخل البيانات كاملة.")

    if st.session_state.actions:
        st.write("---")
        for i, act in enumerate(st.session_state.actions):
            c_show1, c_show2, c_show3, c_show4 = st.columns([0.5, 3, 2, 2])
            with c_show1:
                if st.button("❌", key=f"del_{i}"): delete_action(i)
            with c_show2: st.write(f"**{act['type']}**")
            with c_show3: st.write(f"{act['salary']:,}")
            with c_show4: st.write(f"{act['date'].strftime('%d/%m/%Y')}")

    if st.button("🔄 تصفير القائمة"):
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

def get_months(start, end):
    adj_start = adjust_date(start)
    if adj_start >= end:
        return 0
    return (end.year - adj_start.year) * 12 + (end.month - adj_start.month)

rows = []
total_nominal = 0
rates = {"بكالوريوس": 0.45, "دبلوم": 0.55, "ماجستير": 0.75, "دكتوراه": 1.0, "اعدادية": 0.25, "متوسطة": 0.15}
current_rate = rates.get(degree, 0)

if st.session_state.actions:
    cumulative_diff = 0
    prev_salary = base_sal
    prev_year = None

    for i, curr in enumerate(st.session_state.actions):
        base_diff = curr['salary'] - prev_salary

        if prev_year is None:
            is_new_year = False
        else:
            is_new_year = (curr['date'].year > prev_year)

        if is_new_year:
            effective_diff = base_diff + cumulative_diff
        else:
            effective_diff = base_diff

        cumulative_diff += base_diff

        if i < len(st.session_state.actions) - 1:
            end_date = st.session_state.actions[i+1]['date']
        else:
            end_date = end_calc_date

        months = get_months(curr['date'], end_date)

        if months > 0:
            row_total = effective_diff * months
            total_nominal += row_total

            rows.append({
                "ت": i + 1,
                "نوع": curr['type'],
                "أشهر": months,
                "فرق": f"{effective_diff:,}",
                "اسمي": f"{row_total:,}",
                "ملاحظة": "سنة جديدة (بتراكم)" if is_new_year else "نفس السنة"
            })

        prev_salary = curr['salary']
        prev_year = curr['date'].year

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
    
    # صف مجموع الفرق الاسمي (بنفس تنسيق المستحق الصافي)
    st.markdown(f"""
        <tr class="total-row">
            <td colspan="4" style="text-align:left; padding-left:15px;">مجموع الفرق الاسمي</td>
            <td>{total_nominal:,}</td><td>دينار</td>
        </tr>
        <tr class="total-row">
            <td colspan="4" style="text-align:left; padding-left:15px;">المستحق الصافي ({int(current_rate*100)}%)</td>
            <td>{total_gen:,}</td><td>دينار</td>
        </tr>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        </tbody>
    </table>
    <div style="margin-top:50px; display:flex; justify-content:space-around; text-align:center; font-weight:bold;">
        <div>منظم الجدول<br><br>__________</div>
        <div>التدقيق<br><br>__________</div>
        <div>مدير القسم<br><br>__________</div>
    </div>
    """, unsafe_allow_html=True)
    
    # زر الطباعة الفعّال
    st.markdown("""
    <div style="text-align:center; margin-top:20px;">
        <button onclick="window.print()" style="background-color: #1E3A8A; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
            🖨️ طباعة الكشف
        </button>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.info("أضف الحركات ليتم الاحتساب.")
