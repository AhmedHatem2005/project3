import flet as ft
from datetime import datetime


def main(page: ft.Page):
    page.title = "نظام إدارة المخزن"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.scroll = ft.ScrollMode.AUTO

    # قائمة المنتجات والسجلات (في الذاكرة)
    products = []
    logs = []

    selected_image_path = ["https://picsum.photos/200"]  # صورة افتراضية لو مرفعش صورة

    # ------------------- نافذة رفع الصورة -------------------
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            selected_image_path[0] = e.files[0].path
            selected_img_text.value = f"تم اختيار: {e.files[0].name}"
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    selected_img_text = ft.Text("لم يتم اختيار صورة بعد", color="grey", size=12)

    # ------------------- عناصر إضافة منتج جديد -------------------
    new_prod_name = ft.TextField(label="اسم المنتج الجديد (مثلاً: علبة مناديل)", width=250)
    new_prod_qty = ft.TextField(label="الكمية المبدئية بالمخزن", keyboard_type=ft.KeyboardType.NUMBER, width=180)

    def add_new_product(e):
        if not new_prod_name.value or not new_prod_qty.value:
            return

        # إضافة المنتج القائمة
        products.append({
            "name": new_prod_name.value,
            "quantity": int(new_prod_qty.value),
            "image": selected_image_path[0]
        })

        # تحديث القائمة المنسدلة للوارد والصادر
        product_dropdown.options.append(ft.dropdown.Option(new_prod_name.value))

        # تفريغ الحقول
        new_prod_name.value = ""
        new_prod_qty.value = ""
        selected_img_text.value = "لم يتم اختيار صورة بعد"
        selected_image_path[0] = "https://picsum.photos/200"

        refresh_products()

    add_product_btn = ft.ElevatedButton(
        "إضافة المنتج للمخزن",
        icon=ft.icons.INVENTORY,
        on_click=add_new_product,
        style=ft.ButtonStyle(color="white", bgcolor="green")
    )

    # ------------------- عناصر تسجيل الحركة (صادر / وارد) -------------------
    product_dropdown = ft.Dropdown(label="اختر المنتج", width=200, options=[])
    type_dropdown = ft.Dropdown(
        label="نوع الحركة",
        options=[ft.dropdown.Option("وارد (داخل)"), ft.dropdown.Option("صادر (خارج)")],
        width=150
    )
    qty_input = ft.TextField(label="العدد", keyboard_type=ft.KeyboardType.NUMBER, width=100)

    # ------------------- عرض المنتجات -------------------
    products_grid = ft.Row(wrap=True, spacing=15)

    def refresh_products():
        products_grid.controls.clear()
        for p in products:
            products_grid.controls.append(
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Image(src=p["image"], width=160, height=120, fit=ft.ImageFit.COVER, border_radius=8),
                            ft.Text(p["name"], weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"الموجود بالمخزن: {p['quantity']}", color="blue", weight=ft.FontWeight.W_500),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=12
                    )
                )
            )
        page.update()

    # ------------------- السجل اليومي والحركات -------------------
    logs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("التاريخ والوقت")),
            ft.DataColumn(ft.Text("اسم المنتج")),
            ft.DataColumn(ft.Text("نوع الحركة")),
            ft.DataColumn(ft.Text("العدد")),
        ],
        rows=[]
    )

    def add_transaction(e):
        if not product_dropdown.value or not type_dropdown.value or not qty_input.value:
            return

        qty = int(qty_input.value)
        prod_name = product_dropdown.value
        trans_type = type_dropdown.value
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        # تحديث كمية المنتج
        for p in products:
            if p["name"] == prod_name:
                if "وارد" in trans_type:
                    p["quantity"] += qty
                elif "صادر" in trans_type:
                    if p["quantity"] >= qty:
                        p["quantity"] -= qty
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("الكمية المطلوبة أكبر من المتوفر بالمخزن!"))
                        page.snack_bar.open = True
                        page.update()
                        return

        # تسجيل الحركة في السجل
        logs.append({"time": now_str, "prod": prod_name, "type": trans_type, "qty": qty})

        logs_table.rows.insert(
            0,
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(now_str)),
                ft.DataCell(ft.Text(prod_name)),
                ft.DataCell(ft.Text(trans_type, color="red" if "صادر" in trans_type else "green")),
                ft.DataCell(ft.Text(str(qty))),
            ])
        )

        qty_input.value = ""
        refresh_products()

    add_btn = ft.ElevatedButton("تسجيل الحركة", on_click=add_transaction, icon=ft.icons.ADD)

    # ------------------- تصميم الواجهة الرئيسي -------------------
    page.add(
        ft.Text("لوحة إدارة المخزن والحركة اليومية", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),

        # 1. قسم إضافة منتج جديد
        ft.Text("1. إضافة منتج جديد للمخزن:", size=18, weight=ft.FontWeight.W_600),
        ft.Row([
            new_prod_name,
            new_prod_qty,
            ft.ElevatedButton("اختيار صورة المنتج", icon=ft.icons.IMAGE,
                              on_click=lambda _: file_picker.pick_files(allow_multiple=False)),
            selected_img_text,
            add_product_btn
        ], wrap=True),

        ft.Divider(),

        # 2. عرض المنتجات الحالية
        ft.Text("2. كروت المنتجات والكمية الحالية:", size=18, weight=ft.FontWeight.W_600),
        products_grid,

        ft.Divider(),

        # 3. قسم صادر ووارد
        ft.Text("3. تسجيل حركة صادر / وارد يومية:", size=18, weight=ft.FontWeight.W_600),
        ft.Row([product_dropdown, type_dropdown, qty_input, add_btn]),

        ft.Divider(),

        # 4. السجل اليومي
        ft.Text("4. سجل الحركات اليومي بالتاريخ والوقت:", size=18, weight=ft.FontWeight.W_600),
        logs_table
    )


if __name__ == "__main__":
    # تشغيل التطبيق كموقع ويب على المنفذ 8080
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)