from __future__ import annotations

import threading
from typing import Callable

import pystray
from PIL import Image, ImageDraw


class TrayService:
    def __init__(
        self,
        show_callback: Callable[[], None],
        toggle_callback: Callable[[], bool],
        quit_callback: Callable[[], None],
    ) -> None:
        self.show_callback = show_callback
        self.toggle_callback = toggle_callback
        self.quit_callback = quit_callback
        self.icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self.icon is not None:
            return
        self.icon = pystray.Icon(
            "atalho_medico",
            self._create_icon(),
            "Atalho Médico",
            menu=pystray.Menu(
                pystray.MenuItem("Abrir", lambda: self.show_callback(), default=True),
                pystray.MenuItem("Ativar/pausar expansão", lambda: self.toggle_callback()),
                pystray.MenuItem("Sair", lambda: self.quit_callback()),
            ),
        )
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None

    @staticmethod
    def _create_icon() -> Image.Image:
        image = Image.new("RGBA", (64, 64), (22, 96, 122, 255))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 56, 56), radius=10, fill=(245, 250, 252, 255))
        draw.rectangle((18, 28, 46, 36), fill=(22, 96, 122, 255))
        draw.rectangle((28, 18, 36, 46), fill=(22, 96, 122, 255))
        return image
