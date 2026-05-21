from __future__ import annotations

from collections import Counter
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from atalho_medico.models.snippet import Snippet
from atalho_medico.services.import_export import export_json, import_json
from atalho_medico.services.keyboard_listener import KeyboardListener
from atalho_medico.services.snippet_store import SnippetStore
from atalho_medico.ui.snippet_dialog import SnippetDialog
from atalho_medico.utils.app_log import log_message
from atalho_medico.utils.validators import ValidationError


class MainWindow(QMainWindow):
    show_requested = Signal()
    expansion_status_changed = Signal(bool)

    def __init__(self, store: SnippetStore, listener: KeyboardListener) -> None:
        super().__init__()
        self.store = store
        self.listener = listener
        self._force_close = False
        self.setWindowTitle("Atalho Médico")
        self.resize(1080, 680)

        title_label = QLabel("Atalho Médico")
        title_label.setObjectName("AppTitle")
        subtitle_label = QLabel("Biblioteca local de textos para prontuário, receitas e orientações")
        subtitle_label.setObjectName("AppSubtitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por atalho, título, categoria ou conteúdo")
        self.search_input.textChanged.connect(self.refresh_table)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(46)
        self.toggle_button = QPushButton("Pausar expansão")
        self.toggle_button.setFixedHeight(46)
        self.toggle_button.clicked.connect(self.toggle_expansion)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Atalho", "Título", "Categoria", "Ativo", "Texto"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.setShowGrid(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_selected)
        self.table.horizontalHeader().setFixedHeight(64)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 110)
        self.table.verticalHeader().setDefaultSectionSize(60)

        new_button = QPushButton("Novo atalho")
        new_button.setObjectName("PrimaryButton")
        new_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        new_button.clicked.connect(self.new_snippet)
        edit_button = QPushButton("Editar")
        edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        edit_button.clicked.connect(self.edit_selected)
        delete_button = QPushButton("Excluir")
        delete_button.setObjectName("DangerButton")
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_button.clicked.connect(self.delete_selected)
        import_button = QPushButton("Importar JSON")
        import_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        import_button.clicked.connect(self.import_library)
        export_button = QPushButton("Exportar JSON")
        export_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        export_button.clicked.connect(self.export_library)

        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(2)

        top_layout = QHBoxLayout()
        top_layout.addLayout(title_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.status_label)
        top_layout.addWidget(self.toggle_button)
        top_layout.setSpacing(12)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addWidget(new_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input, 1)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_container = QWidget()
        search_container.setObjectName("SearchBar")
        search_container.setLayout(search_layout)

        action_container = QWidget()
        action_container.setObjectName("ActionBar")
        action_container.setLayout(button_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)
        layout.addLayout(top_layout)
        layout.addWidget(search_container)
        layout.addWidget(self.table, 1)
        layout.addWidget(action_container)

        container = QWidget()
        container.setObjectName("MainSurface")
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.show_requested.connect(self._show_from_tray)
        self.expansion_status_changed.connect(self.set_expansion_status)
        self.set_expansion_status(self.listener.enabled)
        QTimer.singleShot(0, self.refresh_table)

    def refresh_table(self) -> None:
        snippets = self.store.search(self.search_input.text())
        shortcut_counts = Counter(snippet.atalho for snippet in self.store.list_all())
        self.table.setRowCount(len(snippets))
        for row, snippet in enumerate(snippets):
            is_duplicate = shortcut_counts[snippet.atalho] > 1
            values = [
                snippet.atalho,
                snippet.titulo,
                snippet.categoria,
                "",
                snippet.texto,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, snippet.atalho)
                item.setForeground(Qt.black)
                if col in {0, 3}:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if is_duplicate and col == 0:
                    item.setBackground(QBrush(QColor("#ffe1e1")))
                    item.setForeground(QBrush(QColor("#9f1d1d")))
                    item.setToolTip("Atalho duplicado. Dois ou mais textos usam este mesmo atalho.")
                self.table.setItem(row, col, item)
            pill = QLabel("Ativo" if snippet.ativo else "Pausado")
            pill.setObjectName("ActivePill" if snippet.ativo else "InactivePill")
            pill.setAlignment(Qt.AlignCenter)
            pill_container = QWidget()
            pill_container.setObjectName("PillContainer")
            pill_layout = QHBoxLayout(pill_container)
            pill_layout.setContentsMargins(0, 0, 0, 0)
            pill_layout.addWidget(pill)
            pill_layout.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 3, pill_container)
        self.table.clearSelection()

    def set_expansion_status(self, enabled: bool) -> None:
        if enabled:
            self.status_label.setText("Expansão ativa")
            self.status_label.setObjectName("StatusActive")
            self.toggle_button.setText("Pausar expansão")
        else:
            self.status_label.setText("Expansão pausada")
            self.status_label.setObjectName("StatusPaused")
            self.toggle_button.setText("Ativar expansão")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def toggle_expansion(self) -> None:
        self.listener.toggle_enabled()

    def new_snippet(self) -> None:
        dialog = SnippetDialog(self)
        if dialog.exec():
            try:
                self.store.upsert(dialog.snippet())
            except ValidationError as exc:
                QMessageBox.warning(self, "Não foi possível salvar", str(exc))
                return
            self.refresh_table()

    def edit_selected(self) -> None:
        snippet = self._selected_snippet()
        if snippet is None:
            QMessageBox.information(self, "Selecione um atalho", "Escolha um atalho para editar.")
            return
        dialog = SnippetDialog(self, snippet)
        if dialog.exec():
            try:
                self.store.upsert(dialog.snippet(), original_atalho=snippet.atalho)
            except ValidationError as exc:
                QMessageBox.warning(self, "Não foi possível salvar", str(exc))
                return
            self.refresh_table()

    def delete_selected(self) -> None:
        snippet = self._selected_snippet()
        if snippet is None:
            QMessageBox.information(self, "Selecione um atalho", "Escolha um atalho para excluir.")
            return
        answer = QMessageBox.question(
            self,
            "Excluir atalho",
            f"Excluir o atalho {snippet.atalho}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.store.delete(snippet.atalho)
            self.refresh_table()

    def import_library(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Importar JSON", "", "JSON (*.json)")
        if not file_name:
            return
        try:
            count = import_json(Path(file_name), self.store)
        except ValidationError as exc:
            QMessageBox.warning(self, "Importação não concluída", str(exc))
            return
        self.refresh_table()
        QMessageBox.information(self, "Importação concluída", f"{count} atalhos importados.")

    def export_library(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar JSON", "atalhos_medicos.json", "JSON (*.json)")
        if not file_name:
            return
        try:
            count = export_json(Path(file_name), self.store)
        except OSError:
            QMessageBox.warning(self, "Exportação não concluída", "Não foi possível salvar o arquivo.")
            return
        QMessageBox.information(self, "Exportação concluída", f"{count} atalhos exportados.")

    def closeEvent(self, event) -> None:
        if self._force_close:
            log_message("Janela fechada sem confirmação.")
            self.listener.stop()
            event.accept()
            return

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Fechar Atalho Médico")
        dialog.setIcon(QMessageBox.Question)
        dialog.setText("O que deseja fazer?")
        dialog.setInformativeText(
            "Se enviar para a bandeja, o aplicativo continuará rodando e a expansão seguirá ativa."
        )

        tray_button = dialog.addButton("Enviar para bandeja", QMessageBox.AcceptRole)
        close_button = dialog.addButton("Fechar aplicativo", QMessageBox.DestructiveRole)
        cancel_button = dialog.addButton("Cancelar", QMessageBox.RejectRole)
        dialog.setDefaultButton(tray_button)
        dialog.exec()

        clicked_button = dialog.clickedButton()
        if clicked_button == tray_button:
            log_message("Janela enviada para a bandeja pelo botão X.")
            event.ignore()
            self.hide()
            return
        if clicked_button == close_button:
            log_message("Aplicativo fechado pelo botão X.")
            self.listener.stop()
            event.accept()
            QApplication.instance().quit()
            return

        if clicked_button == cancel_button:
            log_message("Fechamento cancelado pelo usuário.")
        event.ignore()

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _selected_snippet(self) -> Snippet | None:
        selected = self.table.selectedItems()
        if not selected:
            return None
        atalho = selected[0].data(Qt.UserRole)
        for snippet in self.store.list_all():
            if snippet.atalho == atalho:
                return snippet
        return None
