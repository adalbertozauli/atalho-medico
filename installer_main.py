from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import winreg
from pathlib import Path


APP_NAME = "Atalho Médico"
APP_VERSION = "0.1.0"
APP_EXE = "AtalhoMedico.exe"


def resource_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / name
    return Path(__file__).resolve().parent / name


def message(text: str, title: str = APP_NAME) -> None:
    ctypes.windll.user32.MessageBoxW(None, text, title, 0x40)


def create_shortcut(
    shortcut_path: Path,
    target: Path,
    working_dir: Path,
    arguments: str = "",
) -> None:
    command = (
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($args[0]);"
        "$s.TargetPath=$args[1];"
        "$s.WorkingDirectory=$args[2];"
        "$s.Arguments=$args[3];"
        "$s.IconLocation=$args[4];"
        "$s.Save()"
    )
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
            str(shortcut_path),
            str(target),
            str(working_dir),
            arguments,
            str(target),
        ],
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def write_uninstaller(install_dir: Path) -> Path:
    script = install_dir / "uninstall.ps1"
    script.write_text(
        f"""$ErrorActionPreference = "SilentlyContinue"
$InstallDir = "{install_dir}"
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\\Windows\\Start Menu\\Programs\\Atalho Médico"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Atalho Médico.lnk"
$RegPath = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AtalhoMedico"
Get-Process -Name "AtalhoMedico" | Stop-Process -Force
Remove-Item $DesktopShortcut -Force
Remove-Item $StartMenuDir -Recurse -Force
Remove-Item $RegPath -Recurse -Force
Remove-Item $InstallDir -Recurse -Force
""",
        encoding="utf-8",
    )
    return script


def register_uninstall(install_dir: Path, exe_path: Path, uninstall_script: Path) -> None:
    uninstall_cmd = (
        f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{uninstall_script}"'
    )
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\AtalhoMedico"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(exe_path))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)


def install() -> None:
    install_dir = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "AtalhoMedico"
    start_menu_dir = (
        Path(os.environ["APPDATA"])
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / APP_NAME
    )
    desktop_shortcut = Path.home() / "Desktop" / f"{APP_NAME}.lnk"
    exe_path = install_dir / APP_EXE

    install_dir.mkdir(parents=True, exist_ok=True)
    start_menu_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(resource_path(APP_EXE), exe_path)
    readme_source = resource_path("README.md")
    if readme_source.exists():
        shutil.copyfile(readme_source, install_dir / "README.md")

    uninstall_script = write_uninstaller(install_dir)
    create_shortcut(start_menu_dir / f"{APP_NAME}.lnk", exe_path, install_dir)
    create_shortcut(desktop_shortcut, exe_path, install_dir)
    create_shortcut(
        start_menu_dir / f"Desinstalar {APP_NAME}.lnk",
        Path("powershell.exe"),
        install_dir,
        f'-NoProfile -ExecutionPolicy Bypass -File "{uninstall_script}"',
    )
    register_uninstall(install_dir, exe_path, uninstall_script)

    subprocess.Popen([str(exe_path)], cwd=str(install_dir))
    message("Atalho Médico foi instalado com sucesso.")


if __name__ == "__main__":
    try:
        install()
    except Exception as exc:
        ctypes.windll.user32.MessageBoxW(
            None,
            f"Não foi possível instalar o Atalho Médico.\n\nDetalhe: {exc}",
            APP_NAME,
            0x10,
        )
        raise
