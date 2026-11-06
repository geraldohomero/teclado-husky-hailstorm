"""
Hardware Settings, Profiles & Firmware Tab for Husky Hailstorm.
Provides Polling Rate selector (125-1000Hz), Win Lock, Live Device Status,
Profile Import/Export (JSON & Official XML), and Factory Reset.
"""

import os
import customtkinter as ctk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from typing import Callable, Optional
from core.device import HuskyDevice
from core.profiles import Profile, ProfileManager


class TabSettings(ctk.CTkFrame):
    """Settings, hardware status, and profile management tab."""
    def __init__(
        self,
        parent,
        device: HuskyDevice,
        profile_manager: ProfileManager,
        on_profile_switched: Optional[Callable[[Profile], None]] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.device = device
        self.profile_mgr = profile_manager
        self.on_profile_switched = on_profile_switched

        self.win_lock_var = ctk.BooleanVar(value=self.profile_mgr.current.win_lock)

        self._build_ui()
        self.refresh_device_info()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Hardware Controls & Device Info
        left_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        ctk.CTkLabel(
            left_card,
            text="⚙️ Parâmetros do Hardware",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 8))

        # 1. Polling Rate
        poll_box = ctk.CTkFrame(left_card, fg_color="#121319", corner_radius=10)
        poll_box.pack(fill="x", padx=15, pady=8)
        poll_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            poll_box,
            text="Taxa de Resposta (Polling Rate):",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self.polling_combo = ctk.CTkComboBox(
            poll_box,
            values=["1000 Hz (1 ms - Recomendado)", "500 Hz (2 ms)", "250 Hz (4 ms)", "125 Hz (8 ms)"],
            command=self._on_polling_rate_selected,
            width=220
        )
        self.polling_combo.grid(row=0, column=1, padx=12, pady=12, sticky="e")

        # 2. Win Lock
        win_box = ctk.CTkFrame(left_card, fg_color="#121319", corner_radius=10)
        win_box.pack(fill="x", padx=15, pady=8)

        self.chk_win_lock = ctk.CTkCheckBox(
            win_box,
            text="Bloquear Tecla Windows (Win Lock)",
            variable=self.win_lock_var,
            font=ctk.CTkFont(weight="bold"),
            command=self._on_win_lock_toggle
        )
        self.chk_win_lock.pack(side="left", padx=12, pady=12)

        # 3. Device Info Card
        info_header = ctk.CTkFrame(left_card, fg_color="transparent")
        info_header.pack(fill="x", padx=15, pady=(15, 4))
        ctk.CTkLabel(
            info_header,
            text="🔍 Diagnóstico & Firmware",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            info_header,
            text="🔄 Atualizar",
            width=70,
            height=26,
            fg_color="#262936",
            hover_color="#363A4D",
            command=self.refresh_device_info
        ).pack(side="right")

        self.info_box = ctk.CTkFrame(left_card, fg_color="#121319", corner_radius=10)
        self.info_box.pack(fill="both", expand=True, padx=15, pady=(4, 15))
        self.info_box.grid_columnconfigure(1, weight=1)

        self.lbl_hw_status = self._create_info_row("Status USB:", "Verificando...", 0)
        self.lbl_hw_model = self._create_info_row("Modelo:", "TY69SKRGB", 1)
        self.lbl_hw_mcu = self._create_info_row("MCU:", "Winbond / M252", 2)
        self.lbl_hw_fw = self._create_info_row("Firmware:", "V1.04.10", 3)
        self.lbl_hw_sn = self._create_info_row("Número de Série:", "ccaba42cd0464b2fbdc89f760c569555", 4)

        # Right Column: Profile Management & Factory Reset
        right_card = ctk.CTkFrame(self, fg_color="#181A22", corner_radius=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        ctk.CTkLabel(
            right_card,
            text="💾 Gerenciamento de Perfis",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 8))

        # Profile Switcher
        prof_box = ctk.CTkFrame(right_card, fg_color="#121319", corner_radius=10)
        prof_box.pack(fill="x", padx=15, pady=8)
        prof_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(prof_box, text="Perfil Ativo:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.profile_combo = ctk.CTkComboBox(
            prof_box,
            values=[p.name for p in self.profile_mgr.profiles],
            command=self._on_profile_dropdown_selected,
            width=200
        )
        self.profile_combo.grid(row=0, column=1, padx=12, pady=12, sticky="e")

        # Profile Actions
        act_frame = ctk.CTkFrame(right_card, fg_color="transparent")
        act_frame.pack(fill="x", padx=15, pady=5)
        act_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            act_frame,
            text="➕ Novo Perfil",
            fg_color="#0066FF",
            hover_color="#0052CC",
            height=34,
            command=self.create_new_profile
        ).grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        ctk.CTkButton(
            act_frame,
            text="🗑️ Excluir Perfil",
            fg_color="#881337",
            hover_color="#9F1239",
            height=34,
            command=self.delete_current_profile
        ).grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Import & Export Buttons
        io_box = ctk.CTkFrame(right_card, fg_color="#121319", corner_radius=10)
        io_box.pack(fill="x", padx=15, pady=10)
        io_box.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            io_box,
            text="Importação & Exportação Multiplataforma",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color="#CBD5E1"
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w")

        ctk.CTkButton(
            io_box,
            text="📤 Exportar JSON",
            fg_color="#262936",
            hover_color="#363A4D",
            height=32,
            command=self.export_json
        ).grid(row=1, column=0, padx=8, pady=4, sticky="ew")

        ctk.CTkButton(
            io_box,
            text="📥 Importar JSON",
            fg_color="#262936",
            hover_color="#363A4D",
            height=32,
            command=self.import_json
        ).grid(row=1, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkButton(
            io_box,
            text="📤 Exportar XML Oficial",
            fg_color="#262936",
            hover_color="#363A4D",
            height=32,
            command=self.export_xml
        ).grid(row=2, column=0, padx=8, pady=(4, 10), sticky="ew")

        ctk.CTkButton(
            io_box,
            text="📥 Importar XML Oficial",
            fg_color="#262936",
            hover_color="#363A4D",
            height=32,
            command=self.import_xml
        ).grid(row=2, column=1, padx=8, pady=(4, 10), sticky="ew")

        # Factory Reset Warning Card
        reset_box = ctk.CTkFrame(right_card, fg_color="#231317", corner_radius=10)
        reset_box.pack(fill="x", padx=15, pady=(10, 15))

        ctk.CTkLabel(
            reset_box,
            text="⚠️ Zona de Perigo - Reset Onboard",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color="#F43F5E"
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            reset_box,
            text="Restaura a memória onboard do microcontrolador para os padrões de fábrica.",
            font=ctk.CTkFont(size=11),
            text_color="#FDA4AF"
        ).pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkButton(
            reset_box,
            text="🔄 Restaurar Teclado aos Padrões de Fábrica",
            fg_color="#E11D48",
            hover_color="#BE123C",
            height=36,
            font=ctk.CTkFont(weight="bold"),
            command=self.factory_reset
        ).pack(fill="x", padx=12, pady=(0, 10))

    def _create_info_row(self, title: str, default_val: str, row_idx: int) -> ctk.CTkLabel:
        ctk.CTkLabel(
            self.info_box,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8E94A8"
        ).grid(row=row_idx, column=0, padx=12, pady=6, sticky="w")

        lbl = ctk.CTkLabel(
            self.info_box,
            text=default_val,
            font=ctk.CTkFont(size=12),
            text_color="#E2E8F0"
        )
        lbl.grid(row=row_idx, column=1, padx=12, pady=6, sticky="w")
        return lbl

    def refresh_device_info(self):
        """Reads hardware serial number and firmware version live over USB HID."""
        if self.device.is_connected:
            self.lbl_hw_status.configure(text="🟢 Conectado (USB HID Interface 2)", text_color="#10B981")
            info = self.device.get_firmware_info()
            if info:
                self.lbl_hw_model.configure(text=f"{info.get('model', 'TY69SKRGB')} ({info.get('type', 'KB')})")
                self.lbl_hw_mcu.configure(text=f"{info.get('mcu', 'M252')} ({info.get('oem', 'TY')})")
                self.lbl_hw_fw.configure(text=info.get('firmware', 'V1.04.10'))

            sn = self.device.get_serial_number()
            if sn:
                self.lbl_hw_sn.configure(text=sn)
        else:
            self.lbl_hw_status.configure(text="🟡 Modo Simulação (Virtual)", text_color="#F59E0B")

    def _on_polling_rate_selected(self, choice: str):
        mapping = {
            "1000 Hz": 1000,
            "500 Hz": 500,
            "250 Hz": 250,
            "125 Hz": 125
        }
        for k, hz in mapping.items():
            if k in choice:
                self.profile_mgr.current.polling_rate = hz
                self.device.set_polling_rate(hz)
                break

    def _on_win_lock_toggle(self):
        self.profile_mgr.current.win_lock = self.win_lock_var.get()

    def _on_profile_dropdown_selected(self, choice: str):
        for idx, p in enumerate(self.profile_mgr.profiles):
            if p.name == choice:
                self.profile_mgr.active_index = idx
                if self.on_profile_switched:
                    self.on_profile_switched(p)
                break

    def create_new_profile(self):
        name = f"Perfil {len(self.profile_mgr.profiles) + 1}"
        new_prof = self.profile_mgr.add_profile(name)
        self.profile_combo.configure(values=[p.name for p in self.profile_mgr.profiles])
        self.profile_combo.set(new_prof.name)
        if self.on_profile_switched:
            self.on_profile_switched(new_prof)

    def delete_current_profile(self):
        if len(self.profile_mgr.profiles) <= 1:
            messagebox.showwarning("Aviso", "Você deve manter ao menos um perfil ativo.")
            return
        self.profile_mgr.delete_profile(self.profile_mgr.active_index)
        self.profile_combo.configure(values=[p.name for p in self.profile_mgr.profiles])
        self.profile_combo.set(self.profile_mgr.current.name)
        if self.on_profile_switched:
            self.on_profile_switched(self.profile_mgr.current)

    def export_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json")],
            initialfile=f"{self.profile_mgr.current.name}.json"
        )
        if path:
            self.profile_mgr.current.save_json(path)
            messagebox.showinfo("Sucesso", f"Perfil exportado com sucesso para:\n{path}")

    def import_json(self):
        path = filedialog.askopenfilename(
            filetypes=[("Arquivos JSON", "*.json")]
        )
        if path:
            try:
                prof = Profile.load_json(path)
                self.profile_mgr.profiles.append(prof)
                self.profile_mgr.active_index = len(self.profile_mgr.profiles) - 1
                self.profile_combo.configure(values=[p.name for p in self.profile_mgr.profiles])
                self.profile_combo.set(prof.name)
                if self.on_profile_switched:
                    self.on_profile_switched(prof)
                messagebox.showinfo("Sucesso", "Perfil importado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao importar perfil JSON: {e}")

    def export_xml(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("Perfil Hailstorm XML", "*.xml")],
            initialfile="witmodProFile.xml"
        )
        if path:
            self.profile_mgr.current.export_xml(path)
            messagebox.showinfo("Sucesso", f"Perfil oficial XML exportado com sucesso para:\n{path}")

    def import_xml(self):
        path = filedialog.askopenfilename(
            filetypes=[("Perfil Hailstorm XML", "*.xml")]
        )
        if path:
            try:
                prof = Profile.import_xml(path)
                self.profile_mgr.profiles.append(prof)
                self.profile_mgr.active_index = len(self.profile_mgr.profiles) - 1
                self.profile_combo.configure(values=[p.name for p in self.profile_mgr.profiles])
                self.profile_combo.set(prof.name)
                if self.on_profile_switched:
                    self.on_profile_switched(prof)
                messagebox.showinfo("Sucesso", "Perfil oficial XML importado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao importar XML oficial: {e}")

    def factory_reset(self):
        confirm = messagebox.askyesno(
            "Confirmação de Reset de Fábrica",
            "Tem certeza de que deseja restaurar as configurações do hardware para o padrão de fábrica?\n\nTodas as customizações gravadas na memória do teclado serão redefinidas.",
            icon="warning"
        )
        if confirm:
            ok = self.device.factory_reset()
            if ok:
                messagebox.showinfo("Reset Concluído", "Comando de restauração enviado com sucesso ao microcontrolador!")
                self.refresh_device_info()
            else:
                messagebox.showerror("Erro", "Não foi possível enviar o comando de reset.")
