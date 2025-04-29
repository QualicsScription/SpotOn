# Main/src/ui/title_bar.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from ..resources.colors import TITLE_BAR_COLOR, BUTTON_COLOR, TEXT_COLOR

class TitleBar(QWidget):
    def __init__(self, parent, title="SpotOn"):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(f"background-color: {TITLE_BAR_COLOR};")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {TEXT_COLOR};")
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(40, 40)
        self.minimize_button.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        self.minimize_button.clicked.connect(parent.showMinimized)
        layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton("□")
        self.maximize_button.setFixedSize(40, 40)
        self.maximize_button.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_button)

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(40, 40)
        self.close_button.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        self.close_button.clicked.connect(parent.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        self.start = None
        self.is_maximized = False

    def toggle_maximize(self):
        if self.is_maximized:
            self.parent().showNormal()
            self.is_maximized = False
            self.maximize_button.setText("□")
        else:
            self.parent().showMaximized()
            self.is_maximized = True
            self.maximize_button.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.globalPos() - self.parent().pos()

    def mouseMoveEvent(self, event):
        if self.start is not None:
            self.parent().move(event.globalPos() - self.start)