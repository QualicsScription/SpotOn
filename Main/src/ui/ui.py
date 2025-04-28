# Main/src/ui/ui.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QProgressBar, QTabWidget, QFileDialog, QMessageBox, QRadioButton, QFrame, QSizeGrip, QApplication)
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
from ...languages.languages import LanguageManager

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
            all_files = [f for f in os.listdir(self.folder)
                         if os.path.isfile(os.path.join(self.folder, f)) and
                         (not extensions or os.path.splitext(f)[1].lower() in extensions)]

            total_comparisons = len(all_files) * (len(all_files) - 1) // 2
            processed = 0
            results = []

            for i in range(len(all_files)):
                if not self.is_running:
                    break

                file1 = os.path.join(self.folder, all_files[i])
                for j in range(i + 1, len(all_files)):
                    if not self.is_running:
                        break

                    file2 = os.path.join(self.folder, all_files[j])
                    comparison_result = self.comparator.compare_files(file1, file2)

                    if comparison_result['total'] >= self.min_similarity:
                        result_data = {
                            'Dosya 1': all_files[i],
                            'Dosya 2': all_files[j],
                            'Metadata': f"{comparison_result['metadata']:.1f}",
                            'Hash': f"{comparison_result['hash']:.1f}",
                            'İçerik': f"{comparison_result['content']:.1f}",
                            'Yapı': f"{comparison_result['structure']:.1f}",
                            'Toplam': f"{comparison_result['total']:.1f}",
                            'Sonuç': comparison_result['category'],
                            'Path1': file1,
                            'Path2': file2,
                            'Details': comparison_result
                        }
                        results.append(result_data)

                    processed += 1
                    progress_value = (processed / total_comparisons) * 100 if total_comparisons > 0 else 0
                    self.progress.emit(progress_value, processed, total_comparisons)

            self.result.emit(results)
            self.status.emit(f"Tamamlandı! {len(results)} benzer dosya çifti bulundu.")
        except Exception as e:
            self.error.emit(str(e))

class ModernFileComparator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Gelişmiş Dosya Karşılaştırıcı v{__version__}")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)

        self.comparator = FileComparator()
        self.results = []
        self.is_running = False
        self.language_manager = LanguageManager()

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Özel başlık çubuğu
        self.title_bar = TitleBar(self, f"Gelişmiş Dosya Karşılaştırıcı v{__version__}")
        main_layout.addWidget(self.title_bar)

        # Kontrol paneli
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        control_layout.addWidget(QLabel("Klasör:"))
        self.folder_path = QLineEdit()
        self.folder_path.setFixedWidth(500)
        control_layout.addWidget(self.folder_path)
        browse_btn = QPushButton("📁 Gözat")
        browse_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        browse_btn.clicked.connect(self.browse_folder)
        control_layout.addWidget(browse_btn)

        # Dosya tipi seçimi
        file_types = {
            'solidworks': 'SolidWorks',
            'cad': 'CAD',
            'document': 'Döküman',
            'image': 'Görsel',
            'all': 'Tüm Dosyalar'
        }
        self.file_type = "solidworks"
        for value, text in file_types.items():
            rb = QRadioButton(text)
            rb.setStyleSheet(f"color: {TEXT_COLOR};")
            if value == "solidworks":
                rb.setChecked(True)
            rb.toggled.connect(lambda checked, v=value: self.set_file_type(v) if checked else None)
            control_layout.addWidget(rb)

        # Minimum benzerlik
        control_layout.addStretch()
        control_layout.addWidget(QLabel("Min. Benzerlik:"))
        self.min_similarity = QLineEdit()
        self.min_similarity.setFixedWidth(50)
        self.min_similarity.setText("0")
        control_layout.addWidget(self.min_similarity)
        control_layout.addWidget(QLabel("%"))

        main_layout.addWidget(control_frame)

        # İlerleme çubuğu
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"color: {TEXT_COLOR};")
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)

        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet(f"color: {TEXT_COLOR};")
        main_layout.addWidget(self.status_label)

        # Sonuçlar paneli
        self.notebook = QTabWidget()
        self.notebook.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        main_layout.addWidget(self.notebook)

        # Tablo görünümü
        self.table_view = TableView(self)
        self.notebook.addTab(self.table_view, "Tablo Görünümü")

        # Görsel analiz
        self.visual_analysis = VisualAnalysis(self)
        self.notebook.addTab(self.visual_analysis, "Görsel Analiz")

        # Detaylı analiz
        self.detail_panel = DetailedAnalysis(self)
        self.notebook.addTab(self.detail_panel, "Detaylı Analiz")

        # Butonlar
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        start_btn = QPushButton("▶️ Başlat")
        start_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        start_btn.clicked.connect(self.start_comparison)
        button_layout.addWidget(start_btn)

        stop_btn = QPushButton("⏹ Durdur")
        stop_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        stop_btn.clicked.connect(self.stop_comparison)
        button_layout.addWidget(stop_btn)

        clear_btn = QPushButton("🗑️ Temizle")
        clear_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_btn)

        report_btn = QPushButton("📊 Rapor")
        report_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        report_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(report_btn)

        export_btn = QPushButton("💾 CSV")
        export_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        export_btn.clicked.connect(self.export_results)
        button_layout.addWidget(export_btn)

        help_btn = QPushButton("?")
        help_btn.setFixedSize(30, 30)
        help_btn.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR};")
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)

        button_layout.addStretch()
        main_layout.addWidget(button_frame)

    def set_file_type(self, value):
        self.file_type = value

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seçin")
        if folder:
            self.folder_path.setText(folder)

    def start_comparison(self):
        if self.is_running:
            return

        folder = self.folder_path.text()
        if not os.path.isdir(folder):
            QMessageBox.critical(self, "Hata", "Geçerli bir klasör seçin!")
            return

        self.is_running = True
        self.clear_results()
        self.status_label.setText("Dosyalar taranıyor...")
        self.progress.setValue(0)

        try:
            min_similarity = int(self.min_similarity.text())
        except ValueError:
            min_similarity = 0

        self.comparison_thread = ComparisonThread(folder, self.file_type, min_similarity, self.comparator)
        self.comparison_thread.progress.connect(self.update_progress)
        self.comparison_thread.result.connect(self.show_results)
        self.comparison_thread.status.connect(self.update_status)
        self.comparison_thread.error.connect(self.show_error)
        self.comparison_thread.start()

    def update_progress(self, progress_value, processed, total):
        self.progress.setValue(int(progress_value))
        self.status_label.setText(f"İşlem: {processed}/{total} ({progress_value:.1f}%)")

    def show_results(self, results):
        self.results = results
        self.table_view.show_results(results)
        self.visual_analysis.update_visual_analysis(results)
        self.status_label.setText(f"Tamamlandı! {len(results)} benzer dosya çifti bulundu.")
        self.progress.setValue(100)

    def update_status(self, status):
        self.status_label.setText(status)
        self.is_running = False

    def show_error(self, error):
        QMessageBox.critical(self, "Hata", error)
        self.is_running = False

    def stop_comparison(self):
        self.is_running = False
        if hasattr(self, 'comparison_thread'):
            self.comparison_thread.is_running = False
        self.status_label.setText("İşlem durduruldu!")

    def clear_results(self):
        self.results = []
        self.table_view.clear_results()
        self.visual_analysis.clear_visual_analysis()
        self.detail_panel.clear_details()
        self.status_label.setText("Hazır")
        self.progress.setValue(0)

    def generate_report(self):
        if not self.results:
            QMessageBox.information(self, "Bilgi", "Rapor oluşturmak için sonuç bulunmuyor!")
            return

        file_path = QFileDialog.getSaveFileName(self, "Rapor Dosyasını Kaydet", "", "HTML Dosyası (*.html)")[0]
        if not file_path:
            return

        from datetime import datetime
        import numpy as np

        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        folder_name = os.path.basename(self.folder_path.text()) if self.folder_path.text() else "Bilinmeyen Klasör"
        sw_count = sum(1 for r in self.results if r.get('Details', {}).get('file_type') == 'solidworks')

        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dosya Karşılaştırma Raporu</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .header {{ background-color: #3498db; color: white; padding: 10px; border-radius: 5px; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .high {{ background-color: #a8e6cf; }}
                .medium {{ background-color: #dcedc1; }}
                .low {{ background-color: #ffd3b6; }}
                .none {{ background-color: #ffaaa5; }}
                .footer {{ margin-top: 30px; font-size: 0.8em; color: #7f8c8d; text-align: center; }}
                .sw-details {{ background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Gelişmiş Dosya Karşılaştırma Raporu</h1>
                <p>Oluşturulma Tarihi: {now}</p>
            </div>
            <div class="summary">
                <h2>Rapor Özeti</h2>
                <p><strong>Klasör:</strong> {folder_name}</p>
                <p><strong>Toplam Karşılaştırma:</strong> {len(self.results)}</p>
                <p><strong>SolidWorks Dosyaları:</strong> {sw_count}</p>
                <p><strong>Ortalama Benzerlik:</strong> {np.mean([float(r['Toplam']) for r in self.results]):.2f}%</p>
            </div>
            <h2>Karşılaştırma Sonuçları</h2>
            <table>
                <tr>
                    <th>Dosya 1</th>
                    <th>Dosya 2</th>
                    <th>Metadata</th>
                    <th>Hash</th>
                    <th>İçerik</th>
                    <th>Yapı</th>
                    <th>Toplam</th>
                    <th>Sonuç</th>
                </tr>
        """
        for result in self.results:
            total_score = float(result['Toplam'])
            css_class = 'none'
            if total_score >= 95:
                css_class = 'high'
            elif total_score >= 75:
                css_class = 'medium'
            elif total_score >= 25:
                css_class = 'low'

            html_content += f"""
                <tr class="{css_class}">
                    <td>{result['Dosya 1']}</td>
                    <td>{result['Dosya 2']}</td>
                    <td>{result['Metadata']}</td>
                    <td>{result['Hash']}</td>
                    <td>{result['İçerik']}</td>
                    <td>{result['Yapı']}</td>
                    <td>{result['Toplam']}</td>
                    <td>{result['Sonuç']}</td>
                </tr>
            """

        if sw_count > 0:
            html_content += """
            </table>
            <h2>SolidWorks Detaylı Analiz</h2>
            <p>SolidWorks dosyaları için detaylı analiz sonuçları:</p>
            """
            for result in self.results:
                details = result.get('Details', {})
                if details.get('file_type') == 'solidworks':
                    sw_details = details.get('details', {})
                    html_content += f"""
                    <div class="sw-details">
                        <h3>{result['Dosya 1']} ↔ {result['Dosya 2']}</h3>
                        <p><strong>Sonuç:</strong> {result['Sonuç']} ({float(result['Toplam']):.1f}%)</p>
                        <ul>
                            <li><strong>Feature Tree:</strong> {sw_details.get('feature_tree', 0):.1f}%</li>
                            <li><strong>Sketch Data:</strong> {sw_details.get('sketch_data', 0):.1f}%</li>
                            <li><strong>Geometry:</strong> {sw_details.get('geometry', 0):.1f}%</li>
                        </ul>
                        <p><strong>Değerlendirme:</strong></p>
                        <div style="background-color: #f5f5f5; padding: 10px; border-left: 4px solid #3498db;">
                            {self.detail_panel.get_sw_evaluation(details).replace('\n', '<br>')}
                        </div>
                    </div>
                    """
        else:
            html_content += """
            </table>
            """

        html_content += f"""
            <div class="footer">
                <p>Bu rapor Gelişmiş Dosya Karşılaştırıcı v{__version__} tarafından oluşturulmuştur.</p>
            </div>
        </body>
        </html>
        """

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        webbrowser.open('file://' + os.path.realpath(file_path))
        QMessageBox.information(self, "Başarılı", f"Rapor başarıyla oluşturuldu:\n{file_path}")

    def export_results(self):
        if not self.results:
            QMessageBox.information(self, "Bilgi", "Dışa aktarmak için sonuç bulunmuyor!")
            return

        file_path = QFileDialog.getSaveFileName(self, "CSV Dosyasını Kaydet", "", "CSV Dosyası (*.csv)")[0]
        if not file_path:
            return

        import csv
        fieldnames = ['Dosya 1', 'Dosya 2', 'Metadata', 'Hash', 'İçerik', 'Yapı', 'Toplam', 'Sonuç']
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                row = {k: result[k] for k in fieldnames}
                writer.writerow(row)

        QMessageBox.information(self, "Başarılı", f"Sonuçlar başarıyla dışa aktarıldı:\n{file_path}")

    def show_help(self):
        help_text = """
        GELIŞMIŞ DOSYA KARŞILAŞTIRICI YARDIM

        Kullanım:
        1. Bir klasör seçin
        2. Dosya tipini belirleyin (varsayılan: SolidWorks)
        3. Minimum benzerlik eşiğini ayarlayın
        4. "Başlat" butonuna tıklayın

        Özellikler:
        - SolidWorks dosyaları için optimize edilmiş karşılaştırma
        - Çok katmanlı analiz (metadata, hash, içerik, yapı)
        - Manipülasyon tespiti
        - Detaylı raporlar (HTML ve CSV)

        Sonuç Yorumlama:
        - 95-100%: Tam veya neredeyse aynı dosyalar
        - 75-95%: Çok benzer dosyalar
        - 50-75%: Orta benzerlik
        - 25-50%: Zayıf benzerlik
        - 0-25%: Farklı dosyalar
        """
        QMessageBox.information(self, "Yardım", help_text)

    def closeEvent(self, event):
        self.is_running = False
        if hasattr(self, 'comparison_thread'):
            self.comparison_thread.is_running = False
        event.accept()