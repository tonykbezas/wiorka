import customtkinter as ctk
import time
import tkinter as tk
from typing import Optional
from simulator import ActivitySimulator, SimulatorConfig

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoPresenceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoPresence - Simulador de Actividad AFK")
        self.geometry("840x740")
        self.minsize(780, 680)

        self.simulator: Optional[ActivitySimulator] = None
        self.timer_seconds = 0
        self.total_duration_seconds = 0

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- HEADER / TITULO Y ESTADO ---
        header_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e293b")
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame, 
            text="⚡ AutoPresence", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f8fafc"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 2), sticky="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Simulación hiper-realista humana | Modo Anti-Capturas, Alt+Tab y pausas de lectura",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        self.status_badge = ctk.CTkLabel(
            header_frame,
            text=" ESTADO: INACTIVO ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155",
            text_color="#e2e8f0",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.status_badge.grid(row=0, column=1, rowspan=2, padx=20, pady=15, sticky="e")

        # --- PANEL CENTRAL ---
        middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        middle_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=1)

        # Tarjeta 1: Temporizador
        timer_card = ctk.CTkFrame(middle_frame, corner_radius=12, fg_color="#1e293b")
        timer_card.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")

        timer_title = ctk.CTkLabel(
            timer_card,
            text="⏳ Tiempo de Reemplazo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#38bdf8"
        )
        timer_title.pack(anchor="w", padx=15, pady=(12, 5))

        preset_frame = ctk.CTkFrame(timer_card, fg_color="transparent")
        preset_frame.pack(fill="x", padx=15, pady=5)

        self.time_preset_var = ctk.StringVar(value="custom")

        presets = [("15m", "15"), ("30m", "30"), ("1h", "60"), ("2h", "120"), ("Indefinido", "0")]
        for text, val in presets:
            btn = ctk.CTkRadioButton(
                preset_frame,
                text=text,
                value=val,
                variable=self.time_preset_var,
                command=self._on_preset_selected,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(side="left", expand=True, padx=2)

        self.slider_label = ctk.CTkLabel(
            timer_card,
            text="Duración personalizada: 30 minutos",
            font=ctk.CTkFont(size=13),
            text_color="#cbd5e1"
        )
        self.slider_label.pack(anchor="w", padx=15, pady=(10, 2))

        self.time_slider = ctk.CTkSlider(
            timer_card,
            from_=5,
            to=240,
            number_of_steps=47,
            command=self._on_slider_change
        )
        self.time_slider.set(30)
        self.time_slider.pack(fill="x", padx=15, pady=(0, 10))

        self.clock_label = ctk.CTkLabel(
            timer_card,
            text="00:30:00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#38bdf8"
        )
        self.clock_label.pack(pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(timer_card, height=8, corner_radius=4)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=15, pady=(5, 10))

        self.sw_stealth_gui = ctk.CTkCheckBox(
            timer_card,
            text="🕵️ Ocultar ventana al iniciar (Anti-Capturas)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#f59e0b"
        )
        self.sw_stealth_gui.pack(anchor="w", padx=15, pady=(0, 12))

        # Tarjeta 2: Acciones
        options_card = ctk.CTkFrame(middle_frame, corner_radius=12, fg_color="#1e293b")
        options_card.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")

        opt_title = ctk.CTkLabel(
            options_card,
            text="⚙️ Acciones y Modo Humano",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#38bdf8"
        )
        opt_title.pack(anchor="w", padx=15, pady=(12, 10))

        self.sw_hyper = ctk.CTkSwitch(options_card, text="🧠 Modo Hiper-Realismo (Ráfagas + Pausas)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#10b981")
        self.sw_hyper.select()
        self.sw_hyper.pack(anchor="w", padx=15, pady=4)

        self.sw_mouse = ctk.CTkSwitch(options_card, text="Mover Mouse (Curvas Bézier)", font=ctk.CTkFont(size=12))
        self.sw_mouse.select()
        self.sw_mouse.pack(anchor="w", padx=15, pady=4)

        self.sw_scroll = ctk.CTkSwitch(options_card, text="Scroll de Lectura (Páginas)", font=ctk.CTkFont(size=12))
        self.sw_scroll.select()
        self.sw_scroll.pack(anchor="w", padx=15, pady=4)

        self.sw_tabs = ctk.CTkSwitch(options_card, text="Cambiar Ventanas / Pestañas", font=ctk.CTkFont(size=12))
        self.sw_tabs.select()
        self.sw_tabs.pack(anchor="w", padx=15, pady=4)

        tab_mode_frame = ctk.CTkFrame(options_card, fg_color="transparent")
        tab_mode_frame.pack(fill="x", padx=15, pady=(2, 6))
        
        tab_mode_lbl = ctk.CTkLabel(tab_mode_frame, text="Atajo cambio:", font=ctk.CTkFont(size=11), text_color="#94a3b8")
        tab_mode_lbl.pack(side="left", padx=(0, 5))

        self.tab_mode_dropdown = ctk.CTkOptionMenu(
            tab_mode_frame,
            values=["Alt + Tab (Ventanas Windows)", "Ctrl + Tab (Pestañas Navegador)", "Ambos (Aleatorio)"],
            font=ctk.CTkFont(size=11),
            height=24
        )
        self.tab_mode_dropdown.set("Alt + Tab (Ventanas Windows)")
        self.tab_mode_dropdown.pack(side="left", fill="x", expand=True)

        self.sw_typing = ctk.CTkSwitch(options_card, text="Simular Tecleo de Teclado", font=ctk.CTkFont(size=12))
        self.sw_typing.select()
        self.sw_typing.pack(anchor="w", padx=15, pady=4)

        self.sw_click = ctk.CTkSwitch(options_card, text="Clics de Mouse Seguros", font=ctk.CTkFont(size=12))
        self.sw_click.deselect()
        self.sw_click.pack(anchor="w", padx=15, pady=4)

        mode_frame = ctk.CTkFrame(options_card, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=(4, 10))

        mode_lbl = ctk.CTkLabel(mode_frame, text="Modo tecleo:", font=ctk.CTkFont(size=11), text_color="#94a3b8")
        mode_lbl.pack(side="left", padx=(0, 5))

        self.typing_mode_dropdown = ctk.CTkOptionMenu(
            mode_frame,
            values=["Seguro (Shift / Flechas)", "Notas simuladas"],
            font=ctk.CTkFont(size=11),
            height=24
        )
        self.typing_mode_dropdown.set("Seguro (Shift / Flechas)")
        self.typing_mode_dropdown.pack(side="left", fill="x", expand=True)

        # --- PANEL INFERIOR ---
        bottom_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e293b")
        bottom_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")

        log_title = ctk.CTkLabel(
            log_header,
            text="📋 Consola de Actividad en Vivo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cbd5e1"
        )
        log_title.pack(side="left")

        clear_btn = ctk.CTkButton(
            log_header,
            text="Limpiar Log",
            font=ctk.CTkFont(size=11),
            width=80,
            height=24,
            fg_color="#334155",
            hover_color="#475569",
            command=self._clear_log
        )
        clear_btn.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(
            bottom_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0f172a",
            text_color="#38bdf8",
            corner_radius=8
        )
        self.log_textbox.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        safety_label = ctk.CTkLabel(
            bottom_frame,
            text="🛡️ PARADA DE EMERGENCIA: Presiona 'ESC' para detener y reaparecer la ventana si está oculta.",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#f59e0b"
        )
        safety_label.grid(row=2, column=0, padx=15, pady=(5, 5))

        control_btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        control_btn_frame.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="ew")
        control_btn_frame.grid_columnconfigure(0, weight=1)
        control_btn_frame.grid_columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(
            control_btn_frame,
            text="▶ INICIAR SIMULACIÓN",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.start_simulation
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.stop_btn = ctk.CTkButton(
            control_btn_frame,
            text="⏹ DETENER (ESC)",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42,
            fg_color="#ef4444",
            hover_color="#dc2626",
            state="disabled",
            command=self.stop_simulation
        )
        self.stop_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _on_slider_change(self, value):
        mins = int(value)
        self.slider_label.configure(text=f"Duración personalizada: {mins} minutos")
        self._update_clock_display(mins * 60)

    def _on_preset_selected(self):
        val = int(self.time_preset_var.get())
        if val > 0:
            self.time_slider.set(val)
            self.slider_label.configure(text=f"Duración personalizada: {val} minutos")
            self._update_clock_display(val * 60)
        else:
            self.slider_label.configure(text="Duración: Indefinida (Hasta detener)")
            self.clock_label.configure(text="∞ INDEFINIDO")

    def _update_clock_display(self, total_seconds: int):
        if total_seconds <= 0:
            self.clock_label.configure(text="∞ INDEFINIDO")
            return
        
        hrs = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        if hrs > 0:
            self.clock_label.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
        else:
            self.clock_label.configure(text=f"{mins:02d}:{secs:02d}")

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        self.after(0, self._append_log, formatted)

    def _append_log(self, text: str):
        self.log_textbox.insert("end", text)
        self.log_textbox.see("end")

    def _clear_log(self):
        self.log_textbox.delete("1.0", "end")

    def _update_status(self, status: str):
        def apply():
            if status == "running":
                self.status_badge.configure(
                    text=" ● EN EJECUCIÓN ",
                    fg_color="#065f46",
                    text_color="#34d399"
                )
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
            else:
                self.status_badge.configure(
                    text=" ESTADO: INACTIVO ",
                    fg_color="#334155",
                    text_color="#e2e8f0"
                )
                self.start_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled")
                self.progress_bar.set(0.0)
                self.deiconify()

        self.after(0, apply)

    def _update_time(self, remaining_seconds: int):
        def apply():
            self._update_clock_display(remaining_seconds)
            if self.total_duration_seconds > 0:
                progress = 1.0 - (remaining_seconds / self.total_duration_seconds)
                self.progress_bar.set(max(0.0, min(1.0, progress)))

        self.after(0, apply)

    def start_simulation(self):
        preset_val = int(self.time_preset_var.get())
        if preset_val > 0:
            duration_secs = preset_val * 60
        else:
            duration_secs = int(self.time_slider.get()) * 60

        if self.time_preset_var.get() == "0":
            duration_secs = 0

        self.total_duration_seconds = duration_secs

        raw_tab = self.tab_mode_dropdown.get()
        if "Alt + Tab" in raw_tab:
            t_mode = "alt_tab"
        elif "Ctrl + Tab" in raw_tab:
            t_mode = "ctrl_tab"
        else:
            t_mode = "both"

        typing_m = "safe" if "Seguro" in self.typing_mode_dropdown.get() else "text"

        config = SimulatorConfig(
            duration_seconds=duration_secs,
            enable_hyper_realism=bool(self.sw_hyper.get()),
            enable_mouse_move=bool(self.sw_mouse.get()),
            enable_scroll=bool(self.sw_scroll.get()),
            enable_tab_switch=bool(self.sw_tabs.get()),
            enable_typing=bool(self.sw_typing.get()),
            enable_clicks=bool(self.sw_click.get()),
            tab_mode=t_mode,
            typing_mode=typing_m
        )

        self.simulator = ActivitySimulator(
            config=config,
            log_callback=self.log,
            time_callback=self._update_time,
            status_callback=self._update_status
        )

        self.simulator.start()

        if self.sw_stealth_gui.get():
            self.after(2000, self.withdraw)

    def stop_simulation(self):
        if self.simulator:
            self.simulator.stop(reason="Detenido manualmente desde la aplicación")
        self.deiconify()
