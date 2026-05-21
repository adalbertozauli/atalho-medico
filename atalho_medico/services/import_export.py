from __future__ import annotations

import json
from pathlib import Path

from atalho_medico.models.snippet import Snippet
from atalho_medico.services.snippet_store import SnippetStore
from atalho_medico.utils.validators import ValidationError, validate_snippet


def import_json(path: Path, store: SnippetStore) -> int:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValidationError("Não foi possível ler o arquivo selecionado.") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError("O arquivo selecionado não contém JSON válido.") from exc

    if not isinstance(raw, list):
        raise ValidationError("O JSON importado deve conter uma lista de atalhos.")

    snippets = [Snippet.from_dict(item) for item in raw if isinstance(item, dict)]
    for snippet in snippets:
        validate_snippet(snippet)

    store.replace_all(snippets)
    return len(snippets)


def export_json(path: Path, store: SnippetStore) -> int:
    snippets = store.list_all()
    path.write_text(
        json.dumps([snippet.to_dict() for snippet in snippets], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(snippets)
