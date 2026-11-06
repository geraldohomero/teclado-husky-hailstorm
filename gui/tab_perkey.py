"""
Per-Key RGB Studio Tab for Husky Hailstorm.
Allows painting individual keys or groups with custom RGB colors,
and streams them to the keyboard using Command 0x0F chunks and Command 0x17.
"""

import customtkinter as ctk
import tkinter.colorchooser as colorchooser
from typing import Callable, Optional, List
from core.keycodes import KEYBOARD_LAYOUT, KEY_GROUPS
from core.lighting import PALETTE_PRESETS, hex_to_rgb, rgb_to_hex
from core.device import HuskyDevice
from core.profiles import Profile
from gui.keyboard_view import KeyboardCanvas


class TabPerKey(ctk.CTkFrame):
    """Custom Per-Key RGB editor tab."""
    def __init__(
        self,
        parent,
        device: HuskyDevice,
        profile: Profile,
        keyboard_canvas: KeyboardCanvas,
        on_change_callback: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.device = device
        self.profile = profile
        self.canvas = keyboard_canvas
        self.on_change = on_change_callback

        self.current_paint_color = "#00F0FF"  # Default Cyan
        self.selected_slots: List[int] = []

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Card: Tools & Quick Groups
        left_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        ctk.CTkLabel(
            left_card,
            text="🎯 Seleção Rápida de Teclas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Group Buttons Grid
        btn_box = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=5)
        btn_box.grid_columnconfigure((0, 1, 2), weight=1)

        groups = [
            ("Todos", "Todos"),
            ("WASD", "WASD"),
            ("Setas", "Setas"),
            ("Letras", "Letras"),
            ("Números", "Números"),
            ("Modificadores", "Modificadores")
        ]

        for i, (name, grp_key) in enumerate(groups):
            r = i // 3
            c = i % 3
            b = ctk.CTkButton(
                btn_box,
                text=name,
                height=34,
                fg_color="#262936",
                hover_color="#363A4D",
                command=lambda k=grp_key: self._select_group(k)
            )
            b.grid(row=r, column=c, padx=4, pady=4, sticky="ew")

        # Instruction text
        info_card = ctk.CTkFrame(left_card, fg_color="#121319", corner_radius=8)
        info_card.pack(fill="x", padx=15, pady=(15, 10))
        ctk.CTkLabel(
            info_card,
            text="💡 Dica: Você também pode clicar diretamente nas teclas do teclado acima ou arrastar o mouse para selecionar várias teclas de uma vez.",
            wraplength=360,
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF"
        ).pack(padx=12, pady=10)

        # Selection Status label
        self.lbl_selection = ctk.CTkLabel(
            left_card,
            text="Nenhuma tecla selecionada",
            font=ctk.CTkFont(weight="bold"),
            text_color="#00F0FF"
        )
        self.lbl_selection.pack(anchor="w", padx=15, pady=(5, 10))

        # Right Card: Palette & Send to Keyboard
        right_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        ctk.CTkLabel(
            right_card,
            text="🎨 Pincel de Cores RGB",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Palette grid
        pal_grid = ctk.CTkFrame(right_card, fg_color="transparent")
        pal_grid.pack(fill="x", padx=15, pady=5)

        for hex_col, name in PALETTE_PRESETS:
            b = ctk.CTkButton(
                pal_grid,
                text="",
                width=32,
                height=32,
                corner_radius=16,
                fg_color=hex_col,
                hover_color=hex_col,
                command=lambda c=hex_col: self._set_brush_color(c)
            )
            b.pack(side="left", padx=4, pady=4)

        # Custom picker button & Active brush preview
        brush_box = ctk.CTkFrame(right_card, fg_color="transparent")
        brush_box.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            brush_box,
            text="🎨 Escolher Cor Personalizada...",
            fg_color="#262936",
            hover_color="#363A4D",
            command=self._pick_custom_brush
        ).pack(side="left", padx=(0, 10))

        self.brush_preview = ctk.CTkButton(
            brush_box,
            text="Pincel",
            width=70,
            height=32,
            fg_color=self.current_paint_color,
            hover_color=self.current_paint_color,
            text_color="#000000",
            font=ctk.CTkFont(weight="bold")
        )
        self.brush_preview.pack(side="left")

        # Action Buttons
        action_box = ctk.CTkFrame(right_card, fg_color="transparent")
        action_box.pack(fill="x", padx=15, pady=(10, 5))
        action_box.grid_columnconfigure((0, 1), weight=1)

        self.btn_paint = ctk.CTkButton(
            action_box,
            text="🖌️ Pintar Selecionadas",
            fg_color="#0066FF",
            hover_color="#0052CC",
            height=36,
            command=self.paint_selected_keys
        )
        self.btn_paint.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.btn_fill = ctk.CTkButton(
            action_box,
            text="🪣 Preencher Todas",
            fg_color="#363A4D",
            hover_color="#464B63",
            height=36,
            command=self.fill_all_keys
        )
        self.btn_fill.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Commit button
        self.btn_commit = ctk.CTkButton(
            right_card,
            text="⚡ Gravar Per-Key RGB no Teclado Físico",
            fg_color="#FF0033",
            hover_color="#D6002A",
            height=42,
            font=ctk.CTkFont(weight="bold"),
            command=self.apply_to_keyboard
        )
        self.btn_commit.pack(fill="x", padx=15, pady=(20, 15))

    def on_canvas_selection_changed(self, slots: List[int]):
        """Called by KeyboardCanvas whenever keys are clicked or selected."""
        self.selected_slots = slots
        count = len(slots)
        if count == 0:
            self.lbl_selection.configure(text="Nenhuma tecla selecionada", text_color="#8E94A8")
        elif count == 1:
            key = next((k for k in KEYBOARD_LAYOUT if k['slot'] == slots[0]), None)
            name = key['label'] if key else f"Slot {slots[0]}"
            self.lbl_selection.configure(text=f"1 tecla selecionada: {name}", text_color="#00F0FF")
        else:
            self.lbl_selection.configure(text=f"{count} teclas selecionadas", text_color="#00F0FF")

    def _select_group(self, group_name: str):
        slots = KEY_GROUPS.get(group_name, [])
        self.canvas.select_slots(slots)
        self.on_canvas_selection_changed(slots)

    def _set_brush_color(self, hex_color: str):
        self.current_paint_color = hex_color
        self.brush_preview.configure(
            fg_color=hex_color,
            hover_color=hex_color,
            text_color="#000000" if hex_color not in ["#1A1A1A", "#000000"] else "#FFFFFF"
        )

    def _pick_custom_brush(self):
        col = colorchooser.askcolor(color=self.current_paint_color, title="Pincel RGB")[1]
        if col:
            self._set_brush_color(col.upper())

    def paint_selected_keys(self):
        """Applies current brush color to all selected keys."""
        if not self.selected_slots:
            return
        for slot in self.selected_slots:
            self.profile.per_key_colors[slot] = self.current_paint_color
            self.canvas.set_key_color(slot, self.current_paint_color)
        if self.on_change:
            self.on_change()

    def fill_all_keys(self):
        """Paints all 68 keyboard keys with current brush color."""
        for k in KEYBOARD_LAYOUT:
            slot = k['slot']
            self.profile.per_key_colors[slot] = self.current_paint_color
            self.canvas.set_key_color(slot, self.current_paint_color)
        if self.on_change:
            self.on_change()

    def apply_to_keyboard(self):
        """Streams chunked 0x0F packets and 0x17 commit to physical keyboard."""
        # Step 1: Set keyboard to Custom RGB mode (ID 14)
        self.device.set_lighting(mode_id=14, brightness=self.profile.brightness, speed=0, target=0)

        # Step 2: Stream per-key colors in 18-key (54 bytes) chunks
        # Collect ordered slots
        slots = [k['slot'] for k in KEYBOARD_LAYOUT]
        chunk_size = 18
        chunk_idx = 0

        for i in range(0, len(slots), chunk_size):
            batch = slots[i:i + chunk_size]
            rgb_bytes = bytearray()
            for slot in batch:
                hex_col = self.profile.per_key_colors.get(slot, "#FF0033")
                r, g, b = hex_to_rgb(hex_col)
                rgb_bytes.extend([r, g, b])

            self.device.write_color_chunk(chunk_index=chunk_idx, rgb_data=bytes(rgb_bytes), target=0)
            chunk_idx += 1

        # Step 3: Commit
        self.device.apply_lighting()
