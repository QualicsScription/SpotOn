# Main/src/ui/title_bar.py
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from ..resources.colors import TITLE_BAR_COLOR, BUTTON_COLOR, TEXT_COLOR

class TitleBar(QFrame):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(f"background-color: {TITLE_BAR_COLOR};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: {TITLE_BAR_COLOR};")
        layout.addWidget(self.title_label)

        layout.addStretch()

        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        minimize_btn.clicked.connect(parent.showMinimized)
        layout.addWidget(minimize_btn)

        maximize_btn = QPushButton("□")
        maximize_btn.setFixedSize(30, 30)
        maximize_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        maximize_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(maximize_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"background-color: #ff5555; color: {TEXT_COLOR};")
        close_btn.clicked.connect(parent.close)
        layout.addWidget(close_btn)

        self.start = None
        self.setMouseTracking(True)
        self.title_label.setMouseTracking(True)

    def toggle_maximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.globalPos() - self.parent().pos()

    def mouseMoveEvent(self, event):
        if self.start is not None:
            self.parent().move(event.globalPos() - self.start)

    def mouseReleaseEvent(self, event):
        self.start = None