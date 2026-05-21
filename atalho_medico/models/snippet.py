from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Snippet:
    atalho: str
    titulo: str
    categoria: str
    texto: str
    ativo: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "Snippet":
        return cls(
            atalho=str(data.get("atalho", "")).strip(),
            titulo=str(data.get("titulo", "")).strip(),
            categoria=str(data.get("categoria", "")).strip(),
            texto=str(data.get("texto", "")),
            ativo=bool(data.get("ativo", True)),
        )

    def to_dict(self) -> dict:
        return {
            "atalho": self.atalho,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "texto": self.texto,
            "ativo": self.ativo,
        }
