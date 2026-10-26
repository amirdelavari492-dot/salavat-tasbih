import flet as ft
import sqlite3

DB_NAME = "counter.db"

BG = "#080F1D"
PANEL = "#111E31"
PANEL_LIGHT = "#192A40"
GOLD = "#E7C27D"
GOLD_LIGHT = "#FFE6AE"
WHITE = "#F5F4F0"
MUTED = "#91A2B9"
BORDER = "#34445B"


def setup_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                id INTEGER PRIMARY KEY,
                salawat INTEGER NOT NULL DEFAULT 0,
                tasbih INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO counters
            (id, salawat, tasbih) VALUES (1, 0, 0)
        """)


def load_counters():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT salawat, tasbih FROM counters WHERE id=1"
        ).fetchone()


def save_counters(salawat, tasbih):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            UPDATE counters
            SET salawat=?, tasbih=?
            WHERE id=1
        """, (salawat, tasbih))


def main(page: ft.Page):
    page.title = "ذکر | شمارنده"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 18
    page.rtl = True
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    setup_database()
    salawat_count, tasbih_count = load_counters()
    active_page = "tasbih"

    def make_text(value, size, color=WHITE, bold=False):
        return ft.Text(
            value,
            size=size,
            color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
            text_align=ft.TextAlign.CENTER,
        )

    def panel(content, padding=18, color=PANEL, radius=24):
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor=color,
            border=ft.Border.all(1, BORDER),
            border_radius=radius,
            width=380,
        )

    def button_style(bgcolor, color, radius=16):
        return ft.ButtonStyle(
            bgcolor=bgcolor,
            color=color,
            shape=ft.RoundedRectangleBorder(radius=radius),
            elevation=2,
        )

    heading = make_text("ذِکــر", 30, GOLD_LIGHT, True)
    subtitle = make_text("آرامشی ملکوتی", 13, MUTED)

    mode_title = make_text("تسبیح‌شمار", 22, WHITE, True)
    mode_description = make_text(
        "هر ذکر، یک قدم نزدیکی به خدا",
        12,
        MUTED,
    )

    count_value = make_text("۰", 58, GOLD_LIGHT, True)
    count_caption = make_text("مجموع شمارش", 12, MUTED)

    dhikr_label = make_text("ذکر فعلی", 12, MUTED)
    dhikr_value = make_text("الله‌اکبر", 26, GOLD_LIGHT, True)
    cycle_value = make_text("دورهٔ اول  •  ۰ از ۳۳", 13, MUTED)

    bead_row = ft.Row(
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    bead_objects = []

    for i in range(4):
        bead_core = ft.Container(
            width=43,
            height=43,
            border_radius=30,
            bgcolor="#263A54",
            border=ft.Border.all(1.5, "#60728B"),
            shadow=ft.BoxShadow(
                blur_radius=9,
                color="#030711",
                offset=ft.Offset(2, 4),
            ),
            content=ft.Container(
                width=12,
                height=7,
                border_radius=10,
                bgcolor="#72849A",
                margin=ft.Margin(7, 0, 0, 8),
            ),
        )

        bead_objects.append(bead_core)

    def build_beads():
        controls = []

        for i, bead in enumerate(bead_objects):
            controls.append(bead)

            if i < 3:
                controls.append(
                    ft.Container(
                        width=13,
                        height=3,
                        bgcolor="#B99A61",
                    )
                )

        bead_row.controls = controls

    build_beads()
    bead_panel = panel(
        ft.Column(
            [
                make_text("تسبیح", 13, MUTED, True),
                ft.Container(height=12),
                bead_row,
                ft.Container(height=9),
                make_text(
                    "درحال اتصال به خداوند...",
                    11,
                    MUTED,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3,
        ),
        padding=18,
        color="#0D192A",
    )

    counter_panel = ft.Container(
        width=290,
        padding=20,
        border_radius=150,
        bgcolor="#14243A",
        border=ft.Border.all(2, "#A98A51"),
        shadow=ft.BoxShadow(
            blur_radius=28,
            spread_radius=1,
            color="#030711",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            [
                make_text("شمارنده", 13, MUTED),
                count_value,
                count_caption,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
    )

    def make_control_button(label, icon, bg, fg, handler, width=105):
        return ft.Button(
            label,
            icon=icon,
            width=width,
            height=49,
            style=button_style(bg, fg),
            on_click=handler,
        )

    def to_persian(number):
        return str(number).translate(
            str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
        )

    def refresh():
        count = tasbih_count if active_page == "tasbih" else salawat_count
        count_value.value = to_persian(count)

        if active_page == "tasbih":
            mode_title.value = "تسبیح‌شمار"
            mode_description.value = "هر ذکر، یک قدم نزدیکی به خدا"
            count_caption.value = "مجموع شمارش"

            position = ((tasbih_count - 1) % 99) + 1 if tasbih_count else 0

            if position == 0 or position <= 33:
                dhikr_value.value = "الله‌اکبر"
                cycle_value.value = (
                    f"دورهٔ اول  •  {to_persian(position)} از ۳۳"
                )
            elif position <= 66:
                dhikr_value.value = "سبحان‌الله"
                cycle_value.value = (
                    f"دورهٔ دوم  •  {to_persian(position - 33)} از ۳۳"
                )
            else:
                dhikr_value.value = "الحمدلله"
                cycle_value.value = (
                    f"دورهٔ سوم  •  {to_persian(position - 66)} از ۳۳"
                )

            bead_panel.visible = True
            dhikr_label.visible = True
            dhikr_value.visible = True
            cycle_value.visible = True

            active_bead = (tasbih_count - 1) % 4 if tasbih_count else 0

            for i, bead in enumerate(bead_objects):
                selected = i == active_bead
                bead.width = 52 if selected else 43
                bead.height = 52 if selected else 43
                bead.bgcolor = "#E7C27D" if selected else "#263A54"
                bead.border = ft.Border.all(
                    2 if selected else 1.5,
                    "#FFF0C7" if selected else "#60728B",
                )
                bead.content.bgcolor = (
                    "#FFF0C7" if selected else "#72849A"
                )

        else:
            mode_title.value = "صلوات‌شمار"
            mode_description.value = "هر صلوات، پاداشی از سوی خدا"
            count_caption.value = "مجموع صلوات"
            bead_panel.visible = False
            dhikr_label.visible = False
            dhikr_value.visible = False
            cycle_value.visible = False

        save_counters(salawat_count, tasbih_count)
        page.update()

    def increase(e):
        nonlocal salawat_count, tasbih_count

        if active_page == "tasbih":
            tasbih_count += 1
        else:
            salawat_count += 1

        refresh()

    def decrease(e):
        nonlocal salawat_count, tasbih_count
        if active_page == "tasbih":
            tasbih_count = max(0, tasbih_count - 1)
        else:
            salawat_count = max(0, salawat_count - 1)

        refresh()

    def reset(e):
        nonlocal salawat_count, tasbih_count

        if active_page == "tasbih":
            tasbih_count = 0
        else:
            salawat_count = 0

        refresh()

    def switch(e):
        nonlocal active_page

        active_page = (
            "salawat" if active_page == "tasbih"
            else "tasbih"
        )

        switch_button.text = (
            "رفتن به تسبیح‌شمار"
            if active_page == "salawat"
            else "رفتن به صلوات‌شمار"
        )

        refresh()

    increase_button = ft.Button(
        "افزایش",
        icon=ft.Icons.ADD,
        width=145,
        height=55,
        style=button_style(GOLD, "#152033", 18),
        on_click=increase,
    )

    decrease_button = ft.Button(
        "کاهش",
        icon=ft.Icons.REMOVE,
        width=105,
        height=55,
        style=button_style(PANEL_LIGHT, WHITE, 18),
        on_click=decrease,
    )

    reset_button = ft.Button(
        "صفرکردن",
        icon=ft.Icons.RESTART_ALT,
        width=125,
        height=45,
        style=button_style("#202D41", GOLD_LIGHT),
        on_click=reset,
    )

    switch_button = ft.Button(
        "رفتن به صلوات‌شمار",
        icon=ft.Icons.SWAP_HORIZ,
        width=250,
        height=48,
        style=button_style("#192A40", GOLD_LIGHT),
        on_click=switch,
    )

    page.add(
        ft.Column(
            [
                ft.Container(height=5),
                heading,
                subtitle,
                ft.Container(height=16),

                panel(
                    ft.Column(
                        [
                            mode_title,
                            mode_description,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=17,
                ),

                ft.Container(height=12),
                bead_panel,
                ft.Container(height=18),
                counter_panel,
                ft.Container(height=14),

                panel(
                    ft.Column(
                        [
                            dhikr_label,
                            dhikr_value,
                            cycle_value,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=16,
                    color="#101B2B",
                ),

                ft.Container(height=18),

                ft.Row(
                    [increase_button, decrease_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),

                ft.Container(height=5),
                reset_button,
                ft.Container(height=8),
                switch_button,
                ft.Container(height=12),

                make_text("ذخیره‌سازی خودکار فعال است", 11, MUTED),
                ft.Container(height=8),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )
    )

    refresh()


ft.run(main)