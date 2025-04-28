# Main/src/ui/detailed_analysis.py
from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR, ACCENT_COLOR
from ..core.utils import get_file_info

class DetailedAnalysis(QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Dosya bilgileri
        file_info_tab = QWidget()
        file_layout = QHBoxLayout(file_info_tab)

        file1_frame = QWidget()
        file1_layout = QVBoxLayout(file1_frame)
        file1_layout.addWidget(QLabel("Dosya 1:"))
        self.file1_info = QTextEdit()
        self.file1_info.setReadOnly(True)
        self.file1_info.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        file1_layout.addWidget(self.file1_info)
        file_layout.addWidget(file1_frame)

        file2_frame = QWidget()
        file2_layout = QVBoxLayout(file2_frame)
        file2_layout.addWidget(QLabel("Dosya 2:"))
        self.file2_info = QTextEdit()
        self.file2_info.setReadOnly(True)
        self.file2_info.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        file2_layout.addWidget(self.file2_info)
        file_layout.addWidget(file2_frame)

        self.addTab(file_info_tab, "Dosya Bilgileri")

        # Karşılaştırma detayları
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(comparison_tab)
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        comparison_layout.addWidget(self.comparison_text)
        self.addTab(comparison_tab, "Karşılaştırma Detayları")

    def update_details(self, file_data):
        self.file1_info.setText(get_file_info(file_data['Path1']))
        self.file2_info.setText(get_file_info(file_data['Path2']))

        details = file_data['Details']
        file_type = details.get('file_type', 'unknown')

        text = f"""
🔍 Detaylı Karşılaştırma 🔍
==========================
Dosya 1: {file_data['Dosya 1']}
Dosya 2: {file_data['Dosya 2']}
Toplam Benzerlik: {details['total']:.2f}%
Sonuç: {details['category']}
Dosya Tipi: {file_type}

📊 Ağırlıklı Skorlar:
- Metadata: {details['metadata']:.2f}%
- Hash: {details['hash']:.2f}%
- İçerik: {details['content']:.2f}%
- Yapı: {details['structure']:.2f}%

🔎 Manipülasyon Analizi:
- Tespit: {'Evet' if details['manipulation']['detected'] else 'Hayır'}
- Skor: {details['manipulation']['score']:.2f}%
- Tür: {details['manipulation']['type']}
        """
        if file_type == 'solidworks' and 'details' in details:
            sw_details = details['details']
            text += f"""

📊 SolidWorks Detaylı Analiz:
---------------------------
- Feature Tree: {sw_details.get('feature_tree', 0):.2f}%
- Sketch Data: {sw_details.get('sketch_data', 0):.2f}%
- Geometry: {sw_details.get('geometry', 0):.2f}%

Değerlendirme:
{self.get_sw_evaluation(details)}
            """
        self.comparison_text.setText(text)

    def get_sw_evaluation(self, details):
        if not details or 'details' not in details:
            return "Değerlendirme yapılamadı."

        sw_details = details['details']
        feature_tree = sw_details.get('feature_tree', 0)
        sketch_data = sw_details.get('sketch_data', 0)
        geometry = sw_details.get('geometry', 0)
        total = details.get('total', 0)

        if total > 98:
            return "Dosyalar birebir aynı veya çok küçük farklılıklar içeriyor."

        evaluation = []

        if feature_tree > 95:
            evaluation.append("Feature ağacı neredeyse aynı.")
        elif feature_tree > 90 and geometry < 80:
            evaluation.append("Feature ağacı benzer ancak geometride değişiklikler var.")
        elif feature_tree < 70 and geometry > 90:
            evaluation.append("Geometri benzer ancak feature ağacında önemli değişiklikler var.")
        elif feature_tree < 50:
            evaluation.append("Feature ağaçları önemli ölçüde farklı.")

        if sketch_data > 90:
            evaluation.append("Sketch verileri neredeyse aynı.")
        elif sketch_data > 70:
            evaluation.append("Sketch verilerinde küçük değişiklikler var.")
        elif sketch_data < 40:
            evaluation.append("Sketch verileri önemli ölçüde farklı.")

        if geometry > 95:
            evaluation.append("Geometri neredeyse aynı.")
        elif geometry > 80:
            evaluation.append("Geometride küçük değişiklikler var.")
        elif geometry < 50:
            evaluation.append("Geometri önemli ölçüde farklı.")

        if feature_tree > 85 and sketch_data > 85 and geometry > 85:
            evaluation.append("Dosya muhtemelen 'Save As' ile oluşturulmuş.")
        elif feature_tree > 90 and sketch_data > 70 and geometry < 60:
            evaluation.append("Dosya aynı feature ağacı kullanılarak farklı geometri ile yeniden oluşturulmuş.")
        elif feature_tree < 50 and sketch_data < 50 and geometry > 90:
            evaluation.append("Dosyalar farklı yöntemlerle oluşturulmuş ancak benzer geometriye sahip.")

        if not evaluation:
            if total > 70:
                evaluation.append("Dosyalar benzer ancak çeşitli değişiklikler içeriyor.")
            else:
                evaluation.append("Dosyalar arasında önemli farklılıklar var.")

        return "\n".join(evaluation)

    def clear_details(self):
        self.file1_info.clear()
        self.file2_info.clear()
        self.comparison_text.clear()