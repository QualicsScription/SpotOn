# Main/src/ui/ui.py
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QProgressBar, QTabWidget, QFileDialog, QMessageBox, QRadioButton, QFrame, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import os
from .title_bar import TitleBar
from .table_view import TableView
from .visual_analysis import VisualAnalysis
from .detailed_analysis import DetailedAnalysis
from ..core.comparator import FileComparator  # FileComparator sınıfı eklendi
from ..languages.languages import LanguageManager  # Dil desteği için eklendi
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR, ACCENT_COLOR

__version__ = "2.0.0"

class ComparisonThread(QThread):
    progress = pyqtSignal(float, int, int)
    result = pyqtSignal(list)
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, folder, file_type, min_similarity, comparator):
        super().__init__()
        self.folder = folder
        self.file_type = file_type
        self.min_similarity = min_similarity
        self.comparator = comparator
        self.is_running = True

    def run(self):
        try:
            extensions = self.comparator.supported_extensions[self.file_type]
            all_files = [
                os.path.join(self.folder, f) for f in os.listdir(self.folder)
                if os.path.isfile(os.path.join(self.folder, f)) and
                (not extensions or os.path.splitext(f)[1].lower() in extensions)
            ]
            total_comparisons = len(all_files) * (len(all_files) - 1) // 2
            processed = 0
            results = []

            for i in range(len(all_files)):
                if not self.is_running:
                    break
                for j in range(i + 1, len(all_files)):
                    if not self.is_running:
                        break
                    result = self.comparator.compare_files(all_files[i], all_files[j])
                    if result['total'] >= self.min_similarity:
                        results.append(result)
                    processed += 1
                    progress_value = (processed / total_comparisons) * 100 if total_comparisons > 0 else 0
                    self.progress.emit(progress_value, processed, total_comparisons)
            self.result.emit(results)
            self.status.emit("Completed!")
        except Exception as e:
            self.error.emit(str(e))

class ModernFileComparator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(800, 600)
        self.lang = LanguageManager()  # Dil yöneticisi
        self.comparator = FileComparator()  # FileComparator örneği
        self.results = []
        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        self.title_bar = TitleBar(self, self.lang)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(main_layout)

        # Title Bar
        main_layout.addWidget(self.title_bar)

        # Control Panel
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(5, 5, 5, 5)

        control_layout.addWidget(QLabel(self.lang.translate("folder")))
        self.folder_path = QLineEdit()
        self.folder_path.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 5px;")
        control_layout.addWidget(self.folder_path)

        browse_btn = QPushButton(self.lang.translate("browse"))
        browse_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        browse_btn.clicked.connect(self.browse_folder)
        control_layout.addWidget(browse_btn)

        control_layout.addWidget(QLabel(self.lang.translate("min_similarity")))
        self.min_similarity = QLineEdit("0")
        self.min_similarity.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 5px;")
        self.min_similarity.setFixedWidth(50)
        control_layout.addWidget(self.min_similarity)
        control_layout.addWidget(QLabel("%"))

        main_layout.addWidget(control_frame)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"QProgressBar {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; }} QProgressBar::chunk {{ background-color: {ACCENT_COLOR}; }}")
        main_layout.addWidget(self.progress)

        # Status Label
        self.status_label = QLabel(self.lang.translate("status_ready"))
        self.status_label.setStyleSheet(f"color: {TEXT_COLOR}; padding: 5px;")
        main_layout.addWidget(self.status_label)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabWidget {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: none; }}")
        main_layout.addWidget(self.tabs)

        self.table_view = TableView(self, self.lang)  # lang parametresi eklendi
        self.visual_analysis = VisualAnalysis(self, self.lang)
        self.detailed_analysis = DetailedAnalysis(self, self.lang)

        self.tabs.addTab(self.table_view, self.lang.translate("table_view"))
        self.tabs.addTab(self.visual_analysis, self.lang.translate("visual_analysis"))
        self.tabs.addTab(self.detailed_analysis, self.lang.translate("detailed_analysis"))

        # Buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(5, 5, 5, 5)

        start_btn = QPushButton(self.lang.translate("start"))
        start_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        start_btn.clicked.connect(self.start_comparison)
        button_layout.addWidget(start_btn)

        stop_btn = QPushButton(self.lang.translate("stop"))
        stop_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        stop_btn.clicked.connect(self.stop_comparison)
        button_layout.addWidget(stop_btn)

        main_layout.addWidget(button_frame)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.lang.translate("browse"))
        if folder:
            self.folder_path.setText(folder)

    def start_comparison(self):
        if self.is_running or not os.path.isdir(self.folder_path.text()):
            QMessageBox.critical(self, "Error", self.lang.translate("invalid_folder"))
            return
        self.is_running = True
        self.clear_results()
        self.status_label.setText(self.lang.translate("status_running"))
        self.thread = ComparisonThread(
            self.folder_path.text(),
            "all",
            int(self.min_similarity.text() or "0"),
            self.comparator
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.result.connect(self.show_results)
        self.thread.status.connect(self.update_status)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def update_progress(self, value, processed, total):
        self.progress.setValue(int(value))
        self.status_label.setText(f"Processed: {processed}/{total} ({value:.1f}%)")

    def show_results(self, results):
        self.table_view.clear()
        for res in results:
            self.table_view.add_result(res)
        self.results = results
        self.visual_analysis.update_visual_analysis(results)
        self.status_label.setText(f"Completed! {len(results)} similar files found.")
        self.progress.setValue(100)
        self.is_running = False

    def stop_comparison(self):
        if hasattr(self, 'thread'):
            self.thread.is_running = False
        self.is_running = False
        self.status_label.setText(self.lang.translate("status_stopped"))

    def clear_results(self):
        self.results = []
        self.table_view.clear()
        self.visual_analysis.clear_visual_analysis()
        self.detailed_analysis.clear()
        self.status_label.setText(self.lang.translate("status_ready"))
        self.progress.setValue(0)

    def toggle_maximize(self):
        """Pencereyi tam ekran yapar veya normal duruma getirir."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()