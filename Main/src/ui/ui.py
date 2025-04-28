from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QProgressBar, QTabWidget, 
                            QFileDialog, QMessageBox, QRadioButton, QFrame, 
                            QSizeGrip, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QFont
import os
import webbrowser
import pandas as pd
from .title_bar import TitleBar
from .table_view import TableView
from .visual_analysis import VisualAnalysis
from .detailed_analysis import DetailedAnalysis
from ..core.comparator import FileComparator
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR, ACCENT_COLOR
from ...languages.languages import LanguageManager  # Düzeltildi

class ComparisonThread(QThread):
    progress = pyqtSignal(float, int, int)
    finished = pyqtSignal()

    def __init__(self, folder, comparator, min_similarity):
        super().__init__()
        self.folder = folder
        self.comparator = comparator
        self.min_similarity = min_similarity
        self.is_running = True

    def run(self):
        file_type = "solidworks"
        extensions = self.comparator.supported_extensions[file_type]
        all_files = [f for f in os.listdir(self.folder) if os.path.isfile(os.path.join(self.folder, f)) and (not extensions or os.path.splitext(f)[1].lower() in extensions)]
        total_comparisons = len(all_files) * (len(all_files) - 1) // 2
        processed = 0
        self.results = []
        for i in range(len(all_files)):
            if not self.is_running:
                break
            file1 = os.path.join(self.folder, all_files[i])
            for j in range(i + 1, len(all_files)):
                if not self.is_running:
                    break
                file2 = os.path.join(self.folder, all_files[j])
                result = self.comparator.compare_files(file1, file2)
                if result['total'] >= self.min_similarity:
                    category = self.lang.get("full_match") if result['total'] >= 95 else self.lang.get("different_files")
                    self.results.append({
                        'Dosya 1': all_files[i], 'Dosya 2': all_files[j], 'Metadata': f"{result['metadata']:.1f}",
                        'Hash': f"{result['hash']:.1f}", 'İçerik': f"{result['content']:.1f}", 'Yapı': f"{result['structure']:.1f}",
                        'Toplam': f"{result['total']:.1f}", 'Sonuç': category, 'Path1': file1, 'Path2': file2, 'Details': result
                    })
                processed += 1
                if processed % 10 == 0:
                    self.progress.emit((processed / total_comparisons) * 100 if total_comparisons > 0 else 0, processed, total_comparisons)
        self.finished.emit()

class ModernFileComparator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(800, 600)
        self.lang = LanguageManager()
        self.comparator = FileComparator()
        self.results = []
        self.is_running = False
        self.old_pos = None
        self.resize_direction = None
        self.setup_ui()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet(f"background-color: {BUTTON_COLOR}; width: 20px; height: 20px;")

    def setup_ui(self):
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar = TitleBar(self, self.lang)
        main_layout.addWidget(self.title_bar)
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.addWidget(QLabel(self.lang.get("folder")))
        self.folder_path = QLineEdit()
        self.folder_path.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 5px;")
        control_layout.addWidget(self.folder_path)
        browse_btn = QPushButton(self.lang.get("browse"))
        browse_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        browse_btn.setMinimumHeight(40)
        browse_btn.setFont(QFont("Arial", 10))
        browse_btn.clicked.connect(self.browse_folder)
        control_layout.addWidget(browse_btn)
        self.file_types = {'solidworks': self.lang.get('solidworks'), 'cad': self.lang.get('cad'), 'document': self.lang.get('document'), 'image': self.lang.get('image'), 'all': self.lang.get('all_files')}
        self.file_type_var = "solidworks"
        self.radio_buttons = []
        for value, text in self.file_types.items():
            rb = QRadioButton(text)
            rb.setChecked(value == "solidworks")
            rb.toggled.connect(lambda checked, v=value: self.set_file_type(v) if checked else None)
            rb.setStyleSheet(f"color: {TEXT_COLOR};")
            control_layout.addWidget(rb)
            self.radio_buttons.append(rb)
        control_layout.addWidget(QLabel(self.lang.get("min_similarity")))
        self.min_similarity = QLineEdit("0")
        self.min_similarity.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 5px;")
        self.min_similarity.setFixedWidth(50)
        control_layout.addWidget(self.min_similarity)
        control_layout.addWidget(QLabel("%"))
        control_layout.addStretch()
        main_layout.addWidget(control_frame)
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"QProgressBar {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; }} QProgressBar::chunk {{ background-color: {ACCENT_COLOR}; }}")
        main_layout.addWidget(self.progress)
        self.status_label = QLabel(self.lang.get("status_ready"))
        self.status_label.setStyleSheet(f"color: {TEXT_COLOR}; padding: 5px;")
        main_layout.addWidget(self.status_label)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabWidget {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: none; }} "
                               f"QTabBar::tab {{ background: {BUTTON_COLOR}; color: {TEXT_COLOR}; padding: 8px; font-size: 12px; border: none; }} "
                               f"QTabBar::tab:selected {{ background: {ACCENT_COLOR}; color: {TEXT_COLOR}; border: none; }}")
        main_layout.addWidget(self.tabs)
        self.table_view = TableView(self, self.lang)
        self.visual_analysis = VisualAnalysis(self, self.lang)
        self.detailed_analysis = DetailedAnalysis(self, self.lang)
        self.tabs.addTab(self.table_view, self.lang.get("table_view"))
        self.tabs.addTab(self.visual_analysis, self.lang.get("visual_analysis"))
        self.tabs.addTab(self.detailed_analysis, self.lang.get("detailed_analysis"))
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(5, 5, 5, 5)
        self.buttons = []
        for text, func in [(self.lang.get("start"), self.start_comparison), (self.lang.get("stop"), self.stop_comparison),
                           (self.lang.get("clear"), self.clear_results), (self.lang.get("report"), self.generate_report),
                           (self.lang.get("csv"), self.export_results), (self.lang.get("help"), self.show_help)]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 10))
            btn.clicked.connect(func)
            button_layout.addWidget(btn)
            self.buttons.append(btn)
        main_layout.addWidget(button_frame)

    def change_language(self, lang):
        lang_code = "tr" if lang == "Türkçe" else "en"
        self.lang.set_language(lang_code)
        self.update_ui_texts()
        QApplication.processEvents()

    def update_ui_texts(self):
        self.title_bar.update_texts()
        self.status_label.setText(self.lang.get("status_ready"))
        self.tabs.setTabText(0, self.lang.get("table_view"))
        self.tabs.setTabText(1, self.lang.get("visual_analysis"))
        self.tabs.setTabText(2, self.lang.get("detailed_analysis"))
        control_frame = self.centralWidget().layout().itemAt(1).widget()
        control_layout = control_frame.layout()
        control_layout.itemAt(0).widget().setText(self.lang.get("folder"))
        control_layout.itemAt(2).widget().setText(self.lang.get("browse"))
        self.file_types = {'solidworks': self.lang.get('solidworks'), 'cad': self.lang.get('cad'), 'document': self.lang.get('document'), 'image': self.lang.get('image'), 'all': self.lang.get('all_files')}
        for i, (value, text) in enumerate(self.file_types.items()):
            self.radio_buttons[i].setText(text)
        control_layout.itemAt(8).widget().setText(self.lang.get("min_similarity"))
        for i, key in enumerate(["start", "stop", "clear", "report", "csv", "help"]):
            self.buttons[i].setText(self.lang.get(key))
        self.table_view.update_headers()
        self.detailed_analysis.update_texts()

    def set_file_type(self, file_type):
        self.file_type_var = file_type

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        margin = 12
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.resize_direction = None
            if pos.x() < margin and pos.y() < margin:
                self.resize_direction = "top-left"
            elif pos.x() > self.width() - margin and pos.y() < margin:
                self.resize_direction = "top-right"
            elif pos.x() < margin and pos.y() > self.height() - margin:
                self.resize_direction = "bottom-left"
            elif pos.x() > self.width() - margin and pos.y() > self.height() - margin:
                self.resize_direction = "bottom-right"
            elif pos.x() < margin:
                self.resize_direction = "left"
            elif pos.x() > self.width() - margin:
                self.resize_direction = "right"
            elif pos.y() < margin:
                self.resize_direction = "top"
            elif pos.y() > self.height() - margin:
                self.resize_direction = "bottom"
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.resize_direction:
            delta = event.globalPos() - self.old_pos
            new_geometry = QRect(self.geometry())
            if "left" in self.resize_direction:
                new_geometry.setLeft(new_geometry.left() + delta.x())
            if "right" in self.resize_direction:
                new_geometry.setRight(new_geometry.right() + delta.x())
            if "top" in self.resize_direction:
                new_geometry.setTop(new_geometry.top() + delta.y())
            if "bottom" in self.resize_direction:
                new_geometry.setBottom(new_geometry.bottom() + delta.y())
            self.setGeometry(new_geometry)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.resize_direction = None
        self.old_pos = None

    def resizeEvent(self, event):
        grip_size = self.size_grip.sizeHint()
        self.size_grip.setGeometry(self.width() - grip_size.width(), self.height() - grip_size.height(), grip_size.width(), grip_size.height())
        super().resizeEvent(event)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.lang.get("browse"))
        if folder:
            self.folder_path.setText(folder)

    def start_comparison(self):
        if self.is_running or not os.path.isdir(self.folder_path.text()):
            QMessageBox.critical(self, "Hata", self.lang.get("invalid_folder"))
            return
        self.is_running = True
        self.clear_results()
        self.status_label.setText(self.lang.get("status_running"))
        self.thread = ComparisonThread(self.folder_path.text(), self.comparator, int(self.min_similarity.text() or "0"))
        self.thread.lang = self.lang
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.show_results)
        self.thread.start()

    def update_progress(self, value, processed, total):
        self.progress.setValue(int(value))
        self.status_label.setText(f"İşlem: {processed}/{total} ({value:.1f}%)")

    def show_results(self):
        self.table_view.clear()
        for res in self.thread.results:
            self.table_view.add_result(res)
        self.results = self.thread.results
        self.visual_analysis.update_visual(self.results)
        self.status_label.setText(f"{self.lang.get('completed')} {len(self.thread.results)} {self.lang.get('similar_files_found')}")
        self.progress.setValue(100)
        self.is_running = False

    def show_detail_view(self, item, column):
        for res in self.results:
            if res['Dosya 1'] == item.text(0) and res['Dosya 2'] == item.text(1):
                self.tabs.setCurrentIndex(2)
                self.detailed_analysis.update_details(res)
                break

    def clear_results(self):
        self.results = []
        self.table_view.clear()
        self.visual_analysis.clear()
        self.detailed_analysis.clear()
        self.status_label.setText(self.lang.get("status_ready"))
        self.progress.setValue(0)

    def stop_comparison(self):
        if hasattr(self, 'thread'):
            self.thread.is_running = False
        self.is_running = False
        self.status_label.setText(self.lang.get("status_stopped"))

    def generate_report(self):
        if not self.results:
            QMessageBox.information(self, "Bilgi", self.lang.get("no_results_for_report"))
            return
        file_path = QFileDialog.getSaveFileName(self, self.lang.get("save_report"), "", "HTML Dosyası (*.html)")[0]
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"<!DOCTYPE html><html lang='tr'><head><meta charset='UTF-8'><title>{self.lang.get('report')}</title><style>body{{font-family:Arial;margin:20px;}}table{{border-collapse:collapse;width:100%;}}th,td{{border:1px solid #ddd;padding:8px;}}</style></head><body><h1>{self.lang.get('report')}</h1><table><tr><th>{self.lang.get('file1')}</th><th>{self.lang.get('file2')}</th><th>{self.lang.get('metadata')}</th><th>{self.lang.get('hash')}</th><th>{self.lang.get('content')}</th><th>{self.lang.get('structure')}</th><th>{self.lang.get('total')}</th><th>{self.lang.get('result')}</th></tr>{''.join(f'<tr><td>{r['Dosya 1']}</td><td>{r['Dosya 2']}</td><td>{r['Metadata']}</td><td>{r['Hash']}</td><td>{r['İçerik']}</td><td>{r['Yapı']}</td><td>{r['Toplam']}</td><td>{r['Sonuç']}</td></tr>' for r in self.results)}</table></body></html>")
            webbrowser.open(f'file://{os.path.realpath(file_path)}')

    def export_results(self):
        if not self.results:
            QMessageBox.information(self, "Bilgi", self.lang.get("no_results_to_export"))
            return
        file_path = QFileDialog.getSaveFileName(self, self.lang.get("save_csv"), "", "CSV Dosyası (*.csv)")[0]
        if file_path:
            pd.DataFrame(self.results).to_csv(file_path, index=False)
            QMessageBox.information(self, "Başarılı", f"{self.lang.get('results_exported')}\n{file_path}")

    def show_help(self):
        QMessageBox.information(self, self.lang.get("help"), self.lang.get("usage_instructions"))
