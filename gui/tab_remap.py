"""
Key Remapping Tab for Husky Hailstorm.
Supports Default Layer, FN Layer, and FN1 Layer remapping,
including standard keys, mouse events, multimedia, system actions, macros, and key disabling.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from core.keycodes import KEYBOARD_LAYOUT, HID_KEYCODES, CODE_TO_NAME, SPECIAL_ACTIONS
from core.profiles import Profile
from core.device import HuskyDevice
from gui.keyboard_view import KeyboardCanvas


class TabRemap(ctk.CTkFrame):
    """Key remapping panel."""
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

        self.selected_slot: Optional[int] = None
        self.active_layer: str = "default"  # "default", "fn", "fn1"

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Layer Selection & Key Inspector
        left_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        ctk.CTkLabel(
            left_card,
            text="📑 Camadas de Função (Layers)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 8))

        # Layer Segmented Button
        self.layer_seg = ctk.CTkSegmentedButton(
            left_card,
            values=["Camada Padrão (Base)", "Camada FN", "Camada FN1"],
            command=self._on_layer_changed
        )
        self.layer_seg.set("Camada Padrão (Base)")
        self.layer_seg.pack(fill="x", padx=15, pady=8)

        # Key Inspector Box
        self.inspector_card = ctk.CTkFrame(left_card, fg_color="#121319", corner_radius=10)
        self.inspector_card.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            self.inspector_card,
            text="Tecla Físico Selecionada:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8E94A8"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        self.lbl_selected_key = ctk.CTkLabel(
            self.inspector_card,
            text="Clique em uma tecla no teclado acima",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00F0FF"
        )
        self.lbl_selected_key.pack(anchor="w", padx=15, pady=2)

        self.lbl_current_mapping = ctk.CTkLabel(
            self.inspector_card,
            text="Função Atual: Padrão de Fábrica",
            font=ctk.CTkFont(size=12),
            text_color="#CBD5E1"
        )
        self.lbl_current_mapping.pack(anchor="w", padx=15, pady=(2, 12))

        # Quick Actions
        action_row = ctk.CTkFrame(left_card, fg_color="transparent")
        action_row.pack(fill="x", padx=15, pady=5)
        action_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_reset_key = ctk.CTkButton(
            action_row,
            text="↺ Restaurar Padrão",
            fg_color="#262936",
            hover_color="#363A4D",
            height=34,
            command=self.reset_key_to_default
        )
        self.btn_reset_key.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.btn_disable_key = ctk.CTkButton(
            action_row,
            text="🚫 Desativar Tecla",
            fg_color="#881337",
            hover_color="#9F1239",
            height=34,
            command=self.disable_key
        )
        self.btn_disable_key.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Right Column: Remap Assignment Palette
        right_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        ctk.CTkLabel(
            right_card,
            text="🎯 Atribuir Nova Função",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 8))

        # Tabs for Remap Categories
        self.category_tabs = ctk.CTkTabview(right_card, fg_color="#121319")
        self.category_tabs.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        tab_kb = self.category_tabs.add("Teclado")
        tab_mouse = self.category_tabs.add("Mouse")
        tab_media = self.category_tabs.add("Multimídia")
        tab_system = self.category_tabs.add("Sistema")
        tab_macro = self.category_tabs.add("Macros")

        # 1. Keyboard Tab
        self._build_keyboard_grid(tab_kb)

        # 2. Mouse Tab
        self._build_mouse_grid(tab_mouse)

        # 3. Multimedia Tab
        self._build_media_grid(tab_media)

        # 4. System Tab
        self._build_system_grid(tab_system)

        # 5. Macro Tab
        self._build_macro_grid(tab_macro)

    def _build_keyboard_grid(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Group common keys
        sections = [
            ("Letras", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")),
            ("Números", ["1!", "2@", "3#", "4$", "5%", "6^", "7&", "8*", "9(", "0)"]),
            ("Teclas de Função", [f"F{i}" for i in range(1, 13)]),
            ("Navegação & Controle", ["Enter", "Esc", "Back", "Tab", "Space", "Delete", "Home", "PageUp", "PageDn", "End", "Up", "Down", "Left", "Right", "Caps"]),
            ("Modificadores", ["LCtrl", "LShift", "LAlt", "LWin", "RCtrl", "RShift", "RAlt"])
        ]

        for sec_name, keys in sections:
            ctk.CTkLabel(scroll, text=sec_name, font=ctk.CTkFont(weight="bold", size=12), text_color="#00F0FF").pack(anchor="w", pady=(8, 4))
            grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            grid_frame.pack(fill="x", pady=2)

            for i, k_name in enumerate(keys):
                code = HID_KEYCODES.get(k_name)
                btn = ctk.CTkButton(
                    grid_frame,
                    text=k_name,
                    width=42,
                    height=28,
                    fg_color="#262936",
                    hover_color="#0066FF",
                    command=lambda c=code, n=k_name: self.assign_key(0, c, n)
                )
                btn.grid(row=i // 6, column=i % 6, padx=3, pady=3, sticky="ew")

    def _build_mouse_grid(self, parent):
        actions = [
            ("Botão Esquerdo", SPECIAL_ACTIONS['MOUSE_LEFT']),
            ("Botão Direito", SPECIAL_ACTIONS['MOUSE_RIGHT']),
            ("Botão do Meio (Scroll Click)", SPECIAL_ACTIONS['MOUSE_MIDDLE']),
            ("Navegar Avançar", SPECIAL_ACTIONS['MOUSE_FORWARD']),
            ("Navegar Voltar", SPECIAL_ACTIONS['MOUSE_BACK']),
            ("Rolar para Cima", SPECIAL_ACTIONS['WHEEL_UP']),
            ("Rolar para Baixo", SPECIAL_ACTIONS['WHEEL_DOWN'])
        ]
        for name, code in actions:
            ctk.CTkButton(
                parent,
                text=name,
                fg_color="#262936",
                hover_color="#0066FF",
                height=32,
                command=lambda c=code, n=name: self.assign_key(1, c, n)
            ).pack(fill="x", padx=10, pady=3)

    def _build_media_grid(self, parent):
        actions = [
            ("Reproduzir / Pausar", SPECIAL_ACTIONS['MEDIA_PLAY_PAUSE']),
            ("Parar (Stop)", SPECIAL_ACTIONS['MEDIA_STOP']),
            ("Faixa Anterior", SPECIAL_ACTIONS['MEDIA_PREV']),
            ("Próxima Faixa", SPECIAL_ACTIONS['MEDIA_NEXT']),
            ("Aumentar Volume (+)", SPECIAL_ACTIONS['MEDIA_VOL_UP']),
            ("Diminuir Volume (-)", SPECIAL_ACTIONS['MEDIA_VOL_DOWN']),
            ("Silenciar Áudio (Mute)", SPECIAL_ACTIONS['MEDIA_MUTE']),
            ("Abrir Media Player", SPECIAL_ACTIONS['MEDIA_PLAYER'])
        ]
        for name, code in actions:
            ctk.CTkButton(
                parent,
                text=name,
                fg_color="#262936",
                hover_color="#0066FF",
                height=32,
                command=lambda c=code, n=name: self.assign_key(2, c, n)
            ).pack(fill="x", padx=10, pady=3)

    def _build_system_grid(self, parent):
        actions = [
            ("Calculadora", SPECIAL_ACTIONS['SYS_CALCULATOR']),
            ("Meu Computador", SPECIAL_ACTIONS['SYS_MY_COMPUTER']),
            ("Navegador Web", SPECIAL_ACTIONS['SYS_BROWSER']),
            ("Cliente de E-mail", SPECIAL_ACTIONS['SYS_EMAIL']),
            ("Pesquisar", SPECIAL_ACTIONS['SYS_SEARCH']),
            ("Mostrar Área de Trabalho", SPECIAL_ACTIONS['SYS_DESKTOP']),
            ("Bloquear Computador (Win+L)", SPECIAL_ACTIONS['SYS_LOCK_PC']),
            ("Copiar (Ctrl+C)", SPECIAL_ACTIONS['SYS_COPY'])
        ]
        for name, code in actions:
            ctk.CTkButton(
                parent,
                text=name,
                fg_color="#262936",
                hover_color="#0066FF",
                height=32,
                command=lambda c=code, n=name: self.assign_key(3, c, n)
            ).pack(fill="x", padx=10, pady=3)

    def _build_macro_grid(self, parent):
        self.macro_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.macro_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.refresh_macro_list()

    def refresh_macro_list(self):
        for w in self.macro_scroll.winfo_children():
            w.destroy()

        if not self.profile.macros:
            ctk.CTkLabel(
                self.macro_scroll,
                text="Nenhuma macro criada ainda.\nCrie uma na aba 'Macros' primeiro.",
                text_color="#8E94A8"
            ).pack(pady=20)
            return

        for m in self.profile.macros:
            ctk.CTkButton(
                self.macro_scroll,
                text=f"⚡ {m.name}",
                fg_color="#262936",
                hover_color="#FF0033",
                height=32,
                command=lambda mac=m: self.assign_key(4, 0, f"Macro: {mac.name}")
            ).pack(fill="x", padx=5, pady=3)

    def on_key_selected(self, slot: int, key_info: dict):
        """Called when a key is clicked on the KeyboardCanvas."""
        self.selected_slot = slot
        label = key_info.get("label", f"Slot {slot}")
        self.lbl_selected_key.configure(text=f"{label} (Slot #{slot})")

        layer_dict = self._get_active_layer_dict()
        mapping = layer_dict.get(slot)
        if mapping:
            self.lbl_current_mapping.configure(text=f"Função Atual: {mapping.get('name', 'Personalizada')}")
        else:
            self.lbl_current_mapping.configure(text=f"Função Atual: {label} (Padrão de Fábrica)")

    def _on_layer_changed(self, choice: str):
        if "FN1" in choice:
            self.active_layer = "fn1"
        elif "FN" in choice:
            self.active_layer = "fn"
        else:
            self.active_layer = "default"

        self.canvas.set_layer(self.active_layer, self._get_active_layer_dict())
        if self.selected_slot:
            key_info = next((k for k in KEYBOARD_LAYOUT if k['slot'] == self.selected_slot), None)
            if key_info:
                self.on_key_selected(self.selected_slot, key_info)

    def _get_active_layer_dict(self) -> Dict[int, dict]:
        if self.active_layer == "fn1":
            return self.profile.layer_fn1
        elif self.active_layer == "fn":
            return self.profile.layer_fn
        return self.profile.layer_default

    def assign_key(self, op_type: int, code: int, name: str):
        """Assigns the new mapping to the selected key slot in the active layer."""
        if self.selected_slot is None:
            return

        layer_dict = self._get_active_layer_dict()
        layer_dict[self.selected_slot] = {
            "type": op_type,
            "code": code,
            "name": name
        }

        self.canvas.set_layer(self.active_layer, layer_dict)
        self.lbl_current_mapping.configure(text=f"Função Atual: {name}")

        if self.on_change:
            self.on_change()

    def reset_key_to_default(self):
        """Removes custom remap for the selected key, restoring its default behavior."""
        if self.selected_slot is None:
            return

        layer_dict = self._get_active_layer_dict()
        if self.selected_slot in layer_dict:
            del layer_dict[self.selected_slot]

        self.canvas.set_layer(self.active_layer, layer_dict)
        key_info = next((k for k in KEYBOARD_LAYOUT if k['slot'] == self.selected_slot), None)
        orig_name = key_info['label'] if key_info else "Padrão"
        self.lbl_current_mapping.configure(text=f"Função Atual: {orig_name} (Padrão de Fábrica)")

        if self.on_change:
            self.on_change()

    def disable_key(self):
        """Disables the selected key."""
        self.assign_key(SPECIAL_ACTIONS['DISABLE_KEY'], 0, "🚫 DESATIVADA")
