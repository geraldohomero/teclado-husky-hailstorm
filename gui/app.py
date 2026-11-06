"""
Main Application Window for Husky Hailstorm Control Center.
Assembles header, persistent interactive keyboard canvas, navigation tabs,
and status bar into a modern, responsive cross-platform GUI.
"""

import os
import customtkinter as ctk
from PIL import Image
from core.device import HuskyDevice
from core.profiles import Profile, ProfileManager
from gui.keyboard_view import KeyboardCanvas
from gui.tab_lighting import TabLighting
from gui.tab_perkey import TabPerKey
from gui.tab_remap import TabRemap
from gui.tab_macros import TabMacros
from gui.tab_settings import TabSettings


class HuskyApp(ctk.CTk):
    """Main application window."""
    def __init__(self, device: HuskyDevice, profile_manager: ProfileManager):
        super().__init__()
        self.device = device
        self.profile_mgr = profile_manager

        # Configure window properties
        self.title("Husky Hailstorm - Centro de Controle RGB Multiplataforma")
        self.geometry("1100x820")
        self.minsize(980, 720)

        # Set visual theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Set app icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "AppLogo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self._build_layout()
        self._sync_all()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Tab content expands

        # ==================== 1. TOP HEADER ====================
        header = ctk.CTkFrame(self, fg_color="#121319", height=54, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # Logo / Brand
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(
            brand_frame,
            text="🐺 HUSKY",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#FF0033"
        ).pack(side="left")

        ctk.CTkLabel(
            brand_frame,
            text=" HAILSTORM",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")

        ctk.CTkLabel(
            brand_frame,
            text=" | TY69SKRGB",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748B"
        ).pack(side="left", padx=(6, 0))

        # Status Pill & Reconnect
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        self.btn_status = ctk.CTkButton(
            status_frame,
            text="🟢 Conectado",
            height=28,
            width=130,
            fg_color="#064E3B",
            hover_color="#065F46",
            text_color="#34D399",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_reconnect_clicked
        )
        self.btn_status.pack(side="left", padx=5)

        # ==================== 2. KEYBOARD CANVAS ====================
        canvas_container = ctk.CTkFrame(self, fg_color="#14151B", corner_radius=0)
        canvas_container.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 5))
        canvas_container.grid_columnconfigure(0, weight=1)

        self.canvas = KeyboardCanvas(
            canvas_container,
            width=960,
            height=240,
            on_key_selected=self._on_key_selected,
            on_selection_change=self._on_canvas_selection_change
        )
        self.canvas.pack(fill="x", padx=10, pady=5)

        # ==================== 3. TABVIEW NAVIGATION ====================
        self.tabview = ctk.CTkTabview(self, fg_color="#14151B", corner_radius=10)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 5))

        tab_lighting_frame = self.tabview.add("💡 Iluminação")
        tab_perkey_frame = self.tabview.add("🎨 Per-Key RGB")
        tab_remap_frame = self.tabview.add("⌨️ Remapeamento")
        tab_macros_frame = self.tabview.add("⚡ Macros")
        tab_settings_frame = self.tabview.add("⚙️ Configurações & Firmware")

        # Tab Components
        self.tab_lighting = TabLighting(
            tab_lighting_frame,
            device=self.device,
            profile=self.profile_mgr.current,
            on_change_callback=self._on_profile_modified
        )
        self.tab_lighting.pack(fill="both", expand=True)

        self.tab_perkey = TabPerKey(
            tab_perkey_frame,
            device=self.device,
            profile=self.profile_mgr.current,
            keyboard_canvas=self.canvas,
            on_change_callback=self._on_profile_modified
        )
        self.tab_perkey.pack(fill="both", expand=True)

        self.tab_remap = TabRemap(
            tab_remap_frame,
            device=self.device,
            profile=self.profile_mgr.current,
            keyboard_canvas=self.canvas,
            on_change_callback=self._on_profile_modified
        )
        self.tab_remap.pack(fill="both", expand=True)

        self.tab_macros = TabMacros(
            tab_macros_frame,
            profile=self.profile_mgr.current,
            on_change_callback=self._on_profile_modified
        )
        self.tab_macros.pack(fill="both", expand=True)

        self.tab_settings = TabSettings(
            tab_settings_frame,
            device=self.device,
            profile_manager=self.profile_mgr,
            on_profile_switched=self._on_profile_switched
        )
        self.tab_settings.pack(fill="both", expand=True)

        # ==================== 4. STATUS BAR ====================
        status_bar = ctk.CTkFrame(self, fg_color="#101116", height=28, corner_radius=0)
        status_bar.grid(row=3, column=0, sticky="ew")

        self.lbl_status_msg = ctk.CTkLabel(
            status_bar,
            text="Pronto | Protocolo HID v1.0.4.10",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        )
        self.lbl_status_msg.pack(side="left", padx=15)

        self.lbl_profile_tag = ctk.CTkLabel(
            status_bar,
            text=f"Perfil: {self.profile_mgr.current.name}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8"
        )
        self.lbl_profile_tag.pack(side="right", padx=15)

    def _sync_all(self):
        """Synchronizes canvas and tabs with the active profile."""
        current = self.profile_mgr.current

        # Update canvas colors
        self.canvas.update_all_colors(current.per_key_colors)
        self.canvas.set_layer("default", current.layer_default)

        # Update connection badge
        if self.device.is_connected:
            self.btn_status.configure(
                text="🟢 Conectado",
                fg_color="#064E3B",
                hover_color="#065F46",
                text_color="#34D399"
            )
            self.lbl_status_msg.configure(text=f"Pronto | Teclado Físico TY69SKRGB Conectado (MI_02)")
        else:
            self.btn_status.configure(
                text="🟡 Simulação",
                fg_color="#78350F",
                hover_color="#92400E",
                text_color="#FCD34D"
            )
            self.lbl_status_msg.configure(text="Pronto | Modo de Simulação Ativo (Teclado Físico não detectado)")

        self.lbl_profile_tag.configure(text=f"Perfil: {current.name}")

    def _on_key_selected(self, slot: int, key_info: dict):
        """Dispatches key click to remap tab inspector."""
        self.tab_remap.on_key_selected(slot, key_info)

    def _on_canvas_selection_change(self, slots: list[int]):
        """Dispatches multi-select to per-key RGB tab."""
        self.tab_perkey.on_canvas_selection_changed(slots)

    def _on_profile_modified(self):
        """Saves current state and updates UI."""
        self.profile_mgr.save_current()

    def _on_profile_switched(self, new_profile: Profile):
        """Handles switching to a different profile."""
        self.tab_lighting.profile = new_profile
        self.tab_lighting.sync_from_profile()

        self.tab_perkey.profile = new_profile
        self.tab_remap.profile = new_profile
        self.tab_macros.profile = new_profile
        self.tab_macros.refresh_macro_sidebar()
        if new_profile.macros:
            self.tab_macros.select_macro(0)

        self._sync_all()

    def _on_reconnect_clicked(self):
        """Attempts reconnecting to the keyboard USB HID interface."""
        ok = self.device.connect()
        self._sync_all()
        self.tab_settings.refresh_device_info()
