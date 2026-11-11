from __future__ import annotations

import asyncio
import tkinter as tk

from circe_app.knowledge.scenario import SCENARIO_TREE
from circe_app.orchestrator import CIRCEOrchestrator


BG = "#F5F8FB"
WHITE = "#FFFFFF"
PURPLE = "#6C4FE0"
PURPLE_DARK = "#4E37B5"
GREEN = "#4CD27F"
GREEN_DARK = "#2FA85F"
YELLOW = "#FFC83D"
YELLOW_DARK = "#D9A000"
BLUE = "#6EB8FF"
TEXT = "#26323F"
MUTED = "#667585"
LINE = "#E1E7EE"
SOFT = "#EEF2F6"
RED = "#FF5A5F"


class CIRCEGuiApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CIRCE · Escape Room de Ciberseguridad")
        self.geometry("1280x820")
        self.minsize(1100, 760)
        self.configure(bg=BG)

        self.orchestrator = CIRCEOrchestrator()
        self.current_screen = "start"
        self.screens = {}

        self.build_ui()
        self.show_screen("start")

    def build_ui(self) -> None:
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)

        self.screens["start"] = self.build_start_screen(container)
        self.screens["sim"] = self.build_sim_screen(container)
        self.screens["results"] = self.build_results_screen(container)

    def build_start_screen(self, parent):
        screen = tk.Frame(parent, bg=BG)
        screen.pack(fill="both", expand=True)

        topbar = tk.Frame(screen, bg=WHITE, height=72, highlightbackground=LINE, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="circe", bg=WHITE, fg=PURPLE, font=("Nunito", 28, "bold"), padx=32, anchor="w").pack(side="left", fill="y")
        tk.Label(topbar, text="Universidad Tecnológica Tula-Tepeji", bg=WHITE, fg=MUTED, font=("Nunito", 12, "bold")).place(x=760, y=24)

        main = tk.Frame(screen, bg=BG)
        main.pack(fill="both", expand=True, padx=60, pady=36)

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="y", padx=46)

        speech = tk.Frame(left, bg=WHITE, bd=2, relief="solid", highlightthickness=2, highlightbackground=LINE, padx=22, pady=20)
        speech.pack(anchor="center", pady=20)
        tk.Label(speech, text="¡Hola! Soy Circe. Hoy tú diriges la respuesta a un incidente de ciberseguridad, y lo harás hablando.", bg=WHITE, fg=TEXT, wraplength=360, justify="center", font=("Nunito", 21, "bold")).pack()

        avatar = tk.Canvas(left, width=220, height=220, bg=BG, highlightthickness=0)
        avatar.pack(pady=10)
        avatar.create_polygon(60, 20, 160, 20, 200, 60, 200, 160, 160, 200, 60, 200, 20, 160, 20, 60, fill=PURPLE, outline=PURPLE_DARK, width=4)
        avatar.create_oval(60, 80, 95, 115, fill="white")
        avatar.create_oval(125, 80, 160, 115, fill="white")
        avatar.create_oval(70, 88, 84, 102, fill=TEXT)
        avatar.create_oval(136, 88, 150, 102, fill=TEXT)
        avatar.create_arc(70, 120, 150, 180, start=200, extent=120, fill="", outline=TEXT, width=4)
        avatar.create_line(20, 60, 42, 90, fill=TEXT, width=4)
        avatar.create_line(200, 60, 178, 90, fill=TEXT, width=4)

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Aprende ciberseguridad con tu voz", bg=BG, fg=TEXT, font=("Nunito", 38, "bold"), justify="left", anchor="w").pack(anchor="w")
        tk.Label(right, text="Toma decisiones, gana XP y descubre qué pasa con cada una.", bg=BG, fg=MUTED, font=("Nunito", 18, "bold")).pack(anchor="w", pady=24)

        scenario = tk.Frame(right, bg=WHITE, bd=2, relief="solid", highlightbackground=GREEN, highlightthickness=2, padx=18, pady=18)
        scenario.pack(fill="x", pady=18)

        left_cell = tk.Frame(scenario, bg=GREEN, width=72, height=72)
        left_cell.pack_propagate(False)
        left_cell.pack(side="left")
        tk.Label(left_cell, text="🗄", bg=GREEN, fg="#10202B", font=("Segoe UI Emoji", 28), justify="center").pack(expand=True)

        text_box = tk.Frame(scenario, bg=WHITE)
        text_box.pack(side="left", fill="x", expand=True, padx=18)
        tk.Label(text_box, text="Filtración de datos", bg=WHITE, fg=TEXT, font=("Nunito", 20, "bold")).pack(anchor="w")
        tk.Label(text_box, text="Eres el responsable de la respuesta · 5 decisiones", bg=WHITE, fg=MUTED, font=("Nunito", 13, "bold")).pack(anchor="w", pady=4)

        tk.Button(scenario, text="EMPEZAR", bg=GREEN, fg="#10202B", activebackground=GREEN_DARK, activeforeground="#10202B",
                  bd=0, font=("Nunito", 14, "bold"), command=lambda: self.show_screen("sim"), width=12, height=2).pack(side="right", padx=16)

        locked = tk.Frame(right, bg=SOFT, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=18, pady=16)
        locked.pack(fill="x")
        tk.Label(locked, text="🔒", bg=SOFT, fg=MUTED, font=("Segoe UI Emoji", 22)).pack(side="left")
        tk.Label(locked, text="Nuevos escenarios próximamente", bg=SOFT, fg=MUTED, font=("Nunito", 16, "bold")).pack(side="left", padx=12)

        audio_box = tk.Frame(right, bg=WHITE, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=20, pady=18)
        audio_box.pack(fill="x", pady=18)

        tk.Label(audio_box, text="Prepara tu audio", bg=WHITE, fg=TEXT, font=("Nunito", 15, "bold"), anchor="w").pack(anchor="w")

        row1 = tk.Frame(audio_box, bg=WHITE)
        row1.pack(fill="x", pady=12)
        tk.Label(row1, text="Micrófono", bg=WHITE, fg=TEXT, font=("Nunito", 13, "bold")).pack(side="left")
        level = tk.Frame(row1, bg=WHITE)
        level.pack(side="left", fill="x", expand=True, padx=18)
        for i in range(12):
            h = [10, 14, 18, 20, 22, 18, 15, 20, 16, 12, 18, 22][i]
            bar = tk.Frame(level, bg=GREEN if i < 9 else LINE, width=10, height=h)
            bar.pack(side="left", padx=3, anchor="s")
        tk.Label(row1, text="Listo", bg="#DDF7E8", fg="#146B3A", font=("Nunito", 10, "bold"), padx=12, pady=4).pack(side="right")

        row2 = tk.Frame(audio_box, bg=WHITE)
        row2.pack(fill="x", pady=8)
        tk.Label(row2, text="Altavoces", bg=WHITE, fg=TEXT, font=("Nunito", 13, "bold")).pack(side="left")
        tk.Label(row2, text="Escucharás a Circe con este volumen.", bg=WHITE, fg=MUTED, font=("Nunito", 11, "bold")).pack(side="left", padx=16, fill="x", expand=True)
        tk.Button(row2, text="Probar", bg=WHITE, fg="#1D5FBF", activebackground=SOFT, activeforeground="#1D5FBF", font=("Nunito", 11, "bold"), bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2).pack(side="right")

        row3 = tk.Frame(audio_box, bg=WHITE)
        row3.pack(fill="x", pady=8)
        tk.Label(row3, text="Ruido ambiental", bg=WHITE, fg=TEXT, font=("Nunito", 13, "bold")).pack(side="left")
        tk.Label(row3, text="Si hay mucho, puedes responder escribiendo.", bg=WHITE, fg=MUTED, font=("Nunito", 11, "bold")).pack(side="left", padx=16, fill="x", expand=True)
        tk.Label(row3, text="Bajo", bg="#DDF7E8", fg="#146B3A", font=("Nunito", 10, "bold"), padx=12, pady=4).pack(side="right")

        return screen

    def build_sim_screen(self, parent):
        screen = tk.Frame(parent, bg=BG)
        screen.pack(fill="both", expand=True)

        topbar = tk.Frame(screen, bg=WHITE, height=72, highlightbackground=LINE, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        left_group = tk.Frame(topbar, bg=WHITE)
        left_group.pack(side="left", padx=16, fill="y")
        tk.Button(left_group, text="←", bg=WHITE, fg=MUTED, font=("Nunito", 18, "bold"), bd=2, relief="solid", highlightbackground=LINE, command=lambda: self.show_screen("start")).pack(side="left", pady=12, padx=14)
        tk.Label(left_group, text="circe", bg=WHITE, fg=PURPLE, font=("Nunito", 26, "bold")).pack(side="left", pady=12)

        progress = tk.Frame(topbar, bg=WHITE)
        progress.pack(side="left", fill="x", expand=True, padx=36)
        bar = tk.Frame(progress, bg="#E8EDF3", height=18, width=420)
        bar.pack(side="left", anchor="center")
        tk.Frame(bar, bg=GREEN, height=18, width=220).pack(side="left")
        tk.Label(progress, text="Decisión 3 de 5", bg=WHITE, fg=MUTED, font=("Nunito", 14, "bold")).pack(side="left", padx=18)

        status = tk.Frame(topbar, bg=WHITE)
        status.pack(side="right", padx=20, fill="y")
        tk.Label(status, text="⚡ 20 XP", bg=WHITE, fg="#B37A00", font=("Nunito", 16, "bold")).pack(side="left", padx=14)
        tk.Label(status, text="❤ 3", bg=WHITE, fg=RED, font=("Nunito", 16, "bold")).pack(side="left")

        body = tk.Frame(screen, bg=BG)
        body.pack(fill="both", expand=True, padx=26, pady=18)

        left_meta = tk.Frame(body, bg=BG, width=260)
        left_meta.pack(side="left", fill="y", padx=18)
        left_meta.pack_propagate(False)
        tk.Label(left_meta, text="Tu recorrido", bg=BG, fg=MUTED, font=("Nunito", 14, "bold"), anchor="w").pack(anchor="w", pady=14)

        for idx, label in enumerate([("Aislar el servidor", "ok"), ("Revisar registros", "part"), ("Contener la fuga", "active"), ("Decisión 4", "lock"), ("Decisión 5", "lock")]):
            row = tk.Frame(left_meta, bg=BG)
            row.pack(fill="x", pady=8)
            bubble = tk.Frame(row, bg=GREEN if label[1] == "ok" else YELLOW if label[1] == "part" else "#E8EDF3" if label[1] == "lock" else YELLOW, width=46, height=46)
            bubble.pack_propagate(False)
            bubble.pack(side="left")
            if label[1] == "ok":
                tk.Label(bubble, text="✓", bg=GREEN, fg="#10202B", font=("Nunito", 17, "bold")).pack(expand=True)
            elif label[1] == "part":
                tk.Label(bubble, text="◔", bg=YELLOW, fg="#3B2A00", font=("Nunito", 17, "bold")).pack(expand=True)
            elif label[1] == "active":
                tk.Label(bubble, text="🎙", bg=YELLOW, fg="#3B2A00", font=("Segoe UI Emoji", 16)).pack(expand=True)
            else:
                tk.Label(bubble, text="🔒", bg="#E8EDF3", fg="#8A97A6", font=("Segoe UI Emoji", 16)).pack(expand=True)
            tk.Label(row, text=label[0], bg=BG, fg=TEXT if label[1] in ["ok", "part", "active"] else "#8A97A6", font=("Nunito", 14, "bold")).pack(side="left", padx=12)
            if idx < 4:
                line = tk.Frame(left_meta, bg=LINE, height=22, width=4)
                line.pack(fill="x", pady=2)

        center = tk.Frame(body, bg=BG)
        center.pack(side="left", fill="both", expand=True)

        pill = tk.Label(center, text="Escenario · Filtración de datos", bg="#EDE8FF", fg="#4A32B8", font=("Nunito", 11, "bold"), padx=14, pady=6)
        pill.pack(anchor="w", pady=14)

        narrator = tk.Frame(center, bg=BG)
        narrator.pack(fill="x")
        avatar = tk.Canvas(narrator, width=120, height=130, bg=BG, highlightthickness=0)
        avatar.pack(side="left")
        avatar.create_polygon(32, 10, 92, 10, 110, 30, 110, 98, 92, 118, 32, 118, 10, 98, 10, 30, fill=PURPLE, outline=PURPLE_DARK, width=4)
        avatar.create_oval(35, 45, 50, 60, fill="white")
        avatar.create_oval(70, 45, 85, 60, fill="white")
        avatar.create_oval(39, 49, 46, 55, fill=TEXT)
        avatar.create_oval(74, 49, 81, 55, fill=TEXT)
        avatar.create_arc(42, 72, 80, 95, start=200, extent=120, fill="", outline=TEXT, width=4)
        bubble = tk.Frame(narrator, bg=WHITE, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=18, pady=16)
        bubble.pack(side="left", fill="x", expand=True)
        tk.Label(bubble, text="Circe, tu narradora", bg=WHITE, fg=PURPLE, font=("Nunito", 10, "bold")).pack(anchor="w")
        self.narrator_text = tk.Label(bubble, text="", bg=WHITE, fg=TEXT, wraplength=560, justify="left", font=("Nunito", 20, "bold"), anchor="w")
        self.narrator_text.pack(anchor="w", pady=10)

        answer_wrap = tk.Frame(center, bg=WHITE, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=18, pady=18)
        answer_wrap.pack(fill="x", pady=18)
        tk.Label(answer_wrap, text="Lo que dijiste", bg=WHITE, fg=MUTED, font=("Nunito", 12, "bold")).pack(anchor="w")
        self.answer_box = tk.Text(answer_wrap, height=5, wrap="word", font=("Nunito", 16), bg=WHITE, fg=TEXT, insertbackground=TEXT, bd=0)
        self.answer_box.pack(fill="x", pady=8)
        button_row = tk.Frame(answer_wrap, bg=WHITE)
        button_row.pack(fill="x")
        tk.Button(button_row, text="Grabar de nuevo", bg=WHITE, fg=TEXT, activebackground=SOFT, font=("Nunito", 11, "bold"), bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2).pack(side="left")
        tk.Button(button_row, text="Escribir en su lugar", bg=WHITE, fg=TEXT, activebackground=SOFT, font=("Nunito", 11, "bold"), bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=10).pack(side="left", padx=10)
        self.evaluate_button = tk.Button(button_row, text="Evaluar decisión", bg=GREEN, fg="#10202B", activebackground=GREEN_DARK, activeforeground="#10202B", font=("Nunito", 12, "bold"), bd=0, command=self.evaluate_current_turn)
        self.evaluate_button.pack(side="right")

        right_meta = tk.Frame(body, bg=BG, width=280)
        right_meta.pack(side="left", fill="y", padx=18)
        right_meta.pack_propagate(False)

        stats = tk.Frame(right_meta, bg=WHITE, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=18, pady=18)
        stats.pack(fill="x")
        tk.Label(stats, text="Estado del incidente", bg=WHITE, fg=TEXT, font=("Nunito", 15, "bold")).pack(anchor="w")
        for label, value, color in [("Contención", 40, "#FFC83D"), ("Datos", 72, GREEN), ("Servicio", 55, BLUE)]:
            box = tk.Frame(stats, bg=WHITE)
            box.pack(fill="x", pady=12)
            tk.Label(box, text=label, bg=WHITE, fg=TEXT, font=("Nunito", 11, "bold")).pack(anchor="w")
            bar_row = tk.Frame(box, bg=WHITE)
            bar_row.pack(fill="x", pady=4)
            tk.Label(bar_row, text=f"{value}%", bg=WHITE, fg=TEXT, font=("Nunito", 11, "bold")).pack(side="right")
            bar = tk.Frame(bar_row, bg="#E8EDF3", height=12)
            bar.pack(fill="x", side="left", expand=True)
            inner = tk.Frame(bar, bg=color, height=12)
            inner.pack(fill="y", side="left")
            inner.configure(width=int(190 * value / 100))

        hint = tk.Frame(right_meta, bg="#EAF4FF", bd=2, relief="solid", highlightbackground="#C9E2FF", highlightthickness=2, padx=16, pady=16)
        hint.pack(fill="x", pady=18)
        tk.Label(hint, text="💡 ¿Necesitas una pista?", bg="#EAF4FF", fg="#1D5FBF", font=("Nunito", 13, "bold")).pack(anchor="w")
        self.hint_text = tk.Label(hint, text="Piensa en qué conviene detener primero y a quién hay que avisar.", bg="#EAF4FF", fg="#3A4A5C", wraplength=220, justify="left", font=("Nunito", 11, "bold"), padx=0, pady=12)
        self.hint_text.pack(anchor="w")
        tk.Button(hint, text="Ver pista", bg=WHITE, fg="#1D5FBF", activebackground=SOFT, font=("Nunito", 11, "bold"), highlightbackground="#C9E2FF", bd=2, relief="solid", command=self.toggle_hint).pack(anchor="w", pady=12)

        feedback = tk.Frame(screen, bg="#FFF3CF", height=110, highlightbackground="#FFD968", highlightthickness=2)
        feedback.pack(fill="x", side="bottom")
        feedback.pack_propagate(False)
        left_fb = tk.Frame(feedback, bg="#FFF3CF")
        left_fb.pack(side="left", fill="both", expand=True, padx=24, pady=18)
        tk.Label(left_fb, text="¡Casi! Respuesta parcial · +5 XP", bg="#FFF3CF", fg="#7A4E00", font=("Nunito", 23, "bold")).pack(anchor="w")
        self.feedback_text = tk.Label(left_fb, text="", bg="#FFF3CF", fg="#6B4A12", wraplength=720, justify="left", font=("Nunito", 13, "bold"), anchor="w")
        self.feedback_text.pack(anchor="w", pady=4)
        tk.Button(feedback, text="Continuar", bg=YELLOW, fg="#3B2A00", activebackground=YELLOW_DARK, activeforeground="#3B2A00", bd=0, font=("Nunito", 15, "bold"), command=lambda: self.show_screen("results"), width=16, height=2).pack(side="right", padx=26, pady=22)

        self.refresh_scene()
        return screen

    def build_results_screen(self, parent):
        screen = tk.Frame(parent, bg=BG)
        screen.pack(fill="both", expand=True)

        topbar = tk.Frame(screen, bg=WHITE, height=72, highlightbackground=LINE, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="circe", bg=WHITE, fg=PURPLE, font=("Nunito", 28, "bold"), padx=32, anchor="w").pack(side="left", fill="y")
        tk.Label(topbar, text="Escenario · Filtración de datos", bg=WHITE, fg=MUTED, font=("Nunito", 12, "bold")).pack(side="right", padx=24, fill="y")

        main = tk.Frame(screen, bg=BG)
        main.pack(fill="both", expand=True, padx=60, pady=34)

        left = tk.Frame(main, bg=BG, width=430)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        canvas = tk.Canvas(left, width=220, height=220, bg=BG, highlightthickness=0)
        canvas.pack(pady=12)
        canvas.create_oval(40, 10, 180, 150, fill="#EAF6F0", outline="#A7E7C3", width=2)
        canvas.create_oval(60, 10, 160, 110, fill=PURPLE, outline=PURPLE_DARK, width=4)
        canvas.create_oval(75, 50, 95, 70, fill="white")
        canvas.create_oval(125, 50, 145, 70, fill="white")
        canvas.create_oval(80, 54, 90, 64, fill=TEXT)
        canvas.create_oval(130, 54, 140, 64, fill=TEXT)
        canvas.create_arc(80, 75, 140, 120, start=210, extent=120, fill="", outline=TEXT, width=4)

        tk.Label(left, text="¡Incidente contenido!", bg=BG, fg=TEXT, font=("Nunito", 34, "bold"), justify="center").pack(anchor="center")
        tk.Label(left, text="Lo lograste, aunque investigar antes de contener dejó que la fuga siguiera unos minutos más.", bg=BG, fg=MUTED, font=("Nunito", 16, "bold"), wraplength=360, justify="center").pack(anchor="center", pady=20)

        tiles = tk.Frame(left, bg=BG)
        tiles.pack(fill="x")
        for label, value, color, bg in [("XP total", "35 XP", "#B37A00", "#FFF1BE"), ("Tiempo", "11:48", "#1D5FBF", "#EAF4FF"), ("Vidas", "3 de 3", "#D93A40", "#FFE5E7")]:
            tile = tk.Frame(tiles, bg=bg, highlightbackground=LINE, highlightthickness=2, padx=10, pady=10)
            tile.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(tile, text=label, bg=bg, fg=color, font=("Nunito", 11, "bold")).pack(anchor="center")
            tk.Label(tile, text=value, bg=bg, fg=color, font=("Nunito", 21, "bold")).pack(anchor="center", pady=8)

        tk.Button(left, text="REINTENTAR EL ESCENARIO", bg=GREEN, fg="#10202B", activebackground=GREEN_DARK, activeforeground="#10202B", bd=0, font=("Nunito", 14, "bold"), command=lambda: self.reset_session_for_results()).pack(fill="x", pady=20)
        tk.Button(left, text="Escuchar resumen de Circe", bg=WHITE, fg=TEXT, activebackground=SOFT, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, font=("Nunito", 12, "bold")).pack(fill="x")

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=32)
        tk.Label(right, text="Repaso de tus decisiones", bg=BG, fg=TEXT, font=("Nunito", 18, "bold")).pack(anchor="w", pady=12)

        for title, desc, xp, style in [
            ("Aislar el servidor afectado", "Frenaste la propagación y conservaste las pruebas.", "+10 XP", "ok"),
            ("Revisar los registros de acceso", "Buen análisis, pero antes de contener: la descarga siguió activa.", "+5 XP", "part"),
            ("Cortar la cuenta y el tráfico saliente", "Detuviste la fuga, pero faltó avisar al responsable de seguridad.", "+5 XP", "part"),
        ]:
            row = tk.Frame(right, bg=WHITE, bd=2, relief="solid", highlightbackground=LINE, highlightthickness=2, padx=16, pady=14)
            row.pack(fill="x", pady=10)
            bubble = tk.Frame(row, bg=GREEN if style == "ok" else YELLOW, width=40, height=40)
            bubble.pack_propagate(False)
            bubble.pack(side="left")
            tk.Label(bubble, text="✓" if style == "ok" else "◔", bg=GREEN if style == "ok" else YELLOW, fg="#10202B" if style == "ok" else "#3B2A00", font=("Nunito", 16, "bold")).pack(expand=True)
            body = tk.Frame(row, bg=WHITE)
            body.pack(side="left", fill="x", expand=True, padx=14)
            tk.Label(body, text=title, bg=WHITE, fg=TEXT, font=("Nunito", 14, "bold")).pack(anchor="w")
            tk.Label(body, text=desc, bg=WHITE, fg=MUTED, font=("Nunito", 11, "bold"), wraplength=360, justify="left").pack(anchor="w")
            tk.Label(row, text=xp, bg=WHITE, fg="#146B3A" if style == "ok" else "#B37A00", font=("Nunito", 12, "bold")).pack(side="right")

        summary = tk.Frame(right, bg="#EDE8FF", bd=2, relief="solid", highlightbackground="#D5CBFF", highlightthickness=2, padx=16, pady=16)
        summary.pack(fill="x", pady=12)
        tk.Label(summary, text="Para reforzar la próxima vez", bg="#EDE8FF", fg="#4A32B8", font=("Nunito", 13, "bold")).pack(anchor="w")
        tk.Label(summary, text="Contén primero y analiza después. Al comunicar un incidente, indica qué datos pudieron quedar expuestos.", bg="#EDE8FF", fg="#3A2F6B", font=("Nunito", 12, "bold"), wraplength=480, justify="left").pack(anchor="w", pady=8)

        return screen

    def show_screen(self, name):
        if name not in self.screens:
            return
        for key, frame in self.screens.items():
            frame.pack_forget()
        self.screens[name].pack(fill="both", expand=True)
        self.current_screen = name
        if name == "sim":
            self.refresh_scene()

    def refresh_scene(self):
        node = SCENARIO_TREE[self.orchestrator.current_node]
        self.narrator_text.config(text=node.prompt)
        self.answer_box.delete("1.0", "end")

    def toggle_hint(self):
        current = self.hint_text.cget("text")
        if current.startswith("Piensa"):
            self.hint_text.config(text="Primero debes aislar el sistema ante un acceso sospechoso; luego revisas registros y alertas para coordinar la respuesta.")
        else:
            self.hint_text.config(text="Piensa en qué conviene detener primero y a quién hay que avisar.")

    def evaluate_current_turn(self):
        answer = self.answer_box.get("1.0", "end").strip()
        if not answer:
            self.feedback_text.config(text="Escribe o habla tu decisión antes de evaluar.")
            return

        try:
            result = asyncio.run(self.orchestrator.process_student_turn(answer))
            verdict = result["evaluation"].get("verdict", "partial")
            reason = result["evaluation"].get("reason", "")
            recommended = result["evaluation"].get("recommended_action", "")
            self.feedback_text.config(text=f"{reason} Recomendación: {recommended}")
            self.narrator_text.config(text=result["node_prompt"])
            if result.get("scenario_completed"):
                self.show_screen("results")
        except Exception as exc:
            self.feedback_text.config(text=f"No se pudo evaluar la decisión: {exc}")

    def reset_session_for_results(self):
        self.orchestrator = CIRCEOrchestrator()
        self.show_screen("sim")
        self.refresh_scene()


def main() -> None:
    app = CIRCEGuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
