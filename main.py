import flet as ft
from datetime import date, timedelta
import uuid

rates = {
    "بكالوريوس": 0.45,
    "دبلوم": 0.55,
    "ماجستير": 0.75,
    "دكتوراه": 1.0,
    "اعدادية": 0.25,
    "متوسطة": 0.15
}

PRIMARY = "#1E3A8A"
BG = "#F4F6FB"
CARD_BG = "#FFFFFF"
TEXT = "#1a1a2e"
ACCENT = "#e8eaf6"

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

def calculate_employee(emp):
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
                "فرق": effective_diff,
                "اسمي": row_total,
                "ملاحظة": "سنة جديدة" if is_new_year else "نفس السنة"
            })

        prev_salary = act['salary']
        prev_year = act['date'].year

    total_gen = total_nominal * rate
    return rows, total_nominal, total_gen


def main(page: ft.Page):
    page.title = "نظام الفروقات"
    page.rtl = True
    page.bgcolor = BG
    page.padding = 0
    page.scroll = None

    employees = []

    # --- الشاشات ---
    main_container = ft.Ref[ft.Column]()
    detail_container = ft.Ref[ft.Column]()

    current_view = {"view": "main"}
    current_emp = {"emp": None}

    def show_main():
        current_view["view"] = "main"
        refresh_main()
        page.update()

    def show_detail(emp):
        current_view["view"] = "detail"
        current_emp["emp"] = emp
        refresh_detail()
        page.update()

    # --- نموذج إضافة موظف ---
    name_field = ft.TextField(label="اسم الموظف", text_align=ft.TextAlign.RIGHT, width=300)
    school_field = ft.TextField(label="المدرسة", text_align=ft.TextAlign.RIGHT, width=300)
    degree_dd = ft.Dropdown(
        label="التحصيل العلمي",
        width=300,
        options=[ft.dropdown.Option(d) for d in rates.keys()],
        value="بكالوريوس",
    )
    base_sal_field = ft.TextField(label="الراتب الأساسي (بالآلاف)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    end_date_field = ft.TextField(label="تاريخ النهاية (YYYY-MM-DD)", value=str(date.today()), width=300)
    add_emp_error = ft.Text("", color="red", size=12)

    def save_employee(e):
        name = name_field.value.strip()
        school = school_field.value.strip()
        try:
            base_sal = int(base_sal_field.value or 0) * 1000
        except:
            add_emp_error.value = "الراتب يجب أن يكون رقماً"
            page.update()
            return
        try:
            end_dt = date.fromisoformat(end_date_field.value.strip())
        except:
            add_emp_error.value = "تاريخ غير صحيح"
            page.update()
            return
        if not name or not school:
            add_emp_error.value = "أدخل الاسم والمدرسة"
            page.update()
            return

        employees.append({
            'id': str(uuid.uuid4()),
            'name': name,
            'school': school,
            'degree': degree_dd.value,
            'base_sal': base_sal,
            'end_date': end_dt,
            'actions': []
        })
        name_field.value = ""
        school_field.value = ""
        base_sal_field.value = ""
        end_date_field.value = str(date.today())
        add_emp_error.value = ""
        add_emp_dlg.open = False
        refresh_main()
        page.update()

    add_emp_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("➕ إضافة موظف جديد", text_align=ft.TextAlign.RIGHT),
        content=ft.Column([
            name_field, school_field, degree_dd,
            base_sal_field, end_date_field, add_emp_error
        ], tight=True, spacing=10, width=320),
        actions=[
            ft.TextButton("إلغاء", on_click=lambda e: close_dlg(add_emp_dlg)),
            ft.ElevatedButton("إضافة", bgcolor=PRIMARY, color="white", on_click=save_employee),
        ],
    )
    page.overlay.append(add_emp_dlg)

    def close_dlg(dlg):
        dlg.open = False
        page.update()

    def open_add_emp(e):
        add_emp_dlg.open = True
        page.update()

    def delete_emp(emp):
        employees.remove(emp)
        refresh_main()
        page.update()

    # --- الشاشة الرئيسية ---
    def refresh_main():
        controls = []

        # AppBar
        controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("نظام الفروقات", color="white", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.icons.ADD, icon_color="white", on_click=open_add_emp),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=PRIMARY,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            )
        )

        if not employees:
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("👥", size=60, text_align=ft.TextAlign.CENTER),
                        ft.Text("لا يوجد موظفون", size=18, color="#90a4ae", text_align=ft.TextAlign.CENTER),
                        ft.Text("اضغط + لإضافة موظف", size=14, color="#b0bec5", text_align=ft.TextAlign.CENTER),
                        ft.ElevatedButton("➕ إضافة موظف", bgcolor=PRIMARY, color="white", on_click=open_add_emp),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                    alignment=ft.alignment.center,
                    padding=60,
                )
            )
        else:
            for emp in employees:
                _, tn, tg = calculate_employee(emp)
                emp_ref = emp
                controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"👤 {emp['name']}", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                                ft.Container(
                                    content=ft.Text(emp['degree'], size=11, color="white"),
                                    bgcolor=PRIMARY, border_radius=15,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"🏫 {emp['school']}", size=13, color="#5c6bc0"),
                            ft.Divider(height=1, color=ACCENT),
                            ft.Row([
                                ft.Column([
                                    ft.Text("الراتب الأساسي", size=11, color="#78909c"),
                                    ft.Text(f"{emp['base_sal']:,}", size=13, weight=ft.FontWeight.BOLD),
                                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Column([
                                    ft.Text("الاسمي", size=11, color="#78909c"),
                                    ft.Text(f"{int(tn):,}", size=13, weight=ft.FontWeight.BOLD, color="#1976d2"),
                                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Column([
                                    ft.Text("الصافي", size=11, color="#78909c"),
                                    ft.Text(f"{int(tg):,}", size=13, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ]),
                            ft.Row([
                                ft.ElevatedButton("📋 تفاصيل", bgcolor=PRIMARY, color="white",
                                    on_click=lambda e, em=emp_ref: show_detail(em)),
                                ft.ElevatedButton("🗑️ حذف", bgcolor="#e53935", color="white",
                                    on_click=lambda e, em=emp_ref: delete_emp(em)),
                            ], alignment=ft.MainAxisAlignment.END),
                        ], spacing=8),
                        bgcolor=CARD_BG, border_radius=12, padding=16,
                        margin=ft.margin.symmetric(horizontal=12, vertical=6),
                        shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                    )
                )

            # ملخص
            summary_rows = [(emp, *calculate_employee(emp)[1:]) for emp in employees if calculate_employee(emp)[1] > 0]
            if summary_rows:
                rows_ctrl = []
                for emp, tn, tg in summary_rows:
                    rows_ctrl.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(emp['name'], size=12)),
                        ft.DataCell(ft.Text(emp['school'], size=12)),
                        ft.DataCell(ft.Text(f"{int(tn):,}", size=12, color="#1976d2")),
                        ft.DataCell(ft.Text(f"{int(tg):,}", size=12, color="#2e7d32")),
                    ]))
                controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 ملخص جميع الموظفين", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("الموظف", size=12, weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("المدرسة", size=12, weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("الاسمي", size=12, weight=ft.FontWeight.BOLD), numeric=True),
                                    ft.DataColumn(ft.Text("الصافي", size=12, weight=ft.FontWeight.BOLD), numeric=True),
                                ],
                                rows=rows_ctrl,
                                heading_row_color=ft.colors.BLUE_50,
                                border=ft.border.all(1, "#e0e0e0"),
                                border_radius=8,
                                column_spacing=15,
                            )
                        ], spacing=10),
                        bgcolor=CARD_BG, border_radius=12, padding=16,
                        margin=ft.margin.symmetric(horizontal=12, vertical=6),
                        shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                    )
                )

        page.controls.clear()
        page.controls.append(
            ft.Column(controls, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        )

    # --- شاشة التفاصيل ---
    def refresh_detail():
        emp = current_emp["emp"]
        if not emp:
            return

        act_type_dd = ft.Dropdown(
            label="نوع الحركة",
            width=200,
            options=[ft.dropdown.Option("علاوة سنوية"), ft.dropdown.Option("ترفيع وظيفي")],
            value="علاوة سنوية",
        )
        act_sal_field = ft.TextField(label="الراتب الجديد (بالآلاف)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        act_date_field = ft.TextField(label="التاريخ (YYYY-MM-DD)", width=180)
        act_error = ft.Text("", color="red", size=12)

        def add_action(e):
            try:
                sal = int(act_sal_field.value or 0) * 1000
            except:
                act_error.value = "الراتب يجب أن يكون رقماً"
                page.update()
                return
            try:
                act_date = date.fromisoformat(act_date_field.value.strip())
            except:
                act_error.value = "تاريخ غير صحيح"
                page.update()
                return
            if sal <= 0:
                act_error.value = "أدخل راتباً أكبر من صفر"
                page.update()
                return

            emp['actions'].append({"type": act_type_dd.value, "salary": sal, "date": act_date})
            emp['actions'] = sorted(emp['actions'], key=lambda x: x['date'])
            act_sal_field.value = ""
            act_date_field.value = ""
            act_error.value = ""
            refresh_detail()
            page.update()

        def remove_action(idx):
            emp['actions'].pop(idx)
            refresh_detail()
            page.update()

        controls = []

        # AppBar
        controls.append(
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton("◀ رجوع", bgcolor="white", color=PRIMARY, on_click=lambda e: show_main()),
                    ft.Text(emp['name'], color="white", size=18, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=PRIMARY,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            )
        )

        # معلومات
        controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(f"👤 {emp['name']}", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.Text(f"🏫 {emp['school']}  |  🎓 {emp['degree']}", size=13),
                    ft.Text(f"💰 الراتب الأساسي: {emp['base_sal']:,}", size=13),
                    ft.Text(f"📅 تاريخ النهاية: {emp['end_date']}", size=13),
                ], spacing=6),
                bgcolor=CARD_BG, border_radius=12, padding=16,
                margin=ft.margin.symmetric(horizontal=12, vertical=6),
                shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
            )
        )

        # نموذج إضافة حركة
        controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("➕ إضافة حركة وظيفية", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    act_type_dd,
                    ft.Row([act_sal_field, act_date_field], spacing=10),
                    act_error,
                    ft.ElevatedButton("إضافة الحركة", bgcolor=PRIMARY, color="white", on_click=add_action),
                ], spacing=10),
                bgcolor=CARD_BG, border_radius=12, padding=16,
                margin=ft.margin.symmetric(horizontal=12, vertical=6),
                shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
            )
        )

        # الحركات
        if emp['actions']:
            action_items = []
            for i, act in enumerate(emp['actions']):
                emoji = "📈" if act['type'] == "ترفيع وظيفي" else "⭐"
                action_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"{emoji} {act['type']}", size=13, expand=True),
                            ft.Text(f"{act['salary']:,} | {act['date']}", size=12, color="#78909c"),
                            ft.ElevatedButton("❌", bgcolor="#e53935", color="white",
                                on_click=lambda e, idx=i: remove_action(idx)),
                        ]),
                        bgcolor=ACCENT, border_radius=10,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    )
                )

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 الحركات الوظيفية", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                        ft.Column(action_items, spacing=8),
                    ], spacing=10),
                    bgcolor=CARD_BG, border_radius=12, padding=16,
                    margin=ft.margin.symmetric(horizontal=12, vertical=6),
                    shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                )
            )

            # النتائج
            rows, total_nominal, total_gen = calculate_employee(emp)
            if rows:
                result_rows = []
                for r in rows:
                    result_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(r['ت']), size=12)),
                        ft.DataCell(ft.Text(r['نوع'], size=12)),
                        ft.DataCell(ft.Text(str(r['أشهر']), size=12)),
                        ft.DataCell(ft.Text(f"{r['فرق']:,}", size=12)),
                        ft.DataCell(ft.Text(f"{r['اسمي']:,}", size=12, color="#1976d2")),
                    ]))

                controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 نتائج الحساب", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("ت", size=12)),
                                    ft.DataColumn(ft.Text("النوع", size=12)),
                                    ft.DataColumn(ft.Text("أشهر", size=12)),
                                    ft.DataColumn(ft.Text("الفرق", size=12), numeric=True),
                                    ft.DataColumn(ft.Text("الاسمي", size=12), numeric=True),
                                ],
                                rows=result_rows,
                                heading_row_color=ft.colors.BLUE_50,
                                border=ft.border.all(1, "#e0e0e0"),
                                border_radius=8,
                                column_spacing=12,
                            ),
                            ft.Divider(),
                            ft.Row([
                                ft.Text("المجموع الاسمي:", size=14, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Text(f"{int(total_nominal):,}", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"),
                            ]),
                            ft.Row([
                                ft.Text(f"المستحق الصافي ({int(rates[emp['degree']]*100)}%):", size=14, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Text(f"{int(total_gen):,}", size=18, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                            ]),
                        ], spacing=12),
                        bgcolor=CARD_BG, border_radius=12, padding=16,
                        margin=ft.margin.symmetric(horizontal=12, vertical=6),
                        shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                    )
                )

        page.controls.clear()
        page.controls.append(
            ft.Column(controls, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        )

    refresh_main()
    page.update()


ft.app(target=main)
