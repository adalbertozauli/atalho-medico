from __future__ import annotations

import ctypes
from pathlib import Path
import time
from threading import Lock

from atalho_medico.utils.app_log import log_message


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_BACK = 0x08
VK_RETURN = 0x0D
VK_TAB = 0x09
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
USER32 = ctypes.WinDLL("user32", use_last_error=True)


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION),
    ]


class TextExpander:
    def __init__(self) -> None:
        self._lock = Lock()

    def expand(self, shortcut: str, text: str, terminator: str) -> None:
        with self._lock:
            log_message(f"Expandindo atalho: {shortcut!r} modo={terminator}")
            self._expand_locked(shortcut, text, terminator)

    def _expand_locked(self, shortcut: str, text: str, terminator: str) -> None:
        time.sleep(0.12 if terminator == "auto" else 0.08)

        suffix = ""
        if terminator == "space":
            suffix = " "
        elif terminator == "tab":
            suffix = "\t"
        elif terminator == "enter":
            suffix = "\n"

        target_text = text + suffix
        delete_count = len(shortcut) + (1 if suffix else 0)

        if _foreground_process_name() == "WINWORD.EXE":
            try:
                _expand_in_word(delete_count, target_text)
                return
            except Exception as exc:
                log_message(f"Falha na expansão via Word COM; usando fallback. erro={exc}")

        # Quando há terminador, o cursor está depois dele. Apagamos tudo e
        # recolocamos o terminador no final para preservar o resultado visual.
        _send_backspaces(delete_count)
        _send_text(target_text)


def _expand_in_word(delete_count: int, text: str) -> None:
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    try:
        word = win32com.client.GetActiveObject("Word.Application")
        selection = word.Selection
        for _ in range(delete_count):
            selection.TypeBackspace()
        selection.TypeText(text.replace("\r\n", "\r").replace("\n", "\r"))
        log_message("Expansão executada via Word COM.")
    finally:
        pythoncom.CoUninitialize()


def _foreground_process_name() -> str:
    hwnd = USER32.GetForegroundWindow()
    if not hwnd:
        return ""

    pid = ctypes.c_ulong()
    USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not process:
        return ""

    try:
        buffer_size = ctypes.c_ulong(260)
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        ok = kernel32.QueryFullProcessImageNameW(process, 0, buffer, ctypes.byref(buffer_size))
        if not ok:
            return ""
        return Path(buffer.value).name.upper()
    finally:
        kernel32.CloseHandle(process)


def _send_backspaces(count: int) -> None:
    for _ in range(count):
        _send_vk(VK_BACK)
        time.sleep(0.006)


def _send_text(text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for char in normalized:
        if char == "\n":
            _send_vk(VK_RETURN)
        elif char == "\t":
            _send_vk(VK_TAB)
        else:
            _send_unicode_char(char)
        time.sleep(0.001)


def _send_vk(vk_code: int) -> None:
    _send_input(KEYBDINPUT(vk_code, 0, 0, 0, 0))
    _send_input(KEYBDINPUT(vk_code, 0, KEYEVENTF_KEYUP, 0, 0))


def _send_unicode_char(char: str) -> None:
    encoded = char.encode("utf-16-le", errors="surrogatepass")
    for index in range(0, len(encoded), 2):
        scan = int.from_bytes(encoded[index : index + 2], "little")
        _send_input(KEYBDINPUT(0, scan, KEYEVENTF_UNICODE, 0, 0))
        _send_input(KEYBDINPUT(0, scan, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0))


def _send_input(keyboard_input: KEYBDINPUT) -> None:
    input_struct = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki=keyboard_input))
    sent = USER32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
    if sent != 1:
        error_code = ctypes.get_last_error()
        log_message(f"Falha SendInput. codigo={error_code}")
        raise OSError(f"O Windows não aceitou o evento de teclado simulado. Código: {error_code}")
