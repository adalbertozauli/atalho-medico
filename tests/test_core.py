from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from atalho_medico.models.snippet import Snippet
from atalho_medico.services.keyboard_listener import KeyboardListener
from atalho_medico.services.snippet_store import SnippetStore
from atalho_medico.services.text_expander import TextExpander
from atalho_medico.utils.validators import ValidationError, validate_snippet


class SnippetStoreTests(unittest.TestCase):
    def test_store_loads_and_searches_snippets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snippets.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "atalho": ".ef",
                            "titulo": "Exame físico",
                            "categoria": "Exame físico",
                            "texto": "BEG.",
                            "ativo": True,
                        },
                        {
                            "atalho": "1cp8",
                            "titulo": "Tomar 8/8",
                            "categoria": "Receitas",
                            "texto": "Tomar 01 comprimido de 8/8 horas.",
                            "ativo": True,
                        },
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            store = SnippetStore(path)

            self.assertEqual(len(store.list_all()), 2)
            self.assertEqual(store.search("receitas")[0].atalho, "1cp8")
            self.assertEqual(store.get_active_by_shortcut(".ef").texto, "BEG.")

    def test_store_rejects_duplicate_shortcut_on_upsert(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snippets.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "atalho": ".ef",
                            "titulo": "Exame físico",
                            "categoria": "Exame físico",
                            "texto": "BEG.",
                            "ativo": True,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            store = SnippetStore(path)

            with self.assertRaises(ValidationError):
                store.upsert(
                    Snippet(
                        atalho=".ef",
                        titulo="Outro",
                        categoria="Exame físico",
                        texto="Outro texto",
                        ativo=True,
                    ),
                    original_atalho=".outro",
                )


class ValidatorTests(unittest.TestCase):
    def test_validator_accepts_non_dot_shortcuts(self) -> None:
        validate_snippet(
            Snippet(
                atalho="1cp8",
                titulo="Tomar 8/8",
                categoria="Receitas",
                texto="Tomar 01 comprimido de 8/8 horas.",
                ativo=True,
            )
        )

    def test_validator_rejects_shortcuts_with_spaces(self) -> None:
        with self.assertRaises(ValidationError):
            validate_snippet(
                Snippet(
                    atalho="1 cp8",
                    titulo="Tomar 8/8",
                    categoria="Receitas",
                    texto="Tomar 01 comprimido de 8/8 horas.",
                    ativo=True,
                )
            )


class KeyboardListenerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MagicMock()
        self.store.list_all.return_value = [
            Snippet(".ef", "Exame físico", "Exame físico", "BEG.", True),
            Snippet("1cp8", "Tomar 8/8", "Receitas", "Tomar 01 comprimido de 8/8 horas.", True),
            Snippet(";cnes", "CNES", "Importados", "123456", True),
            Snippet(".inativo", "Inativo", "Teste", "Não deve expandir", False),
        ]
        self.listener = KeyboardListener(self.store, MagicMock())

    def test_finds_dot_shortcut_case_insensitive(self) -> None:
        snippet = self.listener._find_matching_snippet("texto .EF")
        self.assertIsNotNone(snippet)
        self.assertEqual(snippet.atalho, ".ef")

    def test_finds_non_dot_shortcuts(self) -> None:
        self.assertEqual(self.listener._find_matching_snippet(" 1cp8").atalho, "1cp8")
        self.assertEqual(self.listener._find_matching_snippet(" ;cnes").atalho, ";cnes")

    def test_does_not_expand_inside_words(self) -> None:
        self.assertIsNone(self.listener._find_matching_snippet("abc1cp8"))

    def test_ignores_inactive_snippets(self) -> None:
        self.assertIsNone(self.listener._find_matching_snippet(".inativo"))


class TextExpanderTests(unittest.TestCase):
    def test_fallback_expansion_deletes_shortcut_and_types_text(self) -> None:
        calls: list[tuple[str, object]] = []
        with patch("atalho_medico.services.text_expander.time.sleep", lambda _seconds: None), patch(
            "atalho_medico.services.text_expander._foreground_process_name", return_value="NOTEPAD.EXE"
        ), patch("atalho_medico.services.text_expander._send_vk", lambda vk: calls.append(("vk", vk))), patch(
            "atalho_medico.services.text_expander._send_unicode_char",
            lambda char: calls.append(("char", char)),
        ):
            TextExpander().expand("1cp8", "Tomar 01 comprimido de 8/8 horas.", "auto")

        self.assertEqual(sum(1 for item in calls if item == ("vk", 8)), 4)
        typed = "".join(str(value) for kind, value in calls if kind == "char")
        self.assertEqual(typed, "Tomar 01 comprimido de 8/8 horas.")

    def test_word_expansion_uses_com_path(self) -> None:
        with patch("atalho_medico.services.text_expander.time.sleep", lambda _seconds: None), patch(
            "atalho_medico.services.text_expander._foreground_process_name", return_value="WINWORD.EXE"
        ), patch("atalho_medico.services.text_expander._expand_in_word") as expand_in_word, patch(
            "atalho_medico.services.text_expander._send_text"
        ) as send_text:
            TextExpander().expand(".ef", "BEG.\nMVF.", "auto")

        expand_in_word.assert_called_once_with(3, "BEG.\nMVF.")
        send_text.assert_not_called()

    def test_space_terminator_is_preserved_after_expansion(self) -> None:
        calls: list[tuple[str, object]] = []
        with patch("atalho_medico.services.text_expander.time.sleep", lambda _seconds: None), patch(
            "atalho_medico.services.text_expander._foreground_process_name", return_value="NOTEPAD.EXE"
        ), patch("atalho_medico.services.text_expander._send_vk", lambda vk: calls.append(("vk", vk))), patch(
            "atalho_medico.services.text_expander._send_unicode_char",
            lambda char: calls.append(("char", char)),
        ):
            TextExpander().expand(".ef", "BEG.", "space")

        self.assertEqual(sum(1 for item in calls if item == ("vk", 8)), 4)
        typed = "".join(str(value) for kind, value in calls if kind == "char")
        self.assertEqual(typed, "BEG. ")


if __name__ == "__main__":
    unittest.main()
