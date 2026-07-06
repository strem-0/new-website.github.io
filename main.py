import random
import flet as ft

# بنك الكلمات (العادي والبريميوم)
WORDS_FREE = {
    "🍿 أطعمة": ["منسف", "شاورما", "برغر", "بيتزا"],
    "🦁 حيوانات": ["أسد", "فيل", "قرد", "نمر"]
}
WORDS_PREMIUM = {
    "🏎️ سباق": ["فراري", "ماتور", "حلبة"],
    "🛸 فضائي": ["كوكب", "صخرة", "طبق الطائر"]
}

def main(page: ft.Page):
    # إعدادات أبعاد النافذة لتشبه شاشة الهاتف تماماً على اللابتوب
    page.title = "🕵️‍♂️ لعبة الإمبوستر المستقلة"
    page.window_width = 460
    page.window_height = 720
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    theme_color = ft.Colors.CYAN_400
    is_premium = False

    # بيانات الجولة
    game_data = {
        "mode": "3+ Players", "players": [], "imposter": "", 
        "word": "", "current_idx": 0, "votes": {}
    }

    # عناصر الواجهة
    title_text = ft.Text("🕵️‍♂️ لعبة الإمبوستر التفاعلية", size=24, weight=ft.FontWeight.BOLD, color=theme_color)
    status_text = ft.Text("اختر طور اللعب وسجل الأسماء للبدء!", size=13, color=ft.Colors.GREY_300, text_align=ft.TextAlign.CENTER)
    word_display = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER, text_align=ft.TextAlign.CENTER)
    
    players_view = ft.Column(alignment=ft.MainAxisAlignment.CENTER, spacing=15)
    voting_zone = ft.Column(alignment=ft.MainAxisAlignment.CENTER, spacing=15) # زيادة المسافة بين أزرار التصويت

    name_input = ft.TextField(label="✍️ اسم اللاعب", width=180, border_color=theme_color)
    btn_add_name = ft.ElevatedButton("💾 حفظ", width=100)
    
    mode_dropdown = ft.Dropdown(
        label="🎮 طور اللعب", value="3+ Players", width=160,
        options=[ft.dropdown.Option("2 Players (تخمين)"), ft.dropdown.Option("3+ Players (إمبوستر)")]
    )

    premium_input = ft.TextField(label="💎 كود البريميوم السري", width=160, password=True, can_reveal_password=True)
    premium_status = ft.Text("", size=12, color=ft.Colors.GREEN_ACCENT, weight=ft.FontWeight.BOLD)

    # دالة تفعيل البريميوم
    def activate_premium(e):
        nonlocal is_premium
        if premium_input.value.strip().upper() == "J7ELTE":
            is_premium = True
            premium_status.value = "💎 تم تفعيل البريميوم وفتح الكلمات الإضافية!"
            premium_container.visible = False
        else:
            premium_status.value = "❌ كود خاطئ! حاول مجدداً."
        page.update()

    btn_premium = ft.ElevatedButton("🔓 تفعيل", on_click=activate_premium, width=90, bgcolor=ft.Colors.AMBER_700)

    # حفظ الأسماء يدوياً
    def save_name_click(e):
        name = name_input.value.strip()
        if name and name not in game_data["players"]:
            game_data["players"].append(name)
            name_input.value = ""
            name_input.label = f"✍️ اسم اللاعب {len(game_data['players']) + 1}"
            
            players_view.controls.clear()
            for p in game_data["players"]:
                players_view.controls.append(
                    ft.Text(f"👤 {p}", size=16, color=ft.Colors.GREEN_300, weight=ft.FontWeight.W_500)
                )
                
            if mode_dropdown.value == "2 Players (تخمين)" and len(game_data["players"]) >= 2:
                btn_start.visible = True
            elif mode_dropdown.value == "3+ Players (إمبوستر)" and len(game_data["players"]) >= 3:
                btn_start.visible = True
        page.update()

    btn_add_name.on_click = save_name_click

    # بدء الجولة
    def start_match(e):
        game_data["mode"] = mode_dropdown.value
        game_data["imposter"] = random.choice(game_data["players"])
        
        pool = {**WORDS_FREE, **WORDS_PREMIUM} if is_premium else WORDS_FREE
        cat = random.choice(list(pool.keys()))
        game_data["word"] = f"{cat} -> {random.choice(pool[cat])}"
        game_data["current_idx"] = 0
        
        setup_container.visible = False
        btn_start.visible = False
        show_player_turn()

    def show_player_turn():
        idx = game_data["current_idx"]
        if idx < len(game_data["players"]):
            p_name = game_data["players"][idx]
            status_text.value = f"📱 مرر الجهاز إلى: ⭐ [{p_name}] ⭐\n\nواضغط بالأسفل لكشف الكلمة سرياً!"
            word_display.value = ""
            btn_action.text = f"👀 أنا {p_name}"
            btn_action.visible = True
            btn_action.on_click = reveal_identity
        else:
            btn_action.visible = False
            if game_data["mode"] == "2 Players (تخمين)":
                status_text.value = "🗣️ اسأل صاحبك الآن لتعرف الكلمة!\n\nاضغط بالأسفل عند الانتهاء وتأكيد التخمين!"
                btn_finish_2p.visible = True
            else:
                status_text.value = "🚨 ناقشوا معاً واكشفوا المحتال!\n\nصوّتوا الآن بالأسفل ضد الشخص المشكوك فيه:"
                voting_zone.controls.clear()
                for name in game_data["players"]:
                    voting_zone.controls.append(
                        ft.ElevatedButton(text=f"📌 صوّت ضد: {name}", width=240, height=45, bgcolor=ft.Colors.RED_900, data=name, on_click=vote_submit)
                    )
        page.update()

    def reveal_identity(e):
        idx = game_data["current_idx"]
        p_name = game_data["players"][idx]
        
        if p_name == game_data["imposter"] and game_data["mode"] == "3+ Players (إمبوستر)":
            word_display.value = "🤫 أنت الـ IMPOSTER (المحتال)!\n\nحاول الخداع وإعطاء إجابات عامة تمويهية! 🦊"
        elif p_name == game_data["imposter"] and game_data["mode"] == "2 Players (تخمين)":
            word_display.value = f"🧠 أنت العارف بالكلمة!\n\nالكلمة هي: [{game_data['word']}]\n\nأجب بصوتك بـ (نعم/لا) فقط! 🗣️"
        else:
            word_display.value = f"يا {p_name}، الكلمة السرية هي:\n\n🎉 [{game_data['word']}] 🎉"
            
        btn_action.text = "🙈 فهمت، اخفِ الشاشة ومرر الجهاز"
        btn_action.on_click = next_player
        page.update()

    def next_player(e):
        game_data["current_idx"] += 1
        show_player_turn()

    def vote_submit(e):
        voted = e.control.data
        imp = game_data["imposter"]
        voting_zone.controls.clear()
        
        if voted == imp:
            word_display.value = f"🎉 فوز ساحق للجمهور! 🎉\n\nتم كشف وطرد المحتال ({imp}) بنجاح!"
            word_display.color = ft.Colors.GREEN_ACCENT
        else:
            word_display.value = f"💀 خسارة فادحة! 💀\n\nطردتم بريء والمسؤول الحقيقي هو ({imp})!\n\nالكلمة كانت: {game_data['word']}"
            word_display.color = ft.Colors.RED_ACCENT
        end_game()

    def finish_2p_click(e):
        btn_finish_2p.visible = False
        word_display.value = f"🎯 تحدي التخمين انتهى!\n\nالكلمة المطلوبة كانت: 🎉 [{game_data['word']}] 🎉"
        word_display.color = ft.Colors.GREEN_ACCENT
        end_game()

    def end_game():
        status_text.value = "🏁 الجولة انتهت بنجاح!"
        btn_restart.visible = True
        page.update()

    def restart_game(e):
        game_data["players"] = []
        name_input.label = "✍️ اسم اللاعب 1"
        setup_container.visible = True
        btn_restart.visible = False
        btn_finish_2p.visible = False
        word_display.value = ""
        word_display.color = ft.Colors.AMBER
        status_text.value = "اختر طور اللعب وسجل الأسماء للبدء!"
        if not is_premium:
            premium_container.visible = True
            premium_status.value = ""
        page.update()

    premium_container = ft.Row([premium_input, btn_premium], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    # الحاوية الرئيسية مصلحة ومنظمة بمسافات داخلية ممتازة (spacing=20)
    setup_container = ft.Container(
        content=ft.Column([
            ft.Row([mode_dropdown], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([name_input, btn_add_name], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            premium_container,
            ft.Row([premium_status], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=15, color=ft.Colors.WHITE12),
            players_view
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        padding=20, border_radius=15, 
        border=ft.Border(top=ft.BorderSide(1, theme_color), bottom=ft.BorderSide(1, theme_color), left=ft.BorderSide(1, theme_color), right=ft.BorderSide(1, theme_color)),
        blur=15, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), width=410
    )

    # إصلاح الأزرار السفلية وإعادتها كعناصر Flet مباشرة لتعمل الواجهة فوراً وبدون تعليق الشاشة البيضاء
    btn_action = ft.ElevatedButton("Action", visible=False, width=250, height=45)
    btn_finish_2p = ft.ElevatedButton("🎯 إنهاء التحدي ورؤية الكلمة", on_click=finish_2p_click, visible=False, width=250, height=45, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700))
    btn_start = ft.ElevatedButton("🚀 ابدأ جولة توزيع الأدوار", on_click=start_match, visible=False, width=250, height=45, style=ft.ButtonStyle(bgcolor=theme_color))
    btn_restart = ft.ElevatedButton("🔄 جولة جديدة من الصفر", on_click=restart_game, visible=False, width=250, height=45)

    page.add(
        title_text, 
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        status_text, 
        ft.Divider(height=15, color=ft.Colors.WHITE24), 
        setup_container, 
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        word_display, 
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        btn_action, 
        voting_zone, 
        btn_finish_2p, 
        btn_start, 
        btn_restart
    )

ft.app(target=main, view=ft.AppView.FLET_APP)
