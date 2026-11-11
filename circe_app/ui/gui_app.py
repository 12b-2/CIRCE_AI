from __future__ import annotations

import asyncio
import threading
import tkinter as tk
from typing import Any

from circe_app.knowledge.scenario import list_levels
from circe_app.orchestrator import CIRCEOrchestrator
from circe_app.services import check_local_capabilities


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
RED_LIGHT = "#FFE5E7"
RED_DARK = "#9E1C20"


class CIRCEGuiApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CIRCE · Simulador de Ciberseguridad por Voz e IA (5 Niveles)")
        self.geometry("1320x860")
        self.minsize(1140, 780)
        self.configure(bg=BG)

        self.runtime_status = check_local_capabilities()
        self.orchestrator = CIRCEOrchestrator(level_id="level_1")
        self.completed_levels: dict[str, float] = {}
        self.current_screen = "start"
        self.screens: dict[str, tk.Frame] = {}
        self.input_mode = "voice"
        self.awaiting_next_node = False
        self.last_spoken_feedback = ""

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.build_ui()
        self.show_screen("start")

    def _on_close(self) -> None:
        try:
            self.orchestrator.tts.stop()
            if self.orchestrator.stt.is_recording:
                self.orchestrator.stt.stop_stream_recording()
        except Exception:
            pass
        self.destroy()

    def build_ui(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()
        self.screens["start"] = self.build_start_screen(self.container)
        self.screens["sim"] = self.build_sim_screen(self.container)
        self.screens["results"] = self.build_results_screen(self.container)

    # =========================================================================
    # PANTALLA 1: INICIO Y SELECCIÓN DE LOS 5 NIVELES
    # =========================================================================
    def build_start_screen(self, parent: tk.Widget) -> tk.Frame:
        screen = tk.Frame(parent, bg=BG)

        topbar = tk.Frame(screen, bg=WHITE, height=68, highlightbackground=LINE, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(
            topbar,
            text="circe",
            bg=WHITE,
            fg=PURPLE,
            font=("Nunito", 26, "bold"),
            padx=28,
            anchor="w",
        ).pack(side="left", fill="y")

        ai_badge_text = (
            f"IA: Ollama ({self.orchestrator.llm.model})"
            if self.runtime_status.llm_available
            else "IA: Evaluador Semántico + Voz Local"
        )
        tk.Label(
            topbar,
            text=f"Universidad Tecnológica Tula-Tepeji  ·  {ai_badge_text}",
            bg=WHITE,
            fg=MUTED,
            font=("Nunito", 11, "bold"),
            padx=24,
        ).pack(side="right", fill="y")

        main = tk.Frame(screen, bg=BG)
        main.pack(fill="both", expand=True, padx=40, pady=20)

        # Columna izquierda: Avatar de Circe + Panel de Audio y Voz
        left = tk.Frame(main, bg=BG, width=380)
        left.pack(side="left", fill="y", padx=(0, 28))
        left.pack_propagate(False)

        speech = tk.Frame(
            left,
            bg=WHITE,
            bd=2,
            relief="solid",
            highlightthickness=2,
            highlightbackground=LINE,
            padx=18,
            pady=14,
        )
        speech.pack(fill="x", pady=(4, 10))
        tk.Label(
            speech,
            text=(
                "¡Hola! Soy Circe. Elige cualquiera de los 5 niveles. "
                "Escucharás y leerás cada instrucción, y podrás responder con tu voz o por texto."
            ),
            bg=WHITE,
            fg=TEXT,
            wraplength=330,
            justify="center",
            font=("Nunito", 13, "bold"),
        ).pack()

        avatar = tk.Canvas(left, width=160, height=160, bg=BG, highlightthickness=0)
        avatar.pack(pady=4)
        avatar.create_polygon(
            45, 15, 115, 15, 145, 45, 145, 115, 115, 145, 45, 145, 15, 115, 15, 45,
            fill=PURPLE, outline=PURPLE_DARK, width=3,
        )
        avatar.create_oval(45, 58, 70, 83, fill="white")
        avatar.create_oval(90, 58, 115, 83, fill="white")
        avatar.create_oval(52, 64, 63, 75, fill=TEXT)
        avatar.create_oval(97, 64, 108, 75, fill=TEXT)
        avatar.create_arc(52, 88, 108, 130, start=200, extent=140, fill="", outline=TEXT, width=3)

        # Panel de diagnóstico y prueba de audio
        audio_box = tk.Frame(
            left,
            bg=WHITE,
            bd=2,
            relief="solid",
            highlightbackground=LINE,
            highlightthickness=2,
            padx=16,
            pady=14,
        )
        audio_box.pack(fill="x", pady=10)
        tk.Label(
            audio_box,
            text="Configuración de Voz e IA",
            bg=WHITE,
            fg=TEXT,
            font=("Nunito", 13, "bold"),
            anchor="w",
        ).pack(anchor="w")

        row1 = tk.Frame(audio_box, bg=WHITE)
        row1.pack(fill="x", pady=8)
        tk.Label(row1, text="🎙 Micrófono (STT)", bg=WHITE, fg=TEXT, font=("Nunito", 11, "bold")).pack(side="left")
        self.start_mic_bars: list[tk.Frame] = []
        level_frame = tk.Frame(row1, bg=WHITE)
        level_frame.pack(side="left", fill="x", expand=True, padx=10)
        for i in range(10):
            h = [8, 12, 15, 18, 20, 16, 14, 18, 12, 16][i]
            bar = tk.Frame(level_frame, bg=GREEN if i < 7 else LINE, width=8, height=h)
            bar.pack(side="left", padx=2, anchor="s")
            self.start_mic_bars.append(bar)
        stt_label = "Listo" if self.runtime_status.stt_available else "Texto"
        tk.Label(
            row1,
            text=stt_label,
            bg="#DDF7E8" if self.runtime_status.stt_available else "#FFF3CF",
            fg="#146B3A" if self.runtime_status.stt_available else "#7A4E00",
            font=("Nunito", 9, "bold"),
            padx=8,
            pady=2,
        ).pack(side="right")

        row2 = tk.Frame(audio_box, bg=WHITE)
        row2.pack(fill="x", pady=6)
        tk.Label(row2, text="🔊 Altavoces (TTS)", bg=WHITE, fg=TEXT, font=("Nunito", 11, "bold")).pack(side="left")
        tk.Button(
            row2,
            text="🔊 Probar voz de Circe",
            bg=WHITE,
            fg="#1D5FBF",
            activebackground=SOFT,
            font=("Nunito", 10, "bold"),
            bd=1,
            relief="solid",
            padx=10,
            pady=3,
            command=self._test_speaker_voice,
        ).pack(side="right")

        row3 = tk.Frame(audio_box, bg=WHITE)
        row3.pack(fill="x", pady=6)
        tk.Label(row3, text="🤖 Modelo Evaluador", bg=WHITE, fg=TEXT, font=("Nunito", 11, "bold")).pack(side="left")
        tk.Label(
            row3,
            text="Ollama + Semántico",
            bg="#EDE8FF",
            fg="#4A32B8",
            font=("Nunito", 9, "bold"),
            padx=8,
            pady=2,
        ).pack(side="right")

        # Columna derecha: Catálogo interactivo de los 5 Niveles
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            right,
            text="Entrena ciberseguridad con tu voz (5 Niveles)",
            bg=BG,
            fg=TEXT,
            font=("Nunito", 26, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            right,
            text="Cada nivel presenta 5 situaciones con instrucciones en texto y audio. Responde hablando o escribiendo.",
            bg=BG,
            fg=MUTED,
            font=("Nunito", 12, "bold"),
        ).pack(anchor="w", pady=(2, 12))

        levels_container = tk.Frame(right, bg=BG)
        levels_container.pack(fill="both", expand=True)

        for lvl in list_levels():
            is_done = lvl.id in self.completed_levels
            border_color = GREEN if lvl.level_number == 1 or is_done else PURPLE
            card = tk.Frame(
                levels_container,
                bg=WHITE,
                bd=2,
                relief="solid",
                highlightbackground=border_color,
                highlightthickness=2,
                padx=14,
                pady=10,
            )
            card.pack(fill="x", pady=5)

            icon_box = tk.Frame(card, bg=GREEN if is_done else "#EDE8FF", width=52, height=52)
            icon_box.pack_propagate(False)
            icon_box.pack(side="left")
            tk.Label(
                icon_box,
                text=lvl.icon,
                bg=GREEN if is_done else "#EDE8FF",
                fg=TEXT,
                font=("Segoe UI Emoji", 20),
            ).pack(expand=True)

            info_box = tk.Frame(card, bg=WHITE)
            info_box.pack(side="left", fill="x", expand=True, padx=14)

            header_row = tk.Frame(info_box, bg=WHITE)
            header_row.pack(fill="x")
            tk.Label(
                header_row,
                text=lvl.title,
                bg=WHITE,
                fg=TEXT,
                font=("Nunito", 14, "bold"),
            ).pack(side="left")
            tk.Label(
                header_row,
                text=lvl.difficulty.strip(),
                bg=SOFT,
                fg=PURPLE_DARK,
                font=("Nunito", 9, "bold"),
                padx=8,
                pady=2,
            ).pack(side="left", padx=10)
            if is_done:
                tk.Label(
                    header_row,
                    text=f"✓ Completado ({self.completed_levels[lvl.id]:.0f} pts)",
                    bg="#DDF7E8",
                    fg="#146B3A",
                    font=("Nunito", 9, "bold"),
                    padx=8,
                    pady=2,
                ).pack(side="left")

            tk.Label(
                info_box,
                text=f"{lvl.subtitle} — {lvl.description}",
                bg=WHITE,
                fg=MUTED,
                font=("Nunito", 10, "bold"),
                anchor="w",
                justify="left",
                wraplength=610,
            ).pack(anchor="w", pady=(2, 0))

            tk.Button(
                card,
                text="JUGAR NIVEL",
                bg=GREEN,
                fg="#10202B",
                activebackground=GREEN_DARK,
                activeforeground="#10202B",
                bd=0,
                font=("Nunito", 11, "bold"),
                width=13,
                height=2,
                command=lambda lid=lvl.id: self.start_level(lid),
            ).pack(side="right", padx=8)

        return screen

    # =========================================================================
    # PANTALLA 2: SIMULACIÓN INTERACTIVA (5 DECISIONES POR VOZ Y TEXTO)
    # =========================================================================
    def build_sim_screen(self, parent: tk.Widget) -> tk.Frame:
        screen = tk.Frame(parent, bg=BG)

        # Barra superior
        topbar = tk.Frame(screen, bg=WHITE, height=68, highlightbackground=LINE, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        left_group = tk.Frame(topbar, bg=WHITE)
        left_group.pack(side="left", padx=14, fill="y")
        tk.Button(
            left_group,
            text="← Niveles",
            bg=WHITE,
            fg=TEXT,
            font=("Nunito", 11, "bold"),
            bd=1,
            relief="solid",
            padx=10,
            command=self._return_to_start,
        ).pack(side="left", pady=14, padx=8)
        tk.Label(left_group, text="circe", bg=WHITE, fg=PURPLE, font=("Nunito", 24, "bold")).pack(
            side="left", pady=10, padx=6
        )

        # Barra de progreso dinámica (1 a 5)
        progress = tk.Frame(topbar, bg=WHITE)
        progress.pack(side="left", fill="x", expand=True, padx=24)
        self.progress_bar_outer = tk.Frame(progress, bg="#E8EDF3", height=16, width=360)
        self.progress_bar_outer.pack(side="left", pady=24)
        self.progress_bar_outer.pack_propagate(False)
        self.progress_bar_inner = tk.Frame(self.progress_bar_outer, bg=GREEN, height=16, width=72)
        self.progress_bar_inner.pack(side="left", fill="y")
        self.progress_label = tk.Label(
            progress,
            text="Nivel 1 de 5",
            bg=WHITE,
            fg=MUTED,
            font=("Nunito", 13, "bold"),
        )
        self.progress_label.pack(side="left", padx=14)

        # Botón para activar/silenciar locución automática + indicadores XP y Vidas
        status = tk.Frame(topbar, bg=WHITE)
        status.pack(side="right", padx=18, fill="y")
        self.auto_tts_btn = tk.Button(
            status,
            text="🔊 Voz Auto: ON",
            bg="#EDE8FF",
            fg=PURPLE_DARK,
            font=("Nunito", 10, "bold"),
            bd=0,
            padx=10,
            pady=4,
            command=self._toggle_auto_tts,
        )
        self.auto_tts_btn.pack(side="left", padx=10)
        self.xp_label = tk.Label(status, text="⚡ 0 XP", bg=WHITE, fg="#B37A00", font=("Nunito", 15, "bold"))
        self.xp_label.pack(side="left", padx=12)
        self.lives_label = tk.Label(status, text="❤ 3", bg=WHITE, fg=RED, font=("Nunito", 15, "bold"))
        self.lives_label.pack(side="left")

        # Cuerpo central de 3 columnas
        body = tk.Frame(screen, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=12)

        # Columna izquierda: Recorrido de los 5 niveles/etapas
        self.left_meta = tk.Frame(body, bg=BG, width=250)
        self.left_meta.pack(side="left", fill="y", padx=(4, 16))
        self.left_meta.pack_propagate(False)
        tk.Label(
            self.left_meta,
            text="Progreso (5 Niveles)",
            bg=BG,
            fg=MUTED,
            font=("Nunito", 13, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(6, 10))
        self.timeline_container = tk.Frame(self.left_meta, bg=BG)
        self.timeline_container.pack(fill="both", expand=True)

        # Columna central: Instrucciones (Texto + Audio) y Respuesta (Audio o Texto)
        center = tk.Frame(body, bg=BG)
        center.pack(side="left", fill="both", expand=True)

        top_pill_row = tk.Frame(center, bg=BG)
        top_pill_row.pack(fill="x", pady=(2, 8))
        self.scenario_pill = tk.Label(
            top_pill_row,
            text="Nivel 1 · Filtración de datos",
            bg="#EDE8FF",
            fg="#4A32B8",
            font=("Nunito", 11, "bold"),
            padx=12,
            pady=4,
        )
        self.scenario_pill.pack(side="left")

        self.engine_badge = tk.Label(
            top_pill_row,
            text="Audio STT + TTS Activo",
            bg="#DDF7E8",
            fg="#146B3A",
            font=("Nunito", 10, "bold"),
            padx=10,
            pady=4,
        )
        self.engine_badge.pack(side="right")

        # Bloque Narradora (Instrucciones en texto + controles de audio)
        narrator = tk.Frame(center, bg=BG)
        narrator.pack(fill="x")
        avatar = tk.Canvas(narrator, width=105, height=115, bg=BG, highlightthickness=0)
        avatar.pack(side="left", padx=(0, 10))
        avatar.create_polygon(
            28, 10, 82, 10, 98, 28, 98, 88, 82, 106, 28, 106, 10, 88, 10, 28,
            fill=PURPLE, outline=PURPLE_DARK, width=3,
        )
        avatar.create_oval(32, 40, 46, 54, fill="white")
        avatar.create_oval(62, 40, 76, 54, fill="white")
        avatar.create_oval(36, 44, 42, 50, fill=TEXT)
        avatar.create_oval(66, 44, 72, 50, fill=TEXT)
        avatar.create_arc(38, 64, 72, 86, start=200, extent=130, fill="", outline=TEXT, width=3)

        bubble = tk.Frame(
            narrator,
            bg=WHITE,
            bd=2,
            relief="solid",
            highlightbackground=LINE,
            highlightthickness=2,
            padx=16,
            pady=12,
        )
        bubble.pack(side="left", fill="x", expand=True)

        bubble_header = tk.Frame(bubble, bg=WHITE)
        bubble_header.pack(fill="x")
        self.node_title_label = tk.Label(
            bubble_header,
            text="Circe · Instrucciones del Nivel",
            bg=WHITE,
            fg=PURPLE,
            font=("Nunito", 11, "bold"),
        )
        self.node_title_label.pack(side="left")

        tk.Button(
            bubble_header,
            text="⏹ Detener voz",
            bg=SOFT,
            fg=MUTED,
            font=("Nunito", 9, "bold"),
            bd=0,
            padx=8,
            pady=2,
            command=lambda: self.orchestrator.tts.stop(),
        ).pack(side="right", padx=(6, 0))
        tk.Button(
            bubble_header,
            text="🔊 Escuchar instrucción",
            bg="#EDE8FF",
            fg=PURPLE_DARK,
            font=("Nunito", 10, "bold"),
            bd=0,
            padx=10,
            pady=2,
            command=lambda: self.orchestrator.speak_current_instructions(blocking=False),
        ).pack(side="right")

        self.narrator_text = tk.Label(
            bubble,
            text="",
            bg=WHITE,
            fg=TEXT,
            wraplength=560,
            justify="left",
            font=("Nunito", 15, "bold"),
            anchor="w",
        )
        self.narrator_text.pack(anchor="w", pady=(8, 4), fill="x")

        # Bloque de Respuesta del Estudiante (por Audio o por Texto)
        answer_wrap = tk.Frame(
            center,
            bg=WHITE,
            bd=2,
            relief="solid",
            highlightbackground=LINE,
            highlightthickness=2,
            padx=16,
            pady=14,
        )
        answer_wrap.pack(fill="both", expand=True, pady=12)

        ans_header = tk.Frame(answer_wrap, bg=WHITE)
        ans_header.pack(fill="x")
        tk.Label(
            ans_header,
            text="Tu respuesta (habla por micrófono o escribe tu decisión):",
            bg=WHITE,
            fg=MUTED,
            font=("Nunito", 11, "bold"),
        ).pack(side="left")
        self.voice_status_label = tk.Label(
            ans_header,
            text="🎙 Listo para grabar o escribir",
            bg=SOFT,
            fg=MUTED,
            font=("Nunito", 10, "bold"),
            padx=10,
            pady=2,
        )
        self.voice_status_label.pack(side="right")

        # Medidor de nivel de voz en vivo durante la grabación
        self.voice_meter_frame = tk.Frame(answer_wrap, bg="#E8EDF3", height=8)
        self.voice_meter_frame.pack(fill="x", pady=(6, 4))
        self.voice_meter_frame.pack_propagate(False)
        self.voice_meter_bar = tk.Frame(self.voice_meter_frame, bg=PURPLE, height=8, width=0)
        self.voice_meter_bar.pack(side="left", fill="y")

        self.answer_box = tk.Text(
            answer_wrap,
            height=4,
            wrap="word",
            font=("Nunito", 14),
            bg="#FAFBFD",
            fg=TEXT,
            insertbackground=TEXT,
            bd=1,
            relief="solid",
            padx=10,
            pady=8,
        )
        self.answer_box.pack(fill="both", expand=True, pady=6)

        button_row = tk.Frame(answer_wrap, bg=WHITE)
        button_row.pack(fill="x", pady=(4, 0))

        self.record_button = tk.Button(
            button_row,
            text="🎙 Hablar / Grabar Audio",
            bg=PURPLE,
            fg=WHITE,
            activebackground=PURPLE_DARK,
            activeforeground=WHITE,
            font=("Nunito", 11, "bold"),
            bd=0,
            padx=14,
            pady=8,
            command=self.toggle_voice_recording,
        )
        self.record_button.pack(side="left")

        tk.Button(
            button_row,
            text="⌨ Escribir / Limpiar",
            bg=WHITE,
            fg=TEXT,
            activebackground=SOFT,
            font=("Nunito", 11, "bold"),
            bd=1,
            relief="solid",
            padx=12,
            pady=6,
            command=self.focus_text_input,
        ).pack(side="left", padx=8)

        tk.Button(
            button_row,
            text="✨ Ejemplo de respuesta",
            bg=SOFT,
            fg=PURPLE_DARK,
            activebackground=LINE,
            font=("Nunito", 10, "bold"),
            bd=0,
            padx=10,
            pady=7,
            command=self.fill_sample_answer,
        ).pack(side="left", padx=4)

        self.evaluate_button = tk.Button(
            button_row,
            text="Evaluar decisión ➔",
            bg=GREEN,
            fg="#10202B",
            activebackground=GREEN_DARK,
            activeforeground="#10202B",
            font=("Nunito", 12, "bold"),
            bd=0,
            padx=18,
            pady=8,
            command=self.evaluate_current_turn,
        )
        self.evaluate_button.pack(side="right")

        # Columna derecha: Estado dinámico del incidente y Pista con voz
        right_meta = tk.Frame(body, bg=BG, width=270)
        right_meta.pack(side="left", fill="y", padx=(16, 4))
        right_meta.pack_propagate(False)

        stats = tk.Frame(
            right_meta,
            bg=WHITE,
            bd=2,
            relief="solid",
            highlightbackground=LINE,
            highlightthickness=2,
            padx=16,
            pady=14,
        )
        stats.pack(fill="x")
        tk.Label(stats, text="Estado del incidente", bg=WHITE, fg=TEXT, font=("Nunito", 14, "bold")).pack(anchor="w")

        self.metric_widgets: dict[str, tuple[tk.Label, tk.Frame]] = {}
        for key, label, color in [
            ("containment", "Contención", YELLOW),
            ("data_safety", "Protección de Datos", GREEN),
            ("service_health", "Continuidad Servicio", BLUE),
        ]:
            box = tk.Frame(stats, bg=WHITE)
            box.pack(fill="x", pady=8)
            header = tk.Frame(box, bg=WHITE)
            header.pack(fill="x")
            tk.Label(header, text=label, bg=WHITE, fg=TEXT, font=("Nunito", 10, "bold")).pack(side="left")
            val_lbl = tk.Label(header, text="50%", bg=WHITE, fg=TEXT, font=("Nunito", 10, "bold"))
            val_lbl.pack(side="right")
            bar = tk.Frame(box, bg="#E8EDF3", height=10, width=220)
            bar.pack(fill="x", pady=4)
            bar.pack_propagate(False)
            inner = tk.Frame(bar, bg=color, height=10, width=110)
            inner.pack(side="left", fill="y")
            self.metric_widgets[key] = (val_lbl, inner)

        hint = tk.Frame(
            right_meta,
            bg="#EAF4FF",
            bd=2,
            relief="solid",
            highlightbackground="#C9E2FF",
            highlightthickness=2,
            padx=14,
            pady=12,
        )
        hint.pack(fill="x", pady=14)
        tk.Label(hint, text="💡 Pista Táctica (Texto y Voz)", bg="#EAF4FF", fg="#1D5FBF", font=("Nunito", 12, "bold")).pack(
            anchor="w"
        )
        self.hint_text = tk.Label(
            hint,
            text="Haz clic en 'Escuchar pista' si necesitas orientación sobre esta etapa.",
            bg="#EAF4FF",
            fg="#3A4A5C",
            wraplength=230,
            justify="left",
            font=("Nunito", 10, "bold"),
            pady=8,
        )
        self.hint_text.pack(anchor="w")
        tk.Button(
            hint,
            text="🔊 Ver y escuchar pista",
            bg=WHITE,
            fg="#1D5FBF",
            activebackground=SOFT,
            font=("Nunito", 10, "bold"),
            bd=1,
            relief="solid",
            padx=10,
            pady=4,
            command=self.toggle_hint,
        ).pack(anchor="w", pady=4)

        # Barra inferior de Retroalimentación / Respuesta del Modelo (Texto + Audio)
        self.feedback_frame = tk.Frame(screen, bg=SOFT, height=118, highlightbackground=LINE, highlightthickness=2)
        self.feedback_frame.pack(fill="x", side="bottom")
        self.feedback_frame.pack_propagate(False)

        self.left_fb = tk.Frame(self.feedback_frame, bg=SOFT)
        self.left_fb.pack(side="left", fill="both", expand=True, padx=22, pady=12)

        fb_top = tk.Frame(self.left_fb, bg=SOFT)
        fb_top.pack(fill="x")
        self.feedback_title = tk.Label(
            fb_top,
            text="Esperando tu decisión por voz o texto...",
            bg=SOFT,
            fg=TEXT,
            font=("Nunito", 16, "bold"),
        )
        self.feedback_title.pack(side="left")

        self.replay_feedback_btn = tk.Button(
            fb_top,
            text="🔊 Escuchar evaluación",
            bg=WHITE,
            fg=PURPLE_DARK,
            font=("Nunito", 10, "bold"),
            bd=1,
            relief="solid",
            padx=10,
            pady=2,
            command=self.speak_last_feedback,
        )
        self.replay_feedback_btn.pack(side="left", padx=14)

        self.feedback_text = tk.Label(
            self.left_fb,
            text="Graba tu respuesta con el botón 'Hablar / Grabar Audio' o escríbela en el cuadro y pulsa 'Evaluar decisión'.",
            bg=SOFT,
            fg=MUTED,
            wraplength=860,
            justify="left",
            font=("Nunito", 11, "bold"),
            anchor="w",
        )
        self.feedback_text.pack(anchor="w", pady=4)

        self.next_button = tk.Button(
            self.feedback_frame,
            text="Siguiente nivel ➔",
            bg=YELLOW,
            fg="#3B2A00",
            activebackground=YELLOW_DARK,
            activeforeground="#3B2A00",
            bd=0,
            font=("Nunito", 13, "bold"),
            command=self.on_continue_clicked,
            width=18,
            height=2,
            state="disabled",
        )
        self.next_button.pack(side="right", padx=22, pady=20)

        return screen

    # =========================================================================
    # PANTALLA 3: RESULTADOS DINÁMICOS DE LOS 5 NIVELES
    # =========================================================================
    def build_results_screen(self, parent: tk.Widget) -> tk.Frame:
        screen = tk.Frame(parent, bg=BG)

        topbar = tk.Frame(screen, bg=WHITE, height=68, highlightbackground=LINE, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="circe", bg=WHITE, fg=PURPLE, font=("Nunito", 26, "bold"), padx=28, anchor="w").pack(
            side="left", fill="y"
        )
        self.results_header_label = tk.Label(
            topbar,
            text="Resultados del Nivel",
            bg=WHITE,
            fg=MUTED,
            font=("Nunito", 12, "bold"),
        )
        self.results_header_label.pack(side="right", padx=24, fill="y")

        main = tk.Frame(screen, bg=BG)
        main.pack(fill="both", expand=True, padx=48, pady=24)

        left = tk.Frame(main, bg=BG, width=410)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        canvas = tk.Canvas(left, width=160, height=160, bg=BG, highlightthickness=0)
        canvas.pack(pady=6)
        canvas.create_oval(20, 10, 140, 130, fill="#EAF6F0", outline="#A7E7C3", width=2)
        canvas.create_oval(35, 15, 125, 105, fill=PURPLE, outline=PURPLE_DARK, width=3)
        canvas.create_oval(50, 45, 66, 61, fill="white")
        canvas.create_oval(94, 45, 110, 61, fill="white")
        canvas.create_oval(55, 49, 62, 56, fill=TEXT)
        canvas.create_oval(99, 49, 106, 56, fill=TEXT)
        canvas.create_arc(55, 65, 105, 95, start=200, extent=140, fill="", outline=TEXT, width=3)

        self.results_title_label = tk.Label(
            left,
            text="¡Nivel completado!",
            bg=BG,
            fg=TEXT,
            font=("Nunito", 26, "bold"),
            justify="center",
        )
        self.results_title_label.pack(anchor="center")

        self.results_subtitle_label = tk.Label(
            left,
            text="",
            bg=BG,
            fg=MUTED,
            font=("Nunito", 13, "bold"),
            wraplength=360,
            justify="center",
        )
        self.results_subtitle_label.pack(anchor="center", pady=12)

        tiles = tk.Frame(left, bg=BG)
        tiles.pack(fill="x", pady=6)

        self.res_xp_val = self._create_result_tile(tiles, "XP total", "0 XP", "#B37A00", "#FFF1BE")
        self.res_score_val = self._create_result_tile(tiles, "Puntaje", "0/100", "#146B3A", "#DDF7E8")
        self.res_time_val = self._create_result_tile(tiles, "Tiempo", "00:00", "#1D5FBF", "#EAF4FF")
        self.res_lives_val = self._create_result_tile(tiles, "Vidas", "3 de 3", "#D93A40", "#FFE5E7")

        tk.Button(
            left,
            text="🔊 Escuchar resumen en voz de Circe",
            bg=PURPLE,
            fg=WHITE,
            activebackground=PURPLE_DARK,
            activeforeground=WHITE,
            bd=0,
            font=("Nunito", 12, "bold"),
            pady=10,
            command=self.speak_results_summary,
        ).pack(fill="x", pady=(14, 6))

        tk.Button(
            left,
            text="SIGUIENTE NIVEL DE CAMPAÑA ➔",
            bg=GREEN,
            fg="#10202B",
            activebackground=GREEN_DARK,
            activeforeground="#10202B",
            bd=0,
            font=("Nunito", 12, "bold"),
            pady=10,
            command=self.go_to_next_campaign_level,
        ).pack(fill="x", pady=6)

        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill="x", pady=4)
        tk.Button(
            btn_row,
            text="↻ Reintentar Nivel",
            bg=WHITE,
            fg=TEXT,
            bd=1,
            relief="solid",
            font=("Nunito", 11, "bold"),
            pady=8,
            command=self.reset_session_for_results,
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(
            btn_row,
            text="☰ Menú de 5 Niveles",
            bg=WHITE,
            fg=TEXT,
            bd=1,
            relief="solid",
            font=("Nunito", 11, "bold"),
            pady=8,
            command=self._return_to_start,
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(32, 0))
        tk.Label(
            right,
            text="Repaso de tus 5 decisiones (Voz y Texto)",
            bg=BG,
            fg=TEXT,
            font=("Nunito", 17, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.results_decisions_frame = tk.Frame(right, bg=BG)
        self.results_decisions_frame.pack(fill="both", expand=True)

        return screen

    def _create_result_tile(self, parent: tk.Widget, label: str, value: str, fg: str, bg: str) -> tk.Label:
        tile = tk.Frame(parent, bg=bg, highlightbackground=LINE, highlightthickness=1, padx=8, pady=8)
        tile.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(tile, text=label, bg=bg, fg=fg, font=("Nunito", 10, "bold")).pack(anchor="center")
        val_lbl = tk.Label(tile, text=value, bg=bg, fg=fg, font=("Nunito", 15, "bold"))
        val_lbl.pack(anchor="center", pady=4)
        return val_lbl

    # =========================================================================
    # LÓGICA DE NAVEGACIÓN, AUDIO (STT/TTS) Y EVALUACIÓN
    # =========================================================================
    def start_level(self, level_id: str) -> None:
        self.orchestrator.select_level(level_id)
        self.awaiting_next_node = False
        self.show_screen("sim")

    def _return_to_start(self) -> None:
        self.orchestrator.tts.stop()
        if self.orchestrator.stt.is_recording:
            self.orchestrator.stt.stop_stream_recording()
        self.screens["start"].destroy()
        self.screens["start"] = self.build_start_screen(self.container)
        self.show_screen("start")

    def show_screen(self, name: str) -> None:
        if name not in self.screens:
            return
        for frame in self.screens.values():
            frame.pack_forget()
        self.screens[name].pack(fill="both", expand=True)
        self.current_screen = name
        if name == "sim":
            self.refresh_scene(speak_instructions=True)
        elif name == "results":
            self.populate_results_screen()

    def _test_speaker_voice(self) -> None:
        self.orchestrator.speak_text(
            "Hola, soy Circe. El sistema de voz en español está listo para guiarte en los cinco niveles de ciberseguridad.",
            blocking=False,
        )

    def _toggle_auto_tts(self) -> None:
        enabled = not self.orchestrator.tts.enabled
        self.orchestrator.tts.enabled = enabled
        self.orchestrator.config.auto_speak_instructions = enabled
        self.orchestrator.config.auto_speak_feedback = enabled
        if not enabled:
            self.orchestrator.tts.stop()
            self.auto_tts_btn.config(text="🔇 Voz Auto: OFF", bg=SOFT, fg=MUTED)
        else:
            self.auto_tts_btn.config(text="🔊 Voz Auto: ON", bg="#EDE8FF", fg=PURPLE_DARK)

    def refresh_scene(self, speak_instructions: bool = True) -> None:
        scenario = self.orchestrator.engine.level_scenario
        node = self.orchestrator.get_active_node()
        ordered_nodes = self.orchestrator.get_ordered_nodes()
        total_nodes = len(ordered_nodes)

        self.scenario_pill.config(text=f"{scenario.title}")
        self.node_title_label.config(text=f"Circe · {node.title} (Texto y Audio)")
        self.narrator_text.config(text=node.prompt)
        self.hint_text.config(
            text="Haz clic en 'Ver y escuchar pista' si necesitas ayuda en este nivel."
        )

        # Actualizar barra de progreso superior
        progress_ratio = node.level_number / max(1, total_nodes)
        self.progress_bar_inner.config(width=int(360 * progress_ratio))
        self.progress_label.config(text=f"Decisión {node.level_number} de {total_nodes}")

        # Actualizar XP y Vidas
        self.xp_label.config(text=f"⚡ {self.orchestrator.session.xp} XP")
        self.lives_label.config(text=f"❤ {self.orchestrator.session.lives}")

        # Actualizar métricas del incidente
        for key in ("containment", "data_safety", "service_health"):
            val = getattr(self.orchestrator.session, key, 50)
            lbl, bar = self.metric_widgets[key]
            lbl.config(text=f"{val}%")
            bar.config(width=max(10, int(220 * val / 100)))

        # Reconstruir barra lateral de los 5 niveles/etapas
        for child in self.timeline_container.winfo_children():
            child.destroy()

        for idx, item_node in enumerate(ordered_nodes):
            past = self.orchestrator.session.node_results.get(item_node.id)
            is_active = item_node.id == node.id

            if past:
                verdict = past["content"].get("verdict", "partial")
                bg_color = GREEN if verdict == "correct" else YELLOW if verdict == "partial" else RED
                icon_txt = "✓" if verdict == "correct" else "◔" if verdict == "partial" else "✗"
                fg_color = TEXT
            elif is_active:
                bg_color = PURPLE
                icon_txt = "🎙"
                fg_color = PURPLE_DARK
            else:
                bg_color = "#E8EDF3"
                icon_txt = "🔒"
                fg_color = "#8A97A6"

            row = tk.Frame(self.timeline_container, bg=BG)
            row.pack(fill="x", pady=4)
            bubble = tk.Frame(row, bg=bg_color, width=38, height=38)
            bubble.pack_propagate(False)
            bubble.pack(side="left")
            tk.Label(
                bubble,
                text=icon_txt,
                bg=bg_color,
                fg=WHITE if is_active or (past and past["content"].get("verdict") == "wrong") else TEXT,
                font=("Nunito", 13, "bold"),
            ).pack(expand=True)
            tk.Label(
                row,
                text=item_node.title,
                bg=BG,
                fg=fg_color,
                font=("Nunito", 11, "bold"),
                wraplength=185,
                justify="left",
            ).pack(side="left", padx=10)

            if idx < total_nodes - 1:
                line = tk.Frame(self.timeline_container, bg=LINE, height=12, width=3)
                line.pack(anchor="w", padx=18)

        # Limpiar entrada si no estamos esperando continuar
        if not self.awaiting_next_node:
            self.answer_box.delete("1.0", "end")
            self._set_feedback_banner(
                bg_color=SOFT,
                border_color=LINE,
                title_text=f"Esperando tu respuesta para el {node.title}...",
                body_text="Puedes responder hablando con el botón '🎙 Hablar / Grabar Audio' o escribiendo en el cuadro de texto.",
                title_fg=TEXT,
                body_fg=MUTED,
            )
            self.next_button.config(state="disabled")
            self.evaluate_button.config(state="normal")

        if speak_instructions and self.orchestrator.config.auto_speak_instructions:
            self.orchestrator.speak_current_instructions(blocking=False)

    def _set_feedback_banner(
        self,
        bg_color: str,
        border_color: str,
        title_text: str,
        body_text: str,
        title_fg: str,
        body_fg: str,
    ) -> None:
        self.feedback_frame.config(bg=bg_color, highlightbackground=border_color)
        self.left_fb.config(bg=bg_color)
        self.feedback_title.master.config(bg=bg_color)
        self.feedback_title.config(text=title_text, bg=bg_color, fg=title_fg)
        self.feedback_text.config(text=body_text, bg=bg_color, fg=body_fg)

    def toggle_hint(self) -> None:
        node = self.orchestrator.get_active_node()
        self.hint_text.config(text=node.hint)
        self.orchestrator.speak_text(f"Pista para {node.title}: {node.hint}", blocking=False)

    def focus_text_input(self) -> None:
        self.input_mode = "text"
        self.answer_box.delete("1.0", "end")
        self.answer_box.focus_set()
        self.voice_status_label.config(text="⌨ Modo escritura activo", bg="#EDE8FF", fg=PURPLE_DARK)

    def fill_sample_answer(self) -> None:
        node = self.orchestrator.get_active_node()
        if node.correct_actions:
            sample = f"Mi decisión es {node.correct_actions[0]} para contener y asegurar la evidencia."
            self.answer_box.delete("1.0", "end")
            self.answer_box.insert("1.0", sample)
            self.input_mode = "text"
            self.voice_status_label.config(text="✨ Respuesta de ejemplo cargada", bg="#DDF7E8", fg="#146B3A")

    # =========================================================================
    # GRABACIÓN INTERACTIVA DE VOZ (STT) EN HILO SECUNDARIO
    # =========================================================================
    def toggle_voice_recording(self) -> None:
        if not self.orchestrator.stt.is_recording:
            self._start_voice_capture()
        else:
            self._stop_and_transcribe_voice()

    def _start_voice_capture(self) -> None:
        self.orchestrator.tts.stop()
        try:
            self.orchestrator.stt.start_stream_recording(on_level=self._on_mic_level_update)
            self.input_mode = "voice"
            self.record_button.config(
                text="⏹ Detener y Transcribir",
                bg=RED,
                activebackground=RED_DARK,
            )
            self.voice_status_label.config(
                text="🔴 Grabando tu voz... habla ahora y pulsa 'Detener'",
                bg=RED_LIGHT,
                fg=RED_DARK,
            )
        except Exception as exc:
            self.voice_status_label.config(
                text=f"⚠ Micrófono no disponible ({exc}). Usa escritura o respuesta de ejemplo.",
                bg="#FFF3CF",
                fg="#7A4E00",
            )

    def _on_mic_level_update(self, level: float) -> None:
        width = int(520 * max(0.02, min(1.0, level)))
        try:
            self.after(0, lambda: self.voice_meter_bar.config(width=width))
        except Exception:
            pass

    def _stop_and_transcribe_voice(self) -> None:
        self.record_button.config(
            text="⏳ Transcribiendo voz...",
            bg=YELLOW,
            fg=TEXT,
            state="disabled",
        )
        self.voice_status_label.config(
            text="⏳ Procesando audio con faster-whisper...",
            bg="#FFF3CF",
            fg="#7A4E00",
        )
        self.voice_meter_bar.config(width=0)

        def _worker() -> None:
            try:
                wav_path = self.orchestrator.stt.stop_stream_recording()
                transcript = asyncio.run(self.orchestrator.stt.transcribe(audio_path=wav_path))
                self.after(0, lambda: self._on_transcription_complete(transcript, None))
            except Exception as exc:
                self.after(0, lambda: self._on_transcription_complete("", exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_transcription_complete(self, transcript: str, error: Exception | None) -> None:
        self.record_button.config(
            text="🎙 Hablar / Grabar Audio",
            bg=PURPLE,
            fg=WHITE,
            state="normal",
        )
        if error is not None:
            self.voice_status_label.config(
                text="⚠ STT sin modelo en caché offline; puedes dictar o editar en el cuadro",
                bg="#FFF3CF",
                fg="#7A4E00",
            )
            return

        if transcript:
            self.answer_box.delete("1.0", "end")
            self.answer_box.insert("1.0", transcript)
            self.voice_status_label.config(
                text="✓ Audio transcrito con éxito (listo para evaluar)",
                bg="#DDF7E8",
                fg="#146B3A",
            )
        else:
            self.voice_status_label.config(
                text="No se detectó voz clara. Intenta hablar más cerca del micrófono.",
                bg="#FFF3CF",
                fg="#7A4E00",
            )

    # =========================================================================
    # EVALUACIÓN CON MODELO IA Y RETROALIMENTACIÓN EN TEXTO + AUDIO
    # =========================================================================
    def evaluate_current_turn(self) -> None:
        if self.orchestrator.stt.is_recording:
            self.orchestrator.stt.stop_stream_recording()
            self.record_button.config(text="🎙 Hablar / Grabar Audio", bg=PURPLE, fg=WHITE, state="normal")

        answer = self.answer_box.get("1.0", "end").strip()
        if not answer:
            self._set_feedback_banner(
                bg_color="#FFF3CF",
                border_color="#FFD968",
                title_text="Falta tu respuesta por voz o texto",
                body_text="Por favor graba tu decisión con el micrófono o escríbela antes de evaluar.",
                title_fg="#7A4E00",
                body_fg="#6B4A12",
            )
            self.orchestrator.speak_text("Por favor, graba o escribe tu decisión antes de evaluar.", blocking=False)
            return

        self.evaluate_button.config(state="disabled", text="Evaluando...")

        def _eval_worker() -> None:
            try:
                result = asyncio.run(
                    self.orchestrator.process_student_turn(
                        student_text=answer,
                        auto_advance=False,
                        speak_response=True,
                        input_mode=self.input_mode,
                    )
                )
                self.after(0, lambda: self._on_evaluation_ready(result, None))
            except Exception as exc:
                self.after(0, lambda: self._on_evaluation_ready(None, exc))

        threading.Thread(target=_eval_worker, daemon=True).start()

    def _on_evaluation_ready(self, result: dict[str, Any] | None, error: Exception | None) -> None:
        self.evaluate_button.config(text="Evaluar decisión ➔")
        if error is not None or result is None:
            self.evaluate_button.config(state="normal")
            self._set_feedback_banner(
                bg_color=RED_LIGHT,
                border_color=RED,
                title_text="Error al evaluar",
                body_text=str(error),
                title_fg=RED_DARK,
                body_fg=RED_DARK,
            )
            return

        evaluation = result["evaluation"]
        verdict = evaluation.get("verdict", "partial")
        xp_gained = evaluation.get("xp_gained", 10)
        reason = evaluation.get("reason", "")
        recommended = evaluation.get("recommended_action", "")
        engine_used = evaluation.get("engine_used", "IA Local")
        self.last_spoken_feedback = result.get("spoken_feedback", "")

        self.engine_badge.config(text=f"Evaluado por: {engine_used}")

        if verdict == "correct":
            bg_c, bd_c, tfg, bfg = "#DDF7E8", GREEN, "#146B3A", "#10202B"
            title = f"✓ ¡Decisión Correcta! · +{xp_gained} XP"
        elif verdict == "partial":
            bg_c, bd_c, tfg, bfg = "#FFF3CF", "#FFD968", "#7A4E00", "#6B4A12"
            title = f"◔ Respuesta Parcial · +{xp_gained} XP"
        else:
            bg_c, bd_c, tfg, bfg = RED_LIGHT, RED, RED_DARK, RED_DARK
            title = "✗ Decisión Riesgosa o Incorrecta · -1 Vida"

        self.awaiting_next_node = True
        self.refresh_scene(speak_instructions=False)
        self._set_feedback_banner(
            bg_color=bg_c,
            border_color=bd_c,
            title_text=title,
            body_text=f"{reason}  Recomendación: {recommended}",
            title_fg=tfg,
            body_fg=bfg,
        )

        active_node = self.orchestrator.get_active_node()
        if active_node.next_node:
            self.next_button.config(text=f"Ir al Nivel {active_node.level_number + 1} ➔", state="normal")
        else:
            self.next_button.config(text="Ver Resultados ➔", state="normal")

    def speak_last_feedback(self) -> None:
        if self.last_spoken_feedback:
            self.orchestrator.speak_text(self.last_spoken_feedback, blocking=False)

    def on_continue_clicked(self) -> None:
        self.awaiting_next_node = False
        has_more = self.orchestrator.advance_to_next_node()
        if has_more:
            self.refresh_scene(speak_instructions=True)
        else:
            lvl_id = self.orchestrator.session.level_id
            self.completed_levels[lvl_id] = self.orchestrator.session.score
            self.show_screen("results")

    # =========================================================================
    # PANTALLA DE RESULTADOS Y AVANCE ENTRE LOS 5 NIVELES DE CAMPAÑA
    # =========================================================================
    def populate_results_screen(self) -> None:
        session = self.orchestrator.session
        scenario = self.orchestrator.engine.level_scenario

        self.results_header_label.config(text=scenario.title)
        self.res_xp_val.config(text=f"{session.xp} XP")
        self.res_score_val.config(text=f"{session.score:.0f}/100")
        self.res_time_val.config(text=session.elapsed_formatted())
        self.res_lives_val.config(text=f"{session.lives} de {session.max_lives}")

        if session.score >= 80:
            self.results_title_label.config(text="¡Incidente Contenido con Éxito!")
            summary_msg = (
                f"Completaste los 5 niveles de '{scenario.title}' con un desempeño sobresaliente "
                f"de {session.score:.0f} puntos y {session.xp} XP."
            )
        elif session.score >= 50:
            self.results_title_label.config(text="¡Incidente Controlado Parcialmente!")
            summary_msg = (
                f"Superaste los 5 niveles de '{scenario.title}' con {session.score:.0f} puntos. "
                "Revisa las recomendaciones para fortalecer la contención y preservación forense."
            )
        else:
            self.results_title_label.config(text="Incidente con Impacto Crítico")
            summary_msg = (
                f"Finalizaste '{scenario.title}' con {session.score:.0f} puntos. "
                "Te recomendamos reintentar priorizando aislar la amenaza antes de restaurar."
            )
        self.results_subtitle_label.config(text=summary_msg)

        for child in self.results_decisions_frame.winfo_children():
            child.destroy()

        for node in self.orchestrator.get_ordered_nodes():
            rec = session.node_results.get(node.id)
            verdict = rec["content"].get("verdict", "partial") if rec else "partial"
            xp = rec["content"].get("xp_gained", 0) if rec else 0
            reason = rec["content"].get("reason", "Sin respuesta registrada.") if rec else "Sin evaluar."
            user_ans = rec.get("student_text", "") if rec else ""
            mode_icon = "🎙 Voz" if (rec and rec.get("input_mode") == "voice") else "⌨ Texto"

            bg_b = GREEN if verdict == "correct" else YELLOW if verdict == "partial" else RED
            icon_b = "✓" if verdict == "correct" else "◔" if verdict == "partial" else "✗"

            row = tk.Frame(
                self.results_decisions_frame,
                bg=WHITE,
                bd=1,
                relief="solid",
                highlightbackground=LINE,
                highlightthickness=1,
                padx=12,
                pady=8,
            )
            row.pack(fill="x", pady=4)

            bubble = tk.Frame(row, bg=bg_b, width=34, height=34)
            bubble.pack_propagate(False)
            bubble.pack(side="left")
            tk.Label(
                bubble,
                text=icon_b,
                bg=bg_b,
                fg=WHITE if verdict == "wrong" else TEXT,
                font=("Nunito", 13, "bold"),
            ).pack(expand=True)

            body = tk.Frame(row, bg=WHITE)
            body.pack(side="left", fill="x", expand=True, padx=12)
            tk.Label(
                body,
                text=f"{node.title}  ({mode_icon}: \"{user_ans[:65]}\")",
                bg=WHITE,
                fg=TEXT,
                font=("Nunito", 11, "bold"),
            ).pack(anchor="w")
            tk.Label(
                body,
                text=reason,
                bg=WHITE,
                fg=MUTED,
                font=("Nunito", 10, "bold"),
                wraplength=560,
                justify="left",
            ).pack(anchor="w")

            tk.Label(
                row,
                text=f"+{xp} XP",
                bg=WHITE,
                fg="#146B3A" if verdict == "correct" else "#B37A00",
                font=("Nunito", 11, "bold"),
            ).pack(side="right")

        if self.orchestrator.config.auto_speak_feedback:
            self.speak_results_summary()

    def speak_results_summary(self) -> None:
        session = self.orchestrator.session
        scenario = self.orchestrator.engine.level_scenario
        text = (
            f"Has completado los cinco niveles de {scenario.title}. "
            f"Obtuviste {session.score:.0f} puntos sobre cien, {session.xp} puntos de experiencia, "
            f"y conservaste {session.lives} vidas."
        )
        self.orchestrator.speak_text(text, blocking=False)

    def reset_session_for_results(self) -> None:
        current_level_id = self.orchestrator.session.level_id
        self.start_level(current_level_id)

    def go_to_next_campaign_level(self) -> None:
        levels = list_levels()
        current_id = self.orchestrator.session.level_id
        ids = [lvl.id for lvl in levels]
        try:
            next_idx = (ids.index(current_id) + 1) % len(ids)
        except ValueError:
            next_idx = 0
        self.start_level(ids[next_idx])


def main() -> None:
    app = CIRCEGuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
