"""
Husky Hailstorm Control Center - Entry Point.
Multiplatform open-source driver & GUI for Husky Hailstorm (TY69SKRGB) mechanical keyboard.
"""

import sys
import os
from core.device import HuskyDevice
from core.profiles import ProfileManager, Profile
from gui.app import HuskyApp


def main():
    print("=" * 60)
    print(" Husky Hailstorm Control Center (Open-Source Multiplatform)")
    print(" Reverse-Engineered from WitMod / TianYu TY69SKRGB")
    print("=" * 60)

    # 1. Initialize Device
    device = HuskyDevice()
    connected = device.connect()

    if connected:
        print("[USB] Teclado Husky Hailstorm conectado com sucesso!")
        info = device.get_firmware_info()
        sn = device.get_serial_number()
        if info:
            print(f"[Hardware] Modelo: {info.get('model')} | Firmware: {info.get('firmware')} | MCU: {info.get('mcu')}")
        if sn:
            print(f"[Hardware] Número de Série: {sn}")
    else:
        print("[USB] Teclado físico não detectado. Iniciando em Modo de Simulação.")

    # 2. Initialize Profiles
    profiles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")
    profile_mgr = ProfileManager(storage_dir=profiles_dir)

    # If only the fresh default profile exists, try to import existing official configuration if present
    if len(profile_mgr.profiles) == 1 and profile_mgr.current.name == "Perfil Padrão":
        appdata_dir = os.environ.get("APPDATA", "")
        official_profile_dir = os.path.join(
            appdata_dir,
            "Teclado Gamer Hailstorm",
            "UserConfig",
            "TY69SKRGB"
        )
        if os.path.exists(official_profile_dir):
            for root, _, files in os.walk(official_profile_dir):
                if "witmodProFile.xml" in files:
                    try:
                        xml_path = os.path.join(root, "witmodProFile.xml")
                        imported = Profile.import_xml(xml_path)
                        imported.name = "Perfil Importado do App Oficial"
                        profile_mgr.profiles.append(imported)
                        profile_mgr.active_index = len(profile_mgr.profiles) - 1
                        profile_mgr.save_current()
                        print(f"[Config] Perfil oficial importado de {xml_path}")
                        break
                    except Exception as e:
                        print(f"[Config] Falha ao importar perfil oficial: {e}")

    # 3. Launch GUI
    print("[GUI] Inicializando interface CustomTkinter...")
    app = HuskyApp(device=device, profile_manager=profile_mgr)
    
    try:
        app.mainloop()
    finally:
        # Clean shutdown
        device.close()
        print("[Shutdown] Conexão USB encerrada.")


if __name__ == "__main__":
    main()
