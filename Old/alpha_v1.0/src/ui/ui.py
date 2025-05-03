# Main/src/ui/ui.py
import sys
import os
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QProgressBar, QTabWidget, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from .title_bar import TitleBar
from .table_view import TableView
from .visual_analysis import VisualAnalysis
from .detailed_analysis import DetailedAnalysis
from ..core.comparator import FileComparator  # FileComparator sınıfı eklendi
from ..languages.languages import LanguageManager  # Dil desteği için eklendi
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR, ACCENT_COLOR, TITLE_BAR_COLOR

# Logging yapılandırması
try:
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'Dev', 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(logs_dir, 'file_comparator.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except Exception as e:
    print(f"Logging yapılandırma hatası: {e}")

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
            self.total_comparisons = len(all_files) * (len(all_files) - 1) // 2
            self.processed = 0
            results = []

            for i in range(len(all_files)):
                if not self.is_running:
                    break
                for j in range(i + 1, len(all_files)):
                    if not self.is_running:
                        break
                    result = self.comparator.compare_files(all_files[i], all_files[j])
                    # Hata kontrolü ve varsayılan değerler
                    if 'total' in result and result['total'] >= self.min_similarity:
                        # Details anahtarına karşı hata koruması
                        if 'details' not in result:
                            result['details'] = {}

                        # Dosya adlarını al
                        file1_name = os.path.basename(all_files[i])
                        file2_name = os.path.basename(all_files[j])

                        # Sonuç verisini güvenli bir şekilde oluştur
                        result_data = {
                            'file1': file1_name,
                            'file2': file2_name,
                            'metadata': f"{result.get('metadata', 0):.1f}",
                            'hash': f"{result.get('hash', 0):.1f}",
                            'content': f"{result.get('content', 0):.1f}",
                            'structure': f"{result.get('structure', 0):.1f}",
                            'total': f"{result.get('total', 0):.1f}",
                            'category': result.get('category', 'Hata'),
                            'Path1': all_files[i],
                            'Path2': all_files[j],
                            'Details': result.get('details', {})
                        }
                        results.append(result_data)
                    self.processed += 1
                    progress_value = (self.processed / self.total_comparisons) * 100 if self.total_comparisons > 0 else 0
                    self.progress.emit(progress_value, self.processed, self.total_comparisons)
            self.result.emit(results)
            # Tamamlandı mesajını gönder, ana uygulama bunu çevirecek
            self.status.emit("completed")
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
        self.tabs.setStyleSheet(f"""
            QTabWidget {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: none; }}
            QTabBar::tab {{ min-width: 150px; padding: 8px; }}
            QTabBar::tab:selected {{ background-color: {ACCENT_COLOR}; }}
        """)
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

        clear_btn = QPushButton(self.lang.translate("clear"))
        clear_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_btn)

        report_btn = QPushButton(self.lang.translate("report"))
        report_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        report_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(report_btn)

        csv_btn = QPushButton(self.lang.translate("csv"))
        csv_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        csv_btn.clicked.connect(self.export_csv)
        button_layout.addWidget(csv_btn)

        help_btn = QPushButton(self.lang.translate("help"))
        help_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; padding: 8px;")
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)

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
        # Dosya tipi seçimi (varsayılan olarak "all")
        file_type = "all"
        self.thread = ComparisonThread(
            self.folder_path.text(),
            file_type,
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
        self.status_label.setText(f"{self.lang.translate('processed')}: {processed}/{total} ({value:.1f}%)")

    def update_status(self, message):
        """Thread'den gelen durum mesajını gösterir."""
        # Eğer mesaj bir anahtar ise çevir, değilse doğrudan göster
        if message in ["completed", "status_ready", "status_running", "status_stopped", "status_error"]:
            self.status_label.setText(self.lang.translate(message))
        else:
            self.status_label.setText(message)

    def show_error(self, error_message):
        """Thread'den gelen hata mesajını gösterir."""
        QMessageBox.critical(self, "Hata", error_message)
        self.status_label.setText(self.lang.translate("status_error"))
        self.is_running = False

    def show_results(self, results):
        self.table_view.clear()
        for res in results:
            self.table_view.add_result(res)
        self.results = results
        self.visual_analysis.update_visual_analysis(results)
        self.status_label.setText(f"{self.lang.translate('completed')}! {len(results)} {self.lang.translate('similar_files_found')}")
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

    def show_detail_view(self, item):
        """Seçilen dosya çiftinin detaylı analizini gösterir."""
        index = self.table_view.tree.indexOfTopLevelItem(item)
        if index >= 0 and index < len(self.results):
            self.detailed_analysis.update_details(self.results[index])
            self.tabs.setCurrentIndex(2)  # Detaylı analiz sekmesine geç

    def generate_report(self):
        """HTML rapor oluşturur ve kaydeder."""
        if not self.results:
            QMessageBox.warning(self, "Uyarı", self.lang.translate("no_results_for_report"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, self.lang.translate("save_report"), "", "HTML Files (*.html)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.lang.translate("app_title")} - {self.lang.translate("report")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #4CAF50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .high {{ background-color: #a8e6cf; }}
        .medium {{ background-color: #dcedc1; }}
        .low {{ background-color: #ffd3b6; }}
        .very-low {{ background-color: #ffaaa5; }}
    </style>
</head>
<body>
    <h1>{self.lang.translate("app_title")} - {self.lang.translate("report")}</h1>
    <p>{self.lang.translate("total_comparisons")}: {len(self.results)}</p>

    <h2>{self.lang.translate("similarity_stats")}</h2>
    <table>
        <tr>
            <th>{self.lang.translate("total_comparisons")}</th>
            <th>{self.lang.translate("average_similarity")}</th>
            <th>{self.lang.translate("maximum")}</th>
            <th>{self.lang.translate("minimum")}</th>
        </tr>
        <tr>
            <td>{len(self.results)}</td>
            <td>{sum(float(r['total']) for r in self.results) / len(self.results):.2f}%</td>
            <td>{max(float(r['total']) for r in self.results):.2f}%</td>
            <td>{min(float(r['total']) for r in self.results):.2f}%</td>
        </tr>
    </table>

    <h2>{self.lang.translate("results")}</h2>
    <table>
        <tr>
            <th>{self.lang.translate("file1")}</th>
            <th>{self.lang.translate("file2")}</th>
            <th>{self.lang.translate("metadata")}</th>
            <th>{self.lang.translate("hash")}</th>
            <th>{self.lang.translate("content")}</th>
            <th>{self.lang.translate("structure")}</th>
            <th>{self.lang.translate("total")}</th>
            <th>{self.lang.translate("result")}</th>
        </tr>
        {"".join(f'''
        <tr class="{'high' if float(r['total']) >= 95 else 'medium' if float(r['total']) >= 75 else 'low' if float(r['total']) >= 25 else 'very-low'}">
            <td>{r['file1']}</td>
            <td>{r['file2']}</td>
            <td>{r.get('metadata', 'N/A')}</td>
            <td>{r.get('hash', 'N/A')}</td>
            <td>{r.get('content', 'N/A')}</td>
            <td>{r.get('structure', 'N/A')}</td>
            <td>{r['total']}</td>
            <td>{r.get('category', 'N/A')}</td>
        </tr>''' for r in self.results)}
    </table>

    <p><small>Generated by {self.lang.translate("app_title")} v{__version__}</small></p>
</body>
</html>""")

            QMessageBox.information(
                self, "Bilgi", f"{self.lang.translate('results_exported')} {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor oluşturma hatası: {str(e)}")

    def export_csv(self):
        """Sonuçları CSV dosyasına aktarır."""
        if not self.results:
            QMessageBox.warning(self, "Uyarı", self.lang.translate("no_results_to_export"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, self.lang.translate("save_csv"), "", "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    self.lang.translate("file1"),
                    self.lang.translate("file2"),
                    self.lang.translate("metadata"),
                    self.lang.translate("hash"),
                    self.lang.translate("content"),
                    self.lang.translate("structure"),
                    self.lang.translate("total"),
                    self.lang.translate("result")
                ])

                for r in self.results:
                    writer.writerow([
                        r['file1'],
                        r['file2'],
                        r.get('metadata', 'N/A'),
                        r.get('hash', 'N/A'),
                        r.get('content', 'N/A'),
                        r.get('structure', 'N/A'),
                        r['total'],
                        r.get('category', 'N/A')
                    ])

            QMessageBox.information(
                self, "Bilgi", f"{self.lang.translate('results_exported')} {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"CSV dışa aktarma hatası: {str(e)}")

    def show_help(self):
        """Yardım mesajını gösterir."""
        QMessageBox.information(
            self,
            self.lang.translate("help"),
            self.lang.translate("usage_instructions")
        )

    def change_language(self, language):
        """Uygulamanın dilini değiştirir."""
        if language == "Türkçe":
            self.lang.set_language("tr")
        elif language == "English":
            self.lang.set_language("en")

        # Tüm metinleri güncelle
        # Başlık çubuğu
        self.title_bar.update_texts()

        # Kontrol paneli
        control_frame = self.centralWidget().layout().itemAt(1).widget()
        control_layout = control_frame.layout()

        # Folder label
        control_layout.itemAt(0).widget().setText(self.lang.translate("folder"))

        # Browse button
        control_layout.itemAt(2).widget().setText(self.lang.translate("browse"))

        # Min similarity label
        control_layout.itemAt(3).widget().setText(self.lang.translate("min_similarity"))

        # Status label
        # Eğer işlem devam ediyorsa ve sonuçlar varsa, işlem durumunu güncelle
        if self.is_running and hasattr(self, 'thread') and self.thread.isRunning():
            # İşlem devam ediyor, ilerleme durumunu güncelle
            try:
                value = self.progress.value()
                total_comparisons = getattr(self.thread, 'total_comparisons', 0)
                processed = getattr(self.thread, 'processed', 0)
                self.status_label.setText(f"{self.lang.translate('processed')}: {processed}/{total_comparisons} ({value:.1f}%)")
            except:
                self.status_label.setText(self.lang.translate("status_running"))
        elif self.results:
            # Sonuçlar var, tamamlandı mesajını göster
            self.status_label.setText(f"{self.lang.translate('completed')}! {len(self.results)} {self.lang.translate('similar_files_found')}")
        else:
            # Hazır durumda
            self.status_label.setText(self.lang.translate("status_ready"))

        # Tablo başlıkları
        self.table_view.update_headers()

        # Sekme başlıkları
        self.tabs.setTabText(0, self.lang.translate("table_view"))
        self.tabs.setTabText(1, self.lang.translate("visual_analysis"))
        self.tabs.setTabText(2, self.lang.translate("detailed_analysis"))

        # Butonlar
        button_frame = self.centralWidget().layout().itemAt(5).widget()
        button_layout = button_frame.layout()

        # Start button
        button_layout.itemAt(0).widget().setText(self.lang.translate("start"))

        # Stop button
        button_layout.itemAt(1).widget().setText(self.lang.translate("stop"))

        # Clear button
        button_layout.itemAt(2).widget().setText(self.lang.translate("clear"))

        # Report button
        button_layout.itemAt(3).widget().setText(self.lang.translate("report"))

        # CSV button
        button_layout.itemAt(4).widget().setText(self.lang.translate("csv"))

        # Help button
        button_layout.itemAt(5).widget().setText(self.lang.translate("help"))

        # Diğer bileşenleri güncelle
        self.detailed_analysis.update_texts()
        if hasattr(self.visual_analysis, 'update_texts'):
            self.visual_analysis.update_texts()