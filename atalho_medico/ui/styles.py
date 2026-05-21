APP_STYLE = """
QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
    color: #172126;
}
QMainWindow {
    background: #5f6b72;
}
QDialog {
    background: #5f6b72;
}
QLabel {
    color: #172126;
}
QLabel#AppTitle {
    color: white;
    font-size: 22pt;
    font-weight: 500;
}
QLabel#AppSubtitle {
    color: #dce4e7;
    font-size: 10pt;
}
QWidget#MainSurface {
    background: #5f6b72;
}
QWidget#SearchBar,
QWidget#ActionBar {
    background: transparent;
}
QLineEdit, QTextEdit, QComboBox {
    background: #eef3f4;
    color: #172126;
    border: 1px solid #d7e0e3;
    border-radius: 14px;
    padding: 10px 12px;
    selection-background-color: #fff200;
    selection-color: #172126;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #fff200;
    background: white;
}
QComboBox::drop-down {
    width: 34px;
    border: none;
}
QComboBox QAbstractItemView {
    background: #eef3f4;
    color: #172126;
    border: 1px solid #d7e0e3;
    selection-background-color: #fff200;
    selection-color: #172126;
    padding: 6px;
    outline: 0;
}
QCheckBox {
    color: #eef3f4;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QTableWidget {
    background: #eef3f4;
    alternate-background-color: #f6fafa;
    color: #172126;
    border: none;
    border-radius: 18px;
    gridline-color: transparent;
    selection-background-color: #dbe5e8;
    selection-color: #172126;
    padding: 0;
}
QTableWidget::item {
    color: #172126;
    padding: 12px 14px;
    border: none;
    border-bottom: 1px solid #d9e3e6;
}
QTableWidget::item:selected {
    background: #dbe5e8;
    color: #172126;
}
QTableWidget::item:selected:active {
    background: #dbe5e8;
    color: #172126;
}
QHeaderView::section {
    background: #d7e2e5;
    color: #172126;
    border: 0;
    border-bottom: 1px solid #cbd8dc;
    padding: 14px;
    font-weight: 600;
}
QTableCornerButton::section {
    background: #d7e2e5;
    border: none;
}
QTableWidget QScrollBar:vertical,
QTableWidget QScrollBar:horizontal {
    background: transparent;
    width: 0;
    height: 0;
    border: none;
}
QLabel#ActivePill {
    background: #fff200;
    color: #172126;
    border-radius: 13px;
    padding: 0;
    font-weight: 700;
    min-width: 74px;
    max-width: 74px;
    min-height: 26px;
    max-height: 26px;
}
QLabel#InactivePill {
    background: #d2dade;
    color: #56636b;
    border-radius: 13px;
    padding: 0;
    font-weight: 700;
    min-width: 74px;
    max-width: 74px;
    min-height: 26px;
    max-height: 26px;
}
QWidget#PillContainer {
    background: transparent;
}
QPushButton {
    background: #2f3a43;
    color: white;
    border: none;
    border-radius: 18px;
    padding: 0 18px;
    font-weight: 600;
    min-height: 46px;
    max-height: 46px;
    min-width: 94px;
}
QPushButton:hover {
    background: #222c34;
}
QPushButton#PrimaryButton {
    background: #fff200;
    color: #172126;
}
QPushButton#PrimaryButton:hover {
    background: #f1e500;
}
QPushButton#DangerButton {
    background: #46515a;
}
QPushButton#DangerButton:hover {
    background: #34404a;
}
QPushButton:disabled {
    background: #9da9ae;
}
QLabel#StatusActive {
    background: #fff200;
    color: #172126;
    font-weight: 700;
    border-radius: 18px;
    padding: 0 18px;
    min-height: 46px;
    max-height: 46px;
    min-width: 120px;
}
QLabel#StatusPaused {
    background: #e8eef0;
    color: #4a545b;
    font-weight: 700;
    border-radius: 18px;
    padding: 0 18px;
    min-height: 46px;
    max-height: 46px;
    min-width: 120px;
}
QDialog QLabel {
    color: #eef3f4;
    font-weight: 600;
}
QDialogButtonBox QPushButton {
    min-width: 92px;
}
"""
