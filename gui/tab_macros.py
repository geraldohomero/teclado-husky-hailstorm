"""
Macro Manager & Sequence Editor Tab for Husky Hailstorm.
Provides real-time keystroke recording, manual event insertion (Down/Up/Delay),
playback rules (Once, Loop while pressed, Toggle loop, N times), and persistence.
"""

import time
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional
from core.profiles import Profile, Macro, MacroItem
from core.keycodes import HID_KEYCODES


class TabMacros(ctk.CTkFrame):
    """Macro manager and editor tab."""
    def __init__(
        self,
        parent,
        profile: Profile,
        on_change_callback: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.profile = profile
        self.on_change = on_change_callback

        self.selected_macro_index: Optional[int] = None
        self.is_recording: bool = False
        self.record_start_time: float = 0.0
        self.last_event_time: float = 0.0

        self._ensure_sample_macro()
        self._build_ui()

    def _ensure_sample_macro(self):
        """Adds a starter macro if none exist."""
        if not self.profile.macros:
            sample = Macro("macro_1", "Combo WASD", repeat_mode=1, repeat_count=1)
            sample.events.append(MacroItem("down", 26, "W", 50))
            sample.events.append(MacroItem("up", 26, "W", 30))
            sample.events.append(MacroItem("down", 4, "A", 50))
            sample.events.append(MacroItem("up", 4, "A", 30))
            self.profile.macros.append(sample)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Macro List
        left_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        ctk.CTkLabel(
            left_card,
            text="⚡ Lista de Macros",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 8))

        # Action Buttons
        btn_row = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=5)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row,
            text="➕ Nova Macro",
            fg_color="#0066FF",
            hover_color="#0052CC",
            height=32,
            command=self.create_macro
        ).grid(row=0, column=0, padx=3, sticky="ew")

        ctk.CTkButton(
            btn_row,
            text="🗑️ Excluir",
            fg_color="#881337",
            hover_color="#9F1239",
            height=32,
            command=self.delete_selected_macro
        ).grid(row=0, column=1, padx=3, sticky="ew")

        # Scrollable list of macros
        self.macro_list_frame = ctk.CTkScrollableFrame(left_card, fg_color="#121319")
        self.macro_list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Right Column: Macro Editor
        right_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        right_card.grid_columnconfigure(0, weight=1)

        # Macro Name and Mode header
        header = ctk.CTkFrame(right_card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 8))

        ctk.CTkLabel(header, text="Nome da Macro:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        self.txt_macro_name = ctk.CTkEntry(header, width=180)
        self.txt_macro_name.pack(side="left", padx=(0, 15))
        self.txt_macro_name.bind("<KeyRelease>", self._on_name_edited)

        # Playback Mode
        ctk.CTkLabel(header, text="Modo de Repetição:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        self.combo_repeat = ctk.CTkComboBox(
            header,
            values=["Executar Uma Vez", "Enquanto Pressionada", "Alternar Loop", "Repetir N Vezes"],
            command=self._on_repeat_mode_changed,
            width=160
        )
        self.combo_repeat.pack(side="left")

        # Toolbar: Record and Insert events
        toolbar = ctk.CTkFrame(right_card, fg_color="#121319", corner_radius=8)
        toolbar.pack(fill="x", padx=15, pady=8)

        self.btn_record = ctk.CTkButton(
            toolbar,
            text="⏺️ Gravar Teclas",
            fg_color="#FF0033",
            hover_color="#D6002A",
            height=34,
            width=130,
            command=self.toggle_recording
        )
        self.btn_record.pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            toolbar,
            text="⏱️ +Delay",
            width=80,
            height=34,
            fg_color="#262936",
            hover_color="#363A4D",
            command=self.insert_delay
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            toolbar,
            text="⬆️ Mover Cima",
            width=85,
            height=34,
            fg_color="#262936",
            hover_color="#363A4D",
            command=self.move_event_up
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            toolbar,
            text="⬇️ Mover Baixo",
            width=85,
            height=34,
            fg_color="#262936",
            hover_color="#363A4D",
            command=self.move_event_down
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            toolbar,
            text="❌ Remover",
            width=80,
            height=34,
            fg_color="#3E202A",
            hover_color="#5E202A",
            command=self.delete_selected_event
        ).pack(side="left", padx=4)

        # Event Sequence Table
        self.events_box = ctk.CTkScrollableFrame(right_card, fg_color="#121319")
        self.events_box.pack(fill="both", expand=True, padx=15, pady=10)

        self.selected_event_index: Optional[int] = None

        self.refresh_macro_sidebar()
        if self.profile.macros:
            self.select_macro(0)

    def refresh_macro_sidebar(self):
        """Redraws macro items in the sidebar."""
        for w in self.macro_list_frame.winfo_children():
            w.destroy()

        for idx, m in enumerate(self.profile.macros):
            is_active = (idx == self.selected_macro_index)
            btn = ctk.CTkButton(
                self.macro_list_frame,
                text=f"⚡ {m.name} ({len(m.events)} eventos)",
                fg_color="#2B2E3A" if is_active else "transparent",
                hover_color="#383C4D",
                anchor="w",
                height=34,
                command=lambda i=idx: self.select_macro(i)
            )
            btn.pack(fill="x", padx=4, pady=2)

    def select_macro(self, index: int):
        if 0 <= index < len(self.profile.macros):
            self.selected_macro_index = index
            macro = self.profile.macros[index]
            self.txt_macro_name.delete(0, "end")
            self.txt_macro_name.insert(0, macro.name)

            repeat_names = ["Executar Uma Vez", "Enquanto Pressionada", "Alternar Loop", "Repetir N Vezes"]
            mode_idx = max(0, min(3, macro.repeat_mode - 1))
            self.combo_repeat.set(repeat_names[mode_idx])

            self.refresh_macro_sidebar()
            self.render_events()

    def render_events(self):
        """Renders event rows in the event sequence box."""
        for w in self.events_box.winfo_children():
            w.destroy()

        if self.selected_macro_index is None:
            return

        macro = self.profile.macros[self.selected_macro_index]
        if not macro.events:
            ctk.CTkLabel(
                self.events_box,
                text="Macro vazia. Clique em 'Gravar Teclas' ou insira eventos manualmente.",
                text_color="#8E94A8"
            ).pack(pady=30)
            return

        for idx, ev in enumerate(macro.events):
            row_frame = ctk.CTkFrame(
                self.events_box,
                fg_color="#20222D" if idx == self.selected_event_index else "transparent",
                corner_radius=6,
                height=30
            )
            row_frame.pack(fill="x", padx=4, pady=2)
            row_frame.pack_propagate(False)

            # Icon & Type
            if ev.event_type == "down":
                icon = "⬇️"
                desc = f"Pressionar [{ev.key_name}]"
                color = "#00FF66"
            elif ev.event_type == "up":
                icon = "⬆️"
                desc = f"Soltar [{ev.key_name}]"
                color = "#FF9933"
            else:
                icon = "⏱️"
                desc = f"Aguardar {ev.delay_ms} ms"
                color = "#00F0FF"

            ctk.CTkLabel(
                row_frame,
                text=f"#{idx + 1:02d}  {icon}  {desc}",
                font=ctk.CTkFont(size=12, weight="bold" if idx == self.selected_event_index else "normal"),
                text_color=color
            ).pack(side="left", padx=10)

            # Click row to select
            row_frame.bind("<Button-1>", lambda e, i=idx: self._select_event(i))

    def _select_event(self, index: int):
        self.selected_event_index = index
        self.render_events()

    def toggle_recording(self):
        if self.selected_macro_index is None:
            return

        top = self.winfo_toplevel()
        if not self.is_recording:
            self.is_recording = True
            self.btn_record.configure(text="⏹️ Parar Gravação", fg_color="#F59E0B", hover_color="#D97706")
            self.last_event_time = time.time()
            try:
                top.bind("<KeyPress>", self._on_key_press)
                top.bind("<KeyRelease>", self._on_key_release)
            except Exception as e:
                print(f"[Macro] Erro ao registrar listener: {e}")
        else:
            self.is_recording = False
            self.btn_record.configure(text="⏺️ Gravar Teclas", fg_color="#FF0033", hover_color="#D6002A")
            try:
                top.unbind("<KeyPress>")
                top.unbind("<KeyRelease>")
            except Exception:
                pass

    def _on_key_press(self, event):
        if not self.is_recording or self.selected_macro_index is None:
            return
        now = time.time()
        delay = int((now - self.last_event_time) * 1000)
        self.last_event_time = now

        macro = self.profile.macros[self.selected_macro_index]
        if delay > 20 and len(macro.events) > 0:
            macro.events.append(MacroItem(event_type="delay", delay_ms=min(delay, 2000)))

        key_name = event.keysym.upper()
        code = HID_KEYCODES.get(key_name, 0)
        macro.events.append(MacroItem(event_type="down", code=code, key_name=key_name, delay_ms=50))
        self.render_events()

    def _on_key_release(self, event):
        if not self.is_recording or self.selected_macro_index is None:
            return
        now = time.time()
        delay = int((now - self.last_event_time) * 1000)
        self.last_event_time = now

        macro = self.profile.macros[self.selected_macro_index]
        if delay > 20:
            macro.events.append(MacroItem(event_type="delay", delay_ms=min(delay, 2000)))

        key_name = event.keysym.upper()
        code = HID_KEYCODES.get(key_name, 0)
        macro.events.append(MacroItem(event_type="up", code=code, key_name=key_name, delay_ms=50))
        self.render_events()

    def insert_delay(self):
        if self.selected_macro_index is None:
            return
        macro = self.profile.macros[self.selected_macro_index]
        macro.events.append(MacroItem(event_type="delay", delay_ms=50))
        self.render_events()

    def delete_selected_event(self):
        if self.selected_macro_index is None or self.selected_event_index is None:
            return
        macro = self.profile.macros[self.selected_macro_index]
        if 0 <= self.selected_event_index < len(macro.events):
            del macro.events[self.selected_event_index]
            self.selected_event_index = None
            self.render_events()

    def move_event_up(self):
        if self.selected_macro_index is None or self.selected_event_index is None:
            return
        macro = self.profile.macros[self.selected_macro_index]
        idx = self.selected_event_index
        if idx > 0:
            macro.events[idx], macro.events[idx - 1] = macro.events[idx - 1], macro.events[idx]
            self.selected_event_index = idx - 1
            self.render_events()

    def move_event_down(self):
        if self.selected_macro_index is None or self.selected_event_index is None:
            return
        macro = self.profile.macros[self.selected_macro_index]
        idx = self.selected_event_index
        if idx < len(macro.events) - 1:
            macro.events[idx], macro.events[idx + 1] = macro.events[idx + 1], macro.events[idx]
            self.selected_event_index = idx + 1
            self.render_events()

    def create_macro(self):
        new_id = f"macro_{len(self.profile.macros) + 1}"
        m = Macro(new_id, f"Nova Macro {len(self.profile.macros) + 1}")
        self.profile.macros.append(m)
        self.select_macro(len(self.profile.macros) - 1)
        if self.on_change:
            self.on_change()

    def delete_selected_macro(self):
        if self.selected_macro_index is None:
            return
        del self.profile.macros[self.selected_macro_index]
        self.selected_macro_index = None
        if self.profile.macros:
            self.select_macro(0)
        else:
            self.refresh_macro_sidebar()
            self.render_events()
        if self.on_change:
            self.on_change()

    def _on_name_edited(self, _=None):
        if self.selected_macro_index is not None:
            macro = self.profile.macros[self.selected_macro_index]
            macro.name = self.txt_macro_name.get()
            self.refresh_macro_sidebar()
            if self.on_change:
                self.on_change()

    def _on_repeat_mode_changed(self, choice: str):
        if self.selected_macro_index is not None:
            macro = self.profile.macros[self.selected_macro_index]
            mapping = {
                "Executar Uma Vez": 1,
                "Enquanto Pressionada": 2,
                "Alternar Loop": 3,
                "Repetir N Vezes": 4
            }
            macro.repeat_mode = mapping.get(choice, 1)
            if self.on_change:
                self.on_change()
