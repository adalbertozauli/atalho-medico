from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from atalho_medico.models.snippet import Snippet
from atalho_medico.utils.validators import ValidationError, validate_snippet


INITIAL_CATEGORIES = [
    "Exame físico",
    "HAS",
    "Diabetes",
    "Orientações",
    "Encaminhamentos",
    "Receitas",
    "Pediatria",
    "Saúde mental",
    "Ginecologia",
    "Atestados e declarações",
]


class SnippetDialog(QDialog):
    def __init__(self, parent=None, snippet: Snippet | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Atalho")
        self.setMinimumWidth(520)
        self.setMinimumHeight(430)

        self.shortcut_input = QLineEdit()
        self.shortcut_input.setPlaceholderText(".rcr")

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ritmo cardíaco regular")

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(INITIAL_CATEGORIES)

        self.text_input = QTextEdit()
        self.text_input.setMinimumHeight(150)

        self.active_input = QCheckBox("Ativo")
        self.active_input.setChecked(True)

        form = QFormLayout()
        form.addRow("Atalho", self.shortcut_input)
        form.addRow("Título", self.title_input)
        form.addRow("Categoria", self.category_input)
        form.addRow("Texto expandido", self.text_input)
        form.addRow("", self.active_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Salvar")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancelar")
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if snippet:
            self.shortcut_input.setText(snippet.atalho)
            self.title_input.setText(snippet.titulo)
            self.category_input.setCurrentText(snippet.categoria)
            self.text_input.setPlainText(snippet.texto)
            self.active_input.setChecked(snippet.ativo)

    def snippet(self) -> Snippet:
        return Snippet(
            atalho=self.shortcut_input.text().strip(),
            titulo=self.title_input.text().strip(),
            categoria=self.category_input.currentText().strip(),
            texto=self.text_input.toPlainText(),
            ativo=self.active_input.isChecked(),
        )

    def _accept_if_valid(self) -> None:
        try:
            validate_snippet(self.snippet())
        except ValidationError as exc:
            QMessageBox.warning(self, "Verifique os dados", str(exc))
            return
        self.accept()
