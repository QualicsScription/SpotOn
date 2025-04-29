# Main/src/ui/title_bar.py
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from ..resources.colors import TITLE_BAR_COLOR, BUTTON_COLOR, TEXT_COLOR

class TitleBar(QFrame):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.parent = parent
        self.lang = lang  # Dil yöneticisi
        self.setStyleSheet(f"background-color: {TITLE_BAR_COLOR};")
        self.setFixedHeight(30)

        # Layout oluşturma
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)

        # Başlık etiketi oluşturma
        self.title_label = QLabel(self.lang.translate("app_title"))
        self.title_label.setStyleSheet(f"color: {TEXT_COLOR};")
        layout.addWidget(self.title_label)

        # Sağ tarafa diğer widget'ları itmek için boşluk ekleme
        layout.addStretch()

        # Dil seçimi için combo box
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Türkçe", "English"])
        self.lang_combo.setCurrentText("Türkçe" if self.lang.current_lang == "tr" else "English")
        self.lang_combo.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 5px;")
        self.lang_combo.currentTextChanged.connect(self.parent.change_language)
        layout.addWidget(self.lang_combo)

        # Pencere kontrol butonları
        for text, func, color in [
            ("─", self.parent.showMinimized, BUTTON_COLOR),
            ("□", self.parent.toggle_maximize, BUTTON_COLOR),
            ("✕", self.parent.close, "#ff5555")
        ]:
            btn = QPushButton(text)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color}; color: {TEXT_COLOR}; border: none;")
            btn.clicked.connect(func)
            layout.addWidget(btn)

        self.is_dragging = False
        self.drag_position = None

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.parent.pos()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.parent.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False