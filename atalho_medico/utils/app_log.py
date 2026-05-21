from __future__ import annotations

from datetime import datetime

from atalho_medico.utils.file_utils import log_data_path


def log_message(message: str) -> None:
    log_path = log_data_path()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with log_path.open("a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {message}\n")
    except OSError:
        pass
