from __future__ import annotations

import re

from atalho_medico.models.snippet import Snippet


SHORTCUT_PATTERN = re.compile(r"^[^\s]{1,30}$")


class ValidationError(ValueError):
    pass


def validate_snippet(snippet: Snippet) -> None:
    if not snippet.atalho:
        raise ValidationError("Informe o atalho.")
    if not SHORTCUT_PATTERN.match(snippet.atalho):
        raise ValidationError("O atalho não pode conter espaços e deve ter até 30 caracteres.")
    if not snippet.titulo:
        raise ValidationError("Informe o título.")
    if not snippet.categoria:
        raise ValidationError("Informe a categoria.")
    if not snippet.texto.strip():
        raise ValidationError("Informe o texto expandido.")
