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
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BG
    page.padding = 0

    employees = []

    employees_list_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def refresh_main():
        employees_list_view.controls.clear()
        if not employees:
            employees_list_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("👥", size=60, text_align=ft.TextAlign.CENTER),
                        ft.Text("لا يوجد موظفون بعد", size=18, color="#90a4ae", text_align=ft.TextAlign.CENTER),
                        ft.Text("اضغط الزر أدناه لإضافة موظف", size=14, color="#b0bec5", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=40
                )
            )
        else:
            for emp in employees:
                _, total_nominal, total_gen = calculate_employee(emp)
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("👤", size=24),
                            ft.Column([
                                ft.Text(emp['name'], size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                                ft.Text(emp['school'], size=13, color="#5c6bc0"),
                            ], expand=True, spacing=2),
                            ft.Container(
                                content=ft.Text(emp['degree'], size=12, color="white", weight=ft.FontWeight.BOLD),
                                bgcolor=PRIMARY,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=20,
                            )
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(height=1, color=ACCENT),
                        ft.Row([
                            ft.Column([
                                ft.Text("الراتب الأساسي", size=11, color="#78909c"),
                                ft.Text(f"{emp['base_sal']:,}", size=14, weight=ft.FontWeight.BOLD, color=TEXT),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                            ft.VerticalDivider(width=1, color=ACCENT),
                            ft.Column([
                                ft.Text("المجموع الاسمي", size=11, color="#78909c"),
                                ft.Text(f"{int(total_nominal):,}", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                            ft.VerticalDivider(width=1, color=ACCENT),
                            ft.Column([
                                ft.Text("المستحق الصافي", size=11, color="#78909c"),
                                ft.Text(f"{int(total_gen):,}", size=14, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        ]),
                        ft.Row([
                            ft.ElevatedButton(
                                "📋 تفاصيل",
                                on_click=lambda e, em=emp: open_employee_detail(em),
                                bgcolor=PRIMARY,
                                color="white",
                            ),
                            ft.ElevatedButton(
                                "🗑️ حذف",
                                on_click=lambda e, em=emp: confirm_delete_employee(em),
                                bgcolor="#e53935",
                                color="white",
                            ),
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=10),
                    bgcolor=CARD_BG,
                    border_radius=16,
                    padding=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="#1a1a2e18", offset=ft.Offset(0, 2)),
                    margin=ft.margin.symmetric(horizontal=12)
                )
                employees_list_view.controls.append(card)

            summary_rows = []
            has_data = False
            for emp in employees:
                _, tn, tg = calculate_employee(emp)
                if tn > 0:
                    has_data = True
                    summary_rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(emp['name'], size=13, rtl=True)),
                            ft.DataCell(ft.Text(emp['school'], size=13, rtl=True)),
                            ft.DataCell(ft.Text(f"{int(tn):,}", size=13, color="#1976d2", weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(f"{int(tg):,}", size=13, color="#2e7d32", weight=ft.FontWeight.BOLD)),
                        ])
                    )

            if has_data:
                summary_card = ft.Container(
                    content=ft.Column([
                        ft.Text("📊 النتائج النهائية لجميع الموظفين", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY, rtl=True),
                        ft.Divider(height=1, color=ACCENT),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("الموظف", weight=ft.FontWeight.BOLD, rtl=True)),
                                ft.DataColumn(ft.Text("المدرسة", weight=ft.FontWeight.BOLD, rtl=True)),
                                ft.DataColumn(ft.Text("الاسمي", weight=ft.FontWeight.BOLD, rtl=True), numeric=True),
                                ft.DataColumn(ft.Text("الصافي", weight=ft.FontWeight.BOLD, rtl=True), numeric=True),
                            ],
                            rows=summary_rows,
                            heading_row_color={"default": ACCENT},
                            border=ft.border.all(1, "#e0e0e0"),
                            border_radius=8,
                            column_spacing=20,
                        )
                    ], spacing=10),
                    bgcolor=CARD_BG,
                    border_radius=16,
                    padding=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="#1a1a2e18", offset=ft.Offset(0, 2)),
                    margin=ft.margin.symmetric(horizontal=12)
                )
                employees_list_view.controls.append(summary_card)

        page.update()

    name_field = ft.TextField(label="اسم الموظف", rtl=True, border_radius=10)
    school_field = ft.TextField(label="المدرسة", rtl=True, border_radius=10)
    degree_dd = ft.Dropdown(
        label="التحصيل العلمي",
        options=[ft.dropdown.Option(d) for d in rates.keys()],
        value="بكالوريوس",
        border_radius=10,
    )
    base_sal_field = ft.TextField(label="الراتب الأساسي (بالآلاف)", keyboard_type=ft.KeyboardType.NUMBER, rtl=True, border_radius=10)
    end_date_field = ft.TextField(label="تاريخ نهاية الاحتساب (YYYY-MM-DD)", value=str(date.today()), rtl=True, border_radius=10)
    add_emp_error = ft.Text("", color="red", size=12)

    def save_new_employee(e):
        name = name_field.value.strip()
        school = school_field.value.strip()
        try:
            base_sal = int(base_sal_field.value or 0) * 1000
        except:
            add_emp_error.value = "الراتب يجب أن يكون رقماً"
            page.update()
            return
        try:
            end_date = date.fromisoformat(end_date_field.value.strip())
        except:
            add_emp_error.value = "تاريخ غير صحيح، استخدم YYYY-MM-DD"
            page.update()
            return
        if not name or not school:
            add_emp_error.value = "الرجاء إدخال الاسم والمدرسة"
            page.update()
            return

        employees.append({
            'id': str(uuid.uuid4()),
            'name': name,
            'school': school,
            'degree': degree_dd.value,
            'base_sal': base_sal,
            'end_date': end_date,
            'actions': []
        })
        name_field.value = ""
        school_field.value = ""
        base_sal_field.value = ""
        end_date_field.value = str(date.today())
        add_emp_error.value = ""
        add_emp_dialog.open = False
        refresh_main()
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    add_emp_dialog = ft.AlertDialog(
        title=ft.Text("➕ إضافة موظف جديد", rtl=True, weight=ft.FontWeight.BOLD, color=PRIMARY),
        content=ft.Container(
            content=ft.Column([
                name_field, school_field, degree_dd,
                base_sal_field, end_date_field, add_emp_error,
            ], spacing=12, width=320),
            padding=10
        ),
        actions=[
            ft.TextButton("إلغاء", on_click=lambda e: close_dialog(add_emp_dialog)),
            ft.ElevatedButton("إضافة", bgcolor=PRIMARY, color="white", on_click=save_new_employee),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_add_employee(e):
        add_emp_dialog.open = True
        page.update()

    def confirm_delete_employee(emp):
        def do_delete(e):
            employees.remove(emp)
            del_dialog.open = False
            refresh_main()
            page.update()

        del_dialog = ft.AlertDialog(
            title=ft.Text("تأكيد الحذف", rtl=True),
            content=ft.Text(f"هل تريد حذف {emp['name']}؟", rtl=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: close_dialog(del_dialog)),
                ft.ElevatedButton("حذف", bgcolor="#e53935", color="white", on_click=do_delete),
            ]
        )
        page.overlay.append(del_dialog)
        del_dialog.open = True
        page.update()

    def open_employee_detail(emp):
        detail_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=12)

        act_type_dd = ft.Dropdown(
            label="نوع الحركة",
            options=[ft.dropdown.Option("علاوة سنوية"), ft.dropdown.Option("ترفيع وظيفي")],
            value="علاوة سنوية",
            border_radius=10,
            expand=True,
        )
        act_sal_field = ft.TextField(label="الراتب الجديد (بالآلاف)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, expand=True)
        act_date_field = ft.TextField(label="التاريخ (YYYY-MM-DD)", border_radius=10, expand=True)
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
                act_error.value = "تاريخ غير صحيح، استخدم YYYY-MM-DD"
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
            refresh_main()

        def remove_action(idx):
            emp['actions'].pop(idx)
            refresh_detail()
            refresh_main()

        def refresh_detail():
            detail_content.controls.clear()

            detail_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"👤 {emp['name']}", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY, rtl=True),
                        ft.Text(f"🏫 {emp['school']}  |  🎓 {emp['degree']}", size=13, color=TEXT, rtl=True),
                        ft.Text(f"💰 الراتب الأساسي: {emp['base_sal']:,}", size=13, color=TEXT, rtl=True),
                        ft.Text(f"📅 تاريخ النهاية: {emp['end_date']}", size=13, color=TEXT, rtl=True),
                    ], spacing=6),
                    bgcolor=CARD_BG, border_radius=16, padding=16,
                    shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                )
            )

            detail_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("➕ إضافة حركة وظيفية", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY, rtl=True),
                        act_type_dd,
                        ft.Row([act_sal_field, act_date_field], spacing=10),
                        act_error,
                        ft.ElevatedButton("إضافة الحركة", bgcolor=PRIMARY, color="white", on_click=add_action),
                    ], spacing=10),
                    bgcolor=CARD_BG, border_radius=16, padding=16,
                    shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                )
            )

            if emp['actions']:
                actions_col = ft.Column(spacing=8)
                for i, act in enumerate(emp['actions']):
                    emoji = "📈" if act['type'] == "ترفيع وظيفي" else "⭐"
                    actions_col.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(emoji, size=20),
                                ft.Column([
                                    ft.Text(act['type'], size=13, weight=ft.FontWeight.BOLD, color=TEXT, rtl=True),
                                    ft.Text(f"{act['salary']:,} | {act['date']}", size=12, color="#78909c", rtl=True),
                                ], expand=True, spacing=2),
                                ft.ElevatedButton(
                                    "❌",
                                    on_click=lambda e, idx=i: remove_action(idx),
                                    bgcolor="#e53935",
                                    color="white",
                                )
                            ]),
                            bgcolor=ACCENT, border_radius=12,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        )
                    )

                detail_content.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📋 الحركات الوظيفية", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY, rtl=True),
                            actions_col,
                        ], spacing=10),
                        bgcolor=CARD_BG, border_radius=16, padding=16,
                        shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                    )
                )

                rows, total_nominal, total_gen = calculate_employee(emp)
                if rows:
                    result_rows = []
                    for r in rows:
                        result_rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(r['ت']), size=12)),
                                ft.DataCell(ft.Text(r['نوع'], size=12, rtl=True)),
                                ft.DataCell(ft.Text(str(r['أشهر']), size=12)),
                                ft.DataCell(ft.Text(f"{r['فرق']:,}", size=12)),
                                ft.DataCell(ft.Text(f"{r['اسمي']:,}", size=12, color="#1976d2", weight=ft.FontWeight.BOLD)),
                            ])
                        )

                    detail_content.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text("📊 نتائج الحساب", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY, rtl=True),
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("ت", size=12, weight=ft.FontWeight.BOLD)),
                                        ft.DataColumn(ft.Text("النوع", size=12, weight=ft.FontWeight.BOLD, rtl=True)),
                                        ft.DataColumn(ft.Text("أشهر", size=12, weight=ft.FontWeight.BOLD)),
                                        ft.DataColumn(ft.Text("الفرق", size=12, weight=ft.FontWeight.BOLD), numeric=True),
                                        ft.DataColumn(ft.Text("الاسمي", size=12, weight=ft.FontWeight.BOLD), numeric=True),
                                    ],
                                    rows=result_rows,
                                    heading_row_color={"default": ACCENT},
                                    border=ft.border.all(1, "#e0e0e0"),
                                    border_radius=8,
                                    column_spacing=12,
                                ),
                                ft.Divider(height=1, color="#e0e0e0"),
                                ft.Row([
                                    ft.Text("المجموع الاسمي:", size=14, weight=ft.FontWeight.BOLD, color=TEXT, expand=True, rtl=True),
                                    ft.Text(f"{int(total_nominal):,}", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"),
                                ]),
                                ft.Row([
                                    ft.Text(f"المستحق الصافي ({int(rates[emp['degree']]*100)}%):", size=14, weight=ft.FontWeight.BOLD, color=TEXT, expand=True, rtl=True),
                                    ft.Text(f"{int(total_gen):,}", size=18, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                                ]),
                            ], spacing=12),
                            bgcolor=CARD_BG, border_radius=16, padding=16,
                            shadow=ft.BoxShadow(blur_radius=6, color="#1a1a2e15"),
                        )
                    )

            page.update()

        refresh_detail()

        detail_view = ft.View(
            route=f"/employee/{emp['id']}",
            bgcolor=BG,
            appbar=ft.AppBar(
                title=ft.Text(emp['name'], color="white", rtl=True),
                bgcolor=PRIMARY,
                leading=ft.ElevatedButton(
                    "◀ رجوع",
                    bgcolor=PRIMARY,
                    color="white",
                    on_click=lambda e: go_back()
                ),
                automatically_imply_leading=False,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=0),
            controls=[
                ft.Container(
                    content=detail_content,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=12)
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )
        page.views.append(detail_view)
        page.update()

    def go_back():
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    main_view = ft.View(
        route="/",
        bgcolor=BG,
        appbar=ft.AppBar(
            title=ft.Text("نظام الفروقات", color="white", weight=ft.FontWeight.BOLD, rtl=True),
            bgcolor=PRIMARY,
            center_title=True,
            automatically_imply_leading=False,
        ),
        padding=ft.padding.symmetric(vertical=12, horizontal=0),
        controls=[
            ft.Container(content=employees_list_view, expand=True),
        ],
        floating_action_button=ft.FloatingActionButton(
            text="➕ موظف جديد",
            bgcolor=PRIMARY,
            foreground_color="white",
            on_click=open_add_employee,
        ),
    )

    page.overlay.append(add_emp_dialog)
    page.views.clear()
    page.views.append(main_view)
    refresh_main()
    page.update()


ft.app(main)
