# Main/src/ui/detailed_analysis.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ..core.utils import get_file_info
from ..languages.languages import LanguageManager

class DetailedAnalysis(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        file1_layout = QHBoxLayout()
        file1_layout.addWidget(QLabel(self.language_manager.translate("file1_label")))
        self.file1_info = QLabel("")
        file1_layout.addWidget(self.file1_info)
        layout.addLayout(file1_layout)

        file2_layout = QHBoxLayout()
        file2_layout.addWidget(QLabel(self.language_manager.translate("file2_label")))
        self.file2_info = QLabel("")
        file2_layout.addWidget(self.file2_info)
        layout.addLayout(file2_layout)

        self.setLayout(layout)

    def update_analysis(self, result):
        file1_path = result.get("file1_path", "")
        file2_path = result.get("file2_path", "")
        self.file1_info.setText(get_file_info(file1_path))
        self.file2_info.setText(get_file_info(file2_path))