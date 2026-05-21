from __future__ import annotations

import ctypes
import os
import sys

os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.window=false")

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

from atalho_medico.services.keyboard_listener import KeyboardListener
from atalho_medico.services.snippet_store import SnippetStore
from atalho_medico.services.text_expander import TextExpander
from atalho_medico.services.tray_service import TrayService
from atalho_medico.ui.main_window import MainWindow
from atalho_medico.ui.styles import APP_STYLE
from atalho_medico.utils.file_utils import snippets_data_path
from atalho_medico.utils.app_log import log_message


ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\AtalhoMedicoSingleInstance"
_MUTEX_HANDLE = None


class AppBridge(QObject):
    quit_requested = Signal()


def acquire_single_instance() -> bool:
    global _MUTEX_HANDLE
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _MUTEX_HANDLE = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not _MUTEX_HANDLE:
        log_message("Não foi possível criar mutex de instância única.")
        return True
    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        ctypes.windll.user32.MessageBoxW(
            None,
            "O Atalho Médico já está aberto. Feche a instância atual antes de abrir outra.",
            "Atalho Médico",
            0x40,
        )
        return False
    return True


def main() -> int:
    if not acquire_single_instance():
        return 0

    log_message(f"Aplicativo iniciado. pid={os.getpid()}")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(APP_STYLE)
    bridge = AppBridge()

    store = SnippetStore(snippets_data_path())
    expander = TextExpander()
    listener = KeyboardListener(store, expander)
    window = MainWindow(store, listener)
    listener.status_callback = window.expansion_status_changed.emit

    def show_window() -> None:
        window.show_requested.emit()

    def toggle_expansion() -> bool:
        return listener.toggle_enabled()

    def quit_app() -> None:
        log_message("Aplicativo encerrando.")
        tray.stop()
        listener.stop()
        app.quit()

    bridge.quit_requested.connect(quit_app)

    tray = TrayService(show_window, toggle_expansion, bridge.quit_requested.emit)

    try:
        listener.start()
    except Exception as exc:
        QMessageBox.warning(
            window,
            "Captura global indisponível",
            "Não foi possível iniciar a captura global do teclado. "
            "No Windows, execute o aplicativo normalmente ou como administrador se necessário.\n\n"
            f"Detalhe: {exc}",
        )

    tray.start()
    window.show()

    app.aboutToQuit.connect(listener.stop)
    app.aboutToQuit.connect(tray.stop)
    app.aboutToQuit.connect(lambda: log_message("Evento aboutToQuit recebido."))

    # Mantém o loop do Qt responsivo enquanto serviços de fundo estão ativos.
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
