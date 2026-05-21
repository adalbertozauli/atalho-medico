from __future__ import annotations

from collections import deque
from threading import RLock, Thread
from typing import Callable

import keyboard

from atalho_medico.models.snippet import Snippet
from atalho_medico.services.snippet_store import SnippetStore
from atalho_medico.services.text_expander import TextExpander
from atalho_medico.utils.app_log import log_message


class KeyboardListener:
    def __init__(
        self,
        store: SnippetStore,
        expander: TextExpander,
        status_callback: Callable[[bool], None] | None = None,
    ) -> None:
        self.store = store
        self.expander = expander
        self.status_callback = status_callback
        self._buffer: deque[str] = deque(maxlen=50)
        self._lock = RLock()
        self._enabled = True
        self._hook = None
        self._is_expanding = False

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def start(self) -> None:
        if self._hook is None:
            self._hook = keyboard.on_release(self._on_key_release)

    def stop(self) -> None:
        if self._hook is not None:
            keyboard.unhook(self._hook)
            self._hook = None

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._enabled = enabled
            self._buffer.clear()
        if self.status_callback:
            self.status_callback(enabled)

    def toggle_enabled(self) -> bool:
        self.set_enabled(not self.enabled)
        return self.enabled

    def _on_key_release(self, event: keyboard.KeyboardEvent) -> None:
        if self._is_expanding or not self.enabled:
            return

        key = event.name or ""
        if key in {"space", "enter", "tab"}:
            self._try_expand(key)
            return

        char = self._key_to_char(key)
        with self._lock:
            if char is None:
                if key in {"backspace", "delete", "esc"}:
                    self._buffer.clear()
                return
            self._buffer.append(char)
        self._try_expand("auto")

    def _try_expand(self, terminator: str) -> None:
        with self._lock:
            text = "".join(self._buffer)
        snippet = self._find_matching_snippet(text)
        if snippet is None:
            with self._lock:
                if terminator == "space":
                    self._buffer.append(" ")
                elif terminator != "auto":
                    self._buffer.clear()
            return

        with self._lock:
            self._buffer.clear()
        self._is_expanding = True
        Thread(
            target=self._expand_in_background,
            args=(snippet.atalho, snippet.texto, terminator),
            daemon=True,
        ).start()

    def _expand_in_background(self, shortcut: str, text: str, terminator: str) -> None:
        try:
            self.expander.expand(shortcut, text, terminator)
        except Exception as exc:
            log_message(f"Erro ao expandir {shortcut!r}: {exc}")
        finally:
            self._is_expanding = False

    def _find_matching_snippet(self, text: str) -> Snippet | None:
        snippets = sorted(
            (snippet for snippet in self.store.list_all() if snippet.ativo),
            key=lambda snippet: len(snippet.atalho),
            reverse=True,
        )
        normalized_text = text.casefold()
        for snippet in snippets:
            shortcut = snippet.atalho
            normalized_shortcut = shortcut.casefold()
            if not normalized_text.endswith(normalized_shortcut):
                continue
            start = len(text) - len(shortcut)
            if start == 0 or not text[start - 1].isalnum():
                return snippet
        return None

    @staticmethod
    def _key_to_char(key: str) -> str | None:
        if len(key) == 1:
            return key
        aliases = {
            "decimal": ".",
            "comma": ",",
            "minus": "-",
            "plus": "+",
        }
        return aliases.get(key)
