def generate_excel():
    output = io.BytesIO()
    engine_used = None
    try:
        # محاولة استخدام openpyxl أولاً
        import openpyxl
        engine_used = 'openpyxl'
    except ImportError:
        try:
            # إذا لم يوجد، جرب xlsxwriter
            import xlsxwriter
            engine_used = 'xlsxwriter'
        except ImportError:
            # إذا لم يوجد أي منهما، نعود إلى CSV
            return generate_csv()
    
    with pd.ExcelWriter(output, engine=engine_used) as writer:
        for emp in st.session_state.all_employees:
            # بيانات الموظف
            df_emp = pd.DataFrame([{
                'الموظف': emp['name'],
                'المؤهل': emp['degree'],
                'الراتب الأساسي': emp['base'],
                'تاريخ النهاية': emp['end'],
                'طريقة الاحتساب': emp['mode']
            }])
            df_emp.to_excel(writer, sheet_name=f"{emp['name']}", index=False, startrow=0)

            # حركات الموظف
            actions_data = []
            for act in emp['actions']:
                actions_data.append({
                    'نوع الحركة': act['type'],
                    'رقم الأمر': act['order'],
                    'الراتب الجديد': act['salary'],
                    'التاريخ': act['date']
                })
            df_actions = pd.DataFrame(actions_data)
            df_actions.to_excel(writer, sheet_name=f"{emp['name']}", index=False, startrow=5)

            # نتائج الحساب
            _, total_nom, total_net = calculate_employee(emp)
            df_result = pd.DataFrame([{
                'الاسمي الكلي': total_nom,
                'الصافي المستحق': total_net
            }])
            df_result.to_excel(writer, sheet_name=f"{emp['name']}", index=False, startrow=10)

    output.seek(0)
    return output

def generate_csv():
    """إنشاء ملف CSV يحتوي على جميع البيانات (بديل لـ Excel)"""
    output = io.StringIO()
    all_rows = []
    for emp in st.session_state.all_employees:
        base_row = {
            'الموظف': emp['name'],
            'المؤهل': emp['degree'],
            'الراتب الأساسي': emp['base'],
            'تاريخ النهاية': emp['end'],
            'طريقة الاحتساب': emp['mode']
        }
        # إضافة سطر لكل حركة (توسيع البيانات)
        for act in emp['actions']:
            row = base_row.copy()
            row.update({
                'نوع الحركة': act['type'],
                'رقم الأمر': act['order'],
                'الراتب الجديد': act['salary'],
                'تاريخ الحركة': act['date']
            })
            # حساب النتائج
            _, total_nom, total_net = calculate_employee(emp)
            row['الاسمي الكلي'] = total_nom
            row['الصافي المستحق'] = total_net
            all_rows.append(row)
    
    df = pd.DataFrame(all_rows)
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    return output.getvalue().encode('utf-8-sig')
