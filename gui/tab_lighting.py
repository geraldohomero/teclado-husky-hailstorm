"""
Lighting Effects & RGB Controls Tab for Husky Hailstorm.
Provides controls for all 18 official keyboard effects, side lights,
brightness, speed, direction, color mode, and curated palettes.
"""

import customtkinter as ctk
import tkinter.colorchooser as colorchooser
from typing import Callable, Optional
from core.lighting import (
    KEYBOARD_EFFECTS,
    SIDE_EFFECTS,
    COLOR_MODES,
    DIRECTIONS,
    PALETTE_PRESETS,
    hex_to_rgb,
    rgb_to_hex
)
from core.device import HuskyDevice
from core.profiles import Profile


class TabLighting(ctk.CTkFrame):
    """Lighting settings tab frame."""
    def __init__(
        self,
        parent,
        device: HuskyDevice,
        profile: Profile,
        on_change_callback: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.device = device
        self.profile = profile
        self.on_change = on_change_callback

        self.auto_apply = ctk.BooleanVar(value=True)

        self._build_ui()
        self.sync_from_profile()

    def _build_ui(self):
        # Configure grid: 2 columns
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Keyboard Lighting controls
        left_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        left_card.grid_columnconfigure(1, weight=1)

        # Card Title
        title_box = ctk.CTkFrame(left_card, fg_color="transparent")
        title_box.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 10))
        ctk.CTkLabel(
            title_box,
            text="✨ Efeitos de Iluminação Principal",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        # 1. Effect Selector
        ctk.CTkLabel(left_card, text="Efeito RGB:", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, sticky="w", padx=15, pady=8
        )
        effect_names = [f"{e['id']:02d} - {e['name']}" for e in KEYBOARD_EFFECTS]
        self.effect_combo = ctk.CTkComboBox(
            left_card,
            values=effect_names,
            width=260,
            command=self._on_effect_selected
        )
        self.effect_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=8)

        # Effect Description label
        self.lbl_effect_desc = ctk.CTkLabel(
            left_card,
            text="",
            text_color="#8E94A8",
            font=ctk.CTkFont(size=12, slant="italic")
        )
        self.lbl_effect_desc.grid(row=2, column=1, sticky="w", padx=15, pady=(0, 10))

        # 2. Color Mode (Single vs Rainbow)
        ctk.CTkLabel(left_card, text="Modo de Cor:").grid(
            row=3, column=0, sticky="w", padx=15, pady=8
        )
        self.color_mode_seg = ctk.CTkSegmentedButton(
            left_card,
            values=["Cor Fixa", "Arco-íris / RGB"],
            command=self._on_color_mode_change
        )
        self.color_mode_seg.grid(row=3, column=1, sticky="ew", padx=15, pady=8)

        # 3. Brightness Slider (0 - 4)
        ctk.CTkLabel(left_card, text="Brilho:").grid(
            row=4, column=0, sticky="w", padx=15, pady=8
        )
        bright_box = ctk.CTkFrame(left_card, fg_color="transparent")
        bright_box.grid(row=4, column=1, sticky="ew", padx=15, pady=8)
        bright_box.grid_columnconfigure(0, weight=1)

        self.slider_bright = ctk.CTkSlider(
            bright_box,
            from_=0,
            to=4,
            number_of_steps=4,
            command=self._on_slider_change
        )
        self.slider_bright.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.lbl_bright_val = ctk.CTkLabel(bright_box, text="3", width=25, font=ctk.CTkFont(weight="bold"))
        self.lbl_bright_val.grid(row=0, column=1)

        # 4. Speed Slider (0 - 4)
        ctk.CTkLabel(left_card, text="Velocidade:").grid(
            row=5, column=0, sticky="w", padx=15, pady=8
        )
        speed_box = ctk.CTkFrame(left_card, fg_color="transparent")
        speed_box.grid(row=5, column=1, sticky="ew", padx=15, pady=8)
        speed_box.grid_columnconfigure(0, weight=1)

        self.slider_speed = ctk.CTkSlider(
            speed_box,
            from_=0,
            to=4,
            number_of_steps=4,
            command=self._on_slider_change
        )
        self.slider_speed.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.lbl_speed_val = ctk.CTkLabel(speed_box, text="3", width=25, font=ctk.CTkFont(weight="bold"))
        self.lbl_speed_val.grid(row=0, column=1)

        # 5. Direction Selector
        ctk.CTkLabel(left_card, text="Direção:").grid(
            row=6, column=0, sticky="w", padx=15, pady=8
        )
        dir_names = [d["name"] for d in DIRECTIONS]
        self.dir_combo = ctk.CTkComboBox(
            left_card,
            values=dir_names,
            width=260,
            command=self._on_dir_change
        )
        self.dir_combo.grid(row=6, column=1, sticky="ew", padx=15, pady=8)

        # 6. Primary Color Chips
        ctk.CTkLabel(left_card, text="Paleta de Cores:").grid(
            row=7, column=0, sticky="w", padx=15, pady=8
        )
        pal_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        pal_frame.grid(row=7, column=1, sticky="w", padx=15, pady=8)

        for hex_col, name in PALETTE_PRESETS[:8]:
            btn = ctk.CTkButton(
                pal_frame,
                text="",
                width=24,
                height=24,
                corner_radius=12,
                fg_color=hex_col,
                hover_color=hex_col,
                command=lambda c=hex_col: self._set_color(c)
            )
            btn.pack(side="left", padx=3)

        self.btn_custom_col = ctk.CTkButton(
            pal_frame,
            text="🎨",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="#2E3242",
            hover_color="#3D4258",
            command=self._pick_custom_color
        )
        self.btn_custom_col.pack(side="left", padx=5)

        self.color_preview = ctk.CTkButton(
            pal_frame,
            text="",
            width=32,
            height=28,
            corner_radius=6,
            fg_color=self.profile.color,
            hover_color=self.profile.color,
            border_width=2,
            border_color="#FFFFFF"
        )
        self.color_preview.pack(side="left", padx=4)

        # --- Right Column: Side Lights & Apply Action ---
        right_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        right_card.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(
            right_card,
            text="🌈 Iluminação Lateral (Side Glow)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Side Effect
        ctk.CTkLabel(right_card, text="Efeito Lateral:").grid(
            row=1, column=0, sticky="w", padx=15, pady=8
        )
        side_names = [f"{s['id']} - {s['name']}" for s in SIDE_EFFECTS]
        self.side_combo = ctk.CTkComboBox(
            right_card,
            values=side_names,
            width=180,
            command=self._on_side_effect_selected
        )
        self.side_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=8)

        # Side Brightness
        ctk.CTkLabel(right_card, text="Brilho Lateral:").grid(
            row=2, column=0, sticky="w", padx=15, pady=8
        )
        self.slider_side_bright = ctk.CTkSlider(
            right_card,
            from_=0,
            to=4,
            number_of_steps=4,
            command=self._on_side_change
        )
        self.slider_side_bright.grid(row=2, column=1, sticky="ew", padx=15, pady=8)

        # Side Speed
        ctk.CTkLabel(right_card, text="Velocidade:").grid(
            row=3, column=0, sticky="w", padx=15, pady=8
        )
        self.slider_side_speed = ctk.CTkSlider(
            right_card,
            from_=0,
            to=4,
            number_of_steps=4,
            command=self._on_side_change
        )
        self.slider_side_speed.grid(row=3, column=1, sticky="ew", padx=15, pady=8)

        # Action panel
        action_card = ctk.CTkFrame(right_card, fg_color="#121319", corner_radius=10)
        action_card.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=20)
        action_card.grid_columnconfigure(0, weight=1)

        self.chk_live = ctk.CTkCheckBox(
            action_card,
            text="Aplicar em Tempo Real no Teclado",
            variable=self.auto_apply,
            font=ctk.CTkFont(size=12)
        )
        self.chk_live.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 8))

        self.btn_apply = ctk.CTkButton(
            action_card,
            text="⚡ Aplicar Configurações Agora",
            fg_color="#FF0033",
            hover_color="#D6002A",
            height=38,
            font=ctk.CTkFont(weight="bold"),
            command=self.apply_to_keyboard
        )
        self.btn_apply.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))

    def sync_from_profile(self):
        """Synchronizes UI widgets from current profile values."""
        # Find effect name
        effect = next((e for e in KEYBOARD_EFFECTS if e["id"] == self.profile.light_mode), KEYBOARD_EFFECTS[0])
        self.effect_combo.set(f"{effect['id']:02d} - {effect['name']}")
        self.lbl_effect_desc.configure(text=effect["desc"])

        # Color mode
        mode_str = "Arco-íris / RGB" if self.profile.color_mode == 2 else "Cor Fixa"
        self.color_mode_seg.set(mode_str)

        # Brightness & Speed
        self.slider_bright.set(self.profile.brightness)
        self.lbl_bright_val.configure(text=str(self.profile.brightness))

        self.slider_speed.set(self.profile.speed)
        self.lbl_speed_val.configure(text=str(self.profile.speed))

        # Direction
        dir_info = next((d for d in DIRECTIONS if d["id"] == self.profile.direction), DIRECTIONS[0])
        self.dir_combo.set(dir_info["name"])

        # Color
        self.color_preview.configure(fg_color=self.profile.color, hover_color=self.profile.color)

        # Side lights
        side_info = next((s for s in SIDE_EFFECTS if s["id"] == self.profile.side_mode), SIDE_EFFECTS[0])
        self.side_combo.set(f"{side_info['id']} - {side_info['name']}")
        self.slider_side_bright.set(self.profile.side_brightness)
        self.slider_side_speed.set(self.profile.side_speed)

    def _on_effect_selected(self, choice: str):
        mode_id = int(choice.split(" - ")[0])
        self.profile.light_mode = mode_id
        effect = next((e for e in KEYBOARD_EFFECTS if e["id"] == mode_id), None)
        if effect:
            self.lbl_effect_desc.configure(text=effect["desc"])
        self._notify_change()

    def _on_color_mode_change(self, value: str):
        self.profile.color_mode = 2 if "Arco-íris" in value else 1
        self._notify_change()

    def _on_slider_change(self, _=None):
        self.profile.brightness = int(round(self.slider_bright.get()))
        self.lbl_bright_val.configure(text=str(self.profile.brightness))

        self.profile.speed = int(round(self.slider_speed.get()))
        self.lbl_speed_val.configure(text=str(self.profile.speed))
        self._notify_change()

    def _on_dir_change(self, choice: str):
        dir_item = next((d for d in DIRECTIONS if d["name"] == choice), None)
        if dir_item:
            self.profile.direction = dir_item["id"]
        self._notify_change()

    def _set_color(self, hex_color: str):
        self.profile.color = hex_color
        self.color_preview.configure(fg_color=hex_color, hover_color=hex_color)
        self._notify_change()

    def _pick_custom_color(self):
        color = colorchooser.askcolor(color=self.profile.color, title="Escolha a Cor RGB")[1]
        if color:
            self._set_color(color.upper())

    def _on_side_effect_selected(self, choice: str):
        side_id = int(choice.split(" - ")[0])
        self.profile.side_mode = side_id
        self._notify_change()

    def _on_side_change(self, _=None):
        self.profile.side_brightness = int(round(self.slider_side_bright.get()))
        self.profile.side_speed = int(round(self.slider_side_speed.get()))
        self._notify_change()

    def _notify_change(self):
        if self.on_change:
            self.on_change()
        if self.auto_apply.get():
            self.apply_to_keyboard()

    def apply_to_keyboard(self):
        """Sends lighting configuration directly to physical keyboard over USB HID."""
        r, g, b = hex_to_rgb(self.profile.color)
        # 1. Send Main Keyboard lighting command (0x47)
        self.device.set_lighting(
            mode_id=self.profile.light_mode,
            brightness=self.profile.brightness,
            speed=self.profile.speed,
            direction=self.profile.direction,
            color_mode=self.profile.color_mode,
            r=r, g=g, b=b,
            target=0
        )
        # 2. Commit lighting (0x17)
        self.device.apply_lighting()
