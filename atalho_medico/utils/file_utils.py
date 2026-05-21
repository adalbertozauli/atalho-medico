from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def app_root() -> Path:
    return Path(__file__).resolve().parents[2]


def bundled_resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")).joinpath(*parts)
    return app_root().joinpath(*parts)


def user_data_dir() -> Path:
    candidates = [
        Path(os.environ["APPDATA"]) if os.environ.get("APPDATA") else None,
        Path(os.environ["LOCALAPPDATA"]) if os.environ.get("LOCALAPPDATA") else None,
        Path.home() / "AtalhoMedicoData",
        app_root() / "user_data",
    ]
    for base in candidates:
        if base is None:
            continue
        path = base / "AtalhoMedico"
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except OSError:
            continue
    raise OSError("Não foi possível criar a pasta de dados do Atalho Médico.")


def snippets_data_path() -> Path:
    target = user_data_dir() / "snippets.json"
    if not target.exists():
        source = bundled_resource_path("atalho_medico", "data", "snippets.json")
        if source.exists():
            shutil.copyfile(source, target)
        else:
            target.write_text("[]", encoding="utf-8")
    return target


def log_data_path() -> Path:
    return user_data_dir() / "atalho_medico.log"
