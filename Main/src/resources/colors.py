import os
import sys
import time
import threading
import webbrowser
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QProgressBar, QTabWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, QFileDialog, QMessageBox,
                             QRadioButton, QFrame, QComboBox, QSizeGrip, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QColor, QFont
from comparator import FileComparator
from colors import *
from languages import LanguageManager
from utils import get_file_info, format_size

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
                    self.results.append({
                        'Dosya 1': all_files[i], 'Dosya 2': all_files[j], 'Metadata': f"{result['metadata']:.1f}",
                        'Hash': f"{result['hash']:.1f}", 'İçerik': f"{result['content']:.1f}", 'Yapı': f"{result['structure']:.1f}",
                        'Toplam': f"{result['total']:.1f}", 'Sonuç': result['category'], 'Path1': file1, 'Path2': file2, 'Details': result
                    })
                processed += 1
                if time.time() % 0.1 < 0.01:
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
        self.create_title_bar(main_layout)
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
        self.tabs.setStyleSheet(f"QTabWidget {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: none; }} QTabBar::tab {{ background: {BUTTON_COLOR}; color: {TEXT_COLOR}; padding: 8px; font-size: 12px; }} QTabBar::tab:selected {{ background: {ACCENT_COLOR}; color: {TEXT_COLOR}; }}")
        main_layout.addWidget(self.tabs)
        self.setup_table_view()
        self.setup_visual_analysis()
        self.setup_detail_panel()
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

    def create_title_bar(self, layout):
        title_bar = QFrame()
        title_bar.setStyleSheet(f"background-color: {TITLE_BAR_COLOR};")
        title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 0, 5, 0)
        self.title_label = QLabel(self.lang.get("title"))
        self.title_label.setStyleSheet(f"color: {TEXT_COLOR};")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Türkçe"])
        self.lang_combo.setCurrentText("Türkçe" if self.lang.current_lang == "tr" else "English")
        self.lang_combo.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 5px;")
        self.lang_combo.currentTextChanged.connect(self.change_language)
        title_layout.addWidget(self.lang_combo)
        for text, func, color in [("─", self.showMinimized, BUTTON_COLOR), ("□", self.toggle_maximize, BUTTON_COLOR), ("✕", self.close, "#ff5555")]:
            btn = QPushButton(text)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color}; color: {TEXT_COLOR}; border: none;")
            btn.clicked.connect(func)
            title_layout.addWidget(btn)
        layout.addWidget(title_bar)

    def change_language(self, lang):
        lang_code = "tr" if lang == "Türkçe" else "en"
        self.lang.set_language(lang_code)
        self.update_ui_texts()
        QApplication.processEvents()

    def update_ui_texts(self):
        self.title_label.setText(self.lang.get("title"))
        self.status_label.setText(self.lang.get("status_ready"))
        self.tabs.setTabText(0, self.lang.get("table_view"))
        self.tabs.setTabText(1, self.lang.get("visual_analysis"))
        self.tabs.setTabText(2, self.lang.get("detailed_analysis"))
        self.lang_combo.setItemText(0, "English")
        self.lang_combo.setItemText(1, "Türkçe")
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
        self.tree.setHeaderLabels([self.lang.get("file1"), self.lang.get("file2"), self.lang.get("metadata"), self.lang.get("hash"),
                                   self.lang.get("content"), self.lang.get("structure"), self.lang.get("total"), self.lang.get("result")])

    def set_file_type(self, file_type):
        self.file_type_var = file_type

    def start_move(self, event):
        self.old_pos = event.globalPos()

    def stop_move(self, event):
        self.old_pos = None

    def on_move(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            new_pos = self.pos() + delta
            screen = QApplication.primaryScreen().geometry()
            if new_pos.y() <= screen.top() + 10:
                self.showMaximized()
            elif new_pos.x() <= screen.left() + 10:
                self.setGeometry(screen.left(), screen.top(), screen.width() // 2, screen.height())
            elif new_pos.x() + self.width() >= screen.right() - 10:
                self.setGeometry(screen.right() - screen.width() // 2, screen.top(), screen.width() // 2, screen.height())
            else:
                self.move(new_pos)
            self.old_pos = event.globalPos()

    def toggle_maximize(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def setup_table_view(self):
        table_tab = QWidget()
        layout = QVBoxLayout(table_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tree = QTreeWidget()
        self.tree.setStyleSheet(f"QTreeWidget {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; }} QTreeWidget::item {{ border: none; }} QTreeWidget::header {{ background: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; }}")
        self.tree.setHeaderLabels([self.lang.get("file1"), self.lang.get("file2"), self.lang.get("metadata"), self.lang.get("hash"),
                                   self.lang.get("content"), self.lang.get("structure"), self.lang.get("total"), self.lang.get("result")])
        self.tree.itemDoubleClicked.connect(self.show_detail_view)
        layout.addWidget(self.tree)
        self.tabs.addTab(table_tab, self.lang.get("table_view"))

    def setup_visual_analysis(self):
        visual_tab = QWidget()
        layout = QVBoxLayout(visual_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig, self.ax = plt.subplots(figsize=(6, 4), facecolor=BACKGROUND_COLOR)
        self.fig.set_facecolor(BACKGROUND_COLOR)
        self.ax.set_facecolor(BACKGROUND_COLOR)
        self.ax.tick_params(colors=TEXT_COLOR)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        layout.addWidget(self.canvas)
        self.stats_text = QTextEdit()
        self.stats_text.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none;")
        layout.addWidget(self.stats_text)
        self.tabs.addTab(visual_tab, self.lang.get("visual_analysis"))

    def setup_detail_panel(self):
        detail_tab = QTabWidget()
        detail_tab.setStyleSheet(f"QTabWidget {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: none; }} QTabBar::tab {{ background: {BUTTON_COLOR}; color: {TEXT_COLOR}; padding: 5px; }} QTabBar::tab:selected {{ background: {ACCENT_COLOR}; color: {TEXT_COLOR}; }}")
        file_info_tab = QWidget()
        file_layout = QHBoxLayout(file_info_tab)
        file_layout.setContentsMargins(0, 0, 0, 0)
        self.file1_info = QTextEdit()
        self.file2_info = QTextEdit()
        for w in [self.file1_info, self.file2_info]:
            w.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none;")
            file_layout.addWidget(w)
        detail_tab.addTab(file_info_tab, "Dosya Bilgileri")
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(comparison_tab)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        self.comparison_text = QTextEdit()
        self.comparison_text.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none;")
        comparison_layout.addWidget(self.comparison_text)
        detail_tab.addTab(comparison_tab, "Karşılaştırma Detayları")
        self.tabs.addTab(detail_tab, self.lang.get("detailed_analysis"))

    def mousePressEvent(self, event):
        margin = 8  # Kenar tutma alanını 8 piksele çıkardım
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.resize_direction = None
            # Kenar ve köşeler için kontrol
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
        # QSizeGrip'i sağ alt köşeye yerleştir
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
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.show_results)
        self.thread.start()

    def update_progress(self, value, processed, total):
        self.progress.setValue(int(value))
        self.status_label.setText(f"İşlem: {processed}/{total} ({value:.1f}%)")

    def show_results(self):
        self.tree.clear()
        header_labels = [self.lang.get("file1"), self.lang.get("file2"), self.lang.get("metadata"), self.lang.get("hash"),
                         self.lang.get("content"), self.lang.get("structure"), self.lang.get("total"), self.lang.get("result")]
        self.tree.setHeaderLabels(header_labels)
        for res in self.thread.results:
            item = QTreeWidgetItem([res['Dosya 1'], res['Dosya 2'], res['Metadata'], res['Hash'], res['İçerik'], res['Yapı'], res['Toplam'], res['Sonuç']])
            total_score = float(res['Toplam'])
            item.setBackground(0, QColor("#a8e6cf" if total_score >= 95 else "#dcedc1" if total_score >= 75 else "#ffd3b6" if total_score >= 25 else "#ffaaa5"))
            self.tree.addTopLevelItem(item)
        self.update_visual_analysis()
        self.status_label.setText(f"{self.lang.get('completed')} {len(self.thread.results)} {self.lang.get('similar_files_found')}")
        self.progress.setValue(100)
        self.is_running = False

    def update_visual_analysis(self):
        if not self.thread.results:
            return
        self.ax.clear()
        scores = [float(r['Toplam']) for r in self.thread.results]
        similarity_ranges = {'95-100': 0, '75-95': 0, '50-75': 0, '25-50': 0, '0-25': 0}
        for score in scores:
            similarity_ranges['95-100' if score >= 95 else '75-95' if score >= 75 else '50-75' if score >= 50 else '25-50' if score >= 25 else '0-25'] += 1
        labels, sizes = zip(*[(f"{k}% ({v})", v) for k, v in similarity_ranges.items() if v > 0])
        if sizes:
            self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, textprops={'color': TEXT_COLOR})
            self.ax.axis('equal')
            self.canvas.draw()
        self.stats_text.setText(f"📊 {self.lang.get('similarity_stats')}\n==============================\n{self.lang.get('total_comparisons')}: {len(self.thread.results)}\n{self.lang.get('average_similarity')}: {np.mean(scores):.2f}%\n{self.lang.get('maximum')}: {max(scores):.2f}%\n{self.lang.get('minimum')}: {min(scores):.2f}%\n==============================")

    def show_detail_view(self, item, column):
        for res in self.thread.results:
            if res['Dosya 1'] == item.text(0) and res['Dosya 2'] == item.text(1):
                self.tabs.setCurrentIndex(2)
                self.file1_info.setText(get_file_info(res['Path1']))
                self.file2_info.setText(get_file_info(res['Path2']))
                details = res['Details']
                text = f"🔍 {self.lang.get('detailed_comparison')}\n==========================\n{self.lang.get('file1')}: {res['Dosya 1']}\n{self.lang.get('file2')}: {res['Dosya 2']}\n{self.lang.get('total_similarity')}: {details['total']:.2f}%\n{self.lang.get('result')}: {details['category']}\n{self.lang.get('file_type')}: {details['file_type']}\n\n📊 {self.lang.get('weighted_scores')}:\n- {self.lang.get('metadata')}: {details['metadata']:.2f}%\n- {self.lang.get('hash')}: {details['hash']:.2f}%\n- {self.lang.get('content')}: {details['content']:.2f}%\n- {self.lang.get('structure')}: {details['structure']:.2f}%\n\n🔎 {self.lang.get('manipulation_analysis')}:\n- {self.lang.get('detection')}: {'Evet' if details['manipulation']['detected'] else 'Hayır'}\n- {self.lang.get('score')}: {details['manipulation']['score']:.2f}%\n- {self.lang.get('type')}: {details['manipulation']['type']}"
                if details['file_type'] == 'solidworks' and 'details' in details:
                    sw_details = details['details']
                    text += f"\n\n📊 {self.lang.get('solidworks_detailed_analysis')}:\n---------------------------\n- {self.lang.get('feature_tree')}: {sw_details.get('feature_tree', 0):.2f}%\n- {self.lang.get('sketch_data')}: {sw_details.get('sketch_data', 0):.2f}%\n- {self.lang.get('geometry')}: {sw_details.get('geometry', 0):.2f}%"
                self.comparison_text.setText(text)
                break

    def clear_results(self):
        self.results = []
        self.tree.clear()
        self.ax.clear()
        self.canvas.draw()
        self.stats_text.clear()
        self.file1_info.clear()
        self.file2_info.clear()
        self.comparison_text.clear()
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