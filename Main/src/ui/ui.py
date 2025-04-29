# Main/src/ui/ui.py
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog
)
from PyQt5.QtCore import Qt
from ..core.comparator import FileComparator
from ..core.utils import get_file_info
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR
from .title_bar import TitleBar
from .table_view import TableView
from .visual_analysis import VisualAnalysis
from .detailed_analysis import DetailedAnalysis
from languages.languages import LanguageManager

class ModernFileComparator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_manager = LanguageManager()
        self.comparator = FileComparator()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.title_bar = TitleBar(self, self.language_manager.translate("app_title"))
        self.layout.addWidget(self.title_bar)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.content_widget)

        self.button_layout = QHBoxLayout()
        self.select_button_1 = QPushButton(self.language_manager.translate("select_file_1"))
        self.select_button_1.setStyleSheet(f"background-color: {BUTTON_COLOR};")
        self.select_button_1.clicked.connect(self.select_file_1)
        self.button_layout.addWidget(self.select_button_1)

        self.select_button_2 = QPushButton(self.language_manager.translate("select_file_2"))
        self.select_button_2.setStyleSheet(f"background-color: {BUTTON_COLOR};")
        self.select_button_2.clicked.connect(self.select_file_2)
        self.button_layout.addWidget(self.select_button_2)

        self.compare_button = QPushButton(self.language_manager.translate("compare"))
        self.compare_button.setStyleSheet(f"background-color: {BUTTON_COLOR};")
        self.compare_button.clicked.connect(self.compare_files)
        self.button_layout.addWidget(self.compare_button)

        self.content_layout.addLayout(self.button_layout)

        self.file_info_1 = QLabel(self.language_manager.translate("no_file_selected"))
        self.file_info_1.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.file_info_1)

        self.file_info_2 = QLabel(self.language_manager.translate("no_file_selected"))
        self.file_info_2.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.file_info_2)

        self.table_view = TableView(self)
        self.content_layout.addWidget(self.table_view)

        self.visual_analysis = VisualAnalysis(self)
        self.content_layout.addWidget(self.visual_analysis)

        self.detailed_analysis = DetailedAnalysis(self)
        self.content_layout.addWidget(self.detailed_analysis)

        self.file_path_1 = None
        self.file_path_2 = None

        self.setGeometry(100, 100, 800, 600)

    def select_file_1(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.language_manager.translate("select_file_1"))
        if file_path:
            self.file_path_1 = file_path
            self.file_info_1.setText(get_file_info(file_path))

    def select_file_2(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.language_manager.translate("select_file_2"))
        if file_path:
            self.file_path_2 = file_path
            self.file_info_2.setText(get_file_info(file_path))

    def compare_files(self):
        if not self.file_path_1 or not self.file_path_2:
            return

        result = self.comparator.compare_files(self.file_path_1, self.file_path_2)
        self.table_view.update_table(result)
        self.visual_analysis.update_visualization(result)
        self.detailed_analysis.update_analysis(result)