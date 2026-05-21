from __future__ import annotations

import json
from pathlib import Path
from threading import RLock

from atalho_medico.models.snippet import Snippet
from atalho_medico.utils.file_utils import ensure_parent_dir
from atalho_medico.utils.validators import ValidationError, validate_snippet


class SnippetStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = RLock()
        ensure_parent_dir(self.path)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def list_all(self) -> list[Snippet]:
        with self._lock:
            return self._load()

    def search(self, term: str) -> list[Snippet]:
        term = term.strip().lower()
        snippets = self.list_all()
        if not term:
            return snippets
        return [
            snippet
            for snippet in snippets
            if term in snippet.atalho.lower()
            or term in snippet.titulo.lower()
            or term in snippet.categoria.lower()
            or term in snippet.texto.lower()
        ]

    def get_active_by_shortcut(self, atalho: str) -> Snippet | None:
        atalho = atalho.strip()
        for snippet in self.list_all():
            if snippet.ativo and snippet.atalho == atalho:
                return snippet
        return None

    def upsert(self, snippet: Snippet, original_atalho: str | None = None) -> None:
        validate_snippet(snippet)
        with self._lock:
            snippets = self._load()
            original_atalho = original_atalho or snippet.atalho
            duplicate = any(
                item.atalho == snippet.atalho and item.atalho != original_atalho
                for item in snippets
            )
            if duplicate:
                raise ValidationError("Já existe um atalho cadastrado com esse nome.")

            replaced = False
            updated: list[Snippet] = []
            for item in snippets:
                if item.atalho == original_atalho:
                    updated.append(snippet)
                    replaced = True
                else:
                    updated.append(item)
            if not replaced:
                updated.append(snippet)
            self._save(updated)

    def delete(self, atalho: str) -> None:
        with self._lock:
            snippets = [item for item in self._load() if item.atalho != atalho]
            self._save(snippets)

    def replace_all(self, snippets: list[Snippet]) -> None:
        seen: set[str] = set()
        for snippet in snippets:
            validate_snippet(snippet)
            if snippet.atalho in seen:
                raise ValidationError(f"Atalho duplicado no arquivo: {snippet.atalho}")
            seen.add(snippet.atalho)
        with self._lock:
            self._save(snippets)

    def _load(self) -> list[Snippet]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError("O arquivo local de atalhos está com JSON inválido.") from exc
        if not isinstance(raw, list):
            raise ValidationError("O arquivo de atalhos deve conter uma lista.")
        return [Snippet.from_dict(item) for item in raw if isinstance(item, dict)]

    def _save(self, snippets: list[Snippet]) -> None:
        data = [snippet.to_dict() for snippet in sorted(snippets, key=lambda item: item.atalho)]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
