"""
Build script to compile Husky Hailstorm Control Center into a standalone binary/executable.
Works across Windows (.exe), Linux (ELF), and macOS (.app).
"""

import sys
import os
import subprocess
import platform


def main():
    print("=" * 60)
    print(" Husky Hailstorm Control Center - Build Utility")
    print("=" * 60)

    # 1. Verify PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller detectado: versão {PyInstaller.__version__}")
    except ImportError:
        print("[!] PyInstaller não encontrado. Instalando via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Determine OS separator for --add-data
    sep = ";" if platform.system() == "Windows" else ":"

    # 3. Build arguments
    app_name = "HuskyHailstorm"
    icon_path = os.path.join("assets", "AppLogo.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--onedir",             # or --onefile
        "--windowed",           # GUI app (no console)
        "--clean",
        "--collect-all", "customtkinter",
        f"--add-data=assets{sep}assets",
        f"--add-data=profiles{sep}profiles",
        "main.py"
    ]

    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    print("\n[Executando comando de compilação:]")
    print(" ".join(cmd))
    print("-" * 60)

    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print(" [SUCESSO] Compilação concluída!")
        out_dir = os.path.join("dist", app_name)
        print(f" Executável gerado na pasta: {out_dir}")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRO] Falha durante a compilação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
