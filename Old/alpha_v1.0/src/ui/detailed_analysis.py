# Main/src/ui/detailed_analysis.py
from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR, ACCENT_COLOR
from ..core.utils import get_file_info
from ..languages.languages import LanguageManager

class DetailedAnalysis(QTabWidget):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"QTabWidget {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; border: none; }} "
                          f"QTabBar::tab {{ background: {BUTTON_COLOR}; color: {TEXT_COLOR}; padding: 5px; font-size: 12px; }} "
                          f"QTabBar::tab:selected {{ background: {ACCENT_COLOR}; color: {TEXT_COLOR}; }}")
        file_info_tab = QWidget()
        file_info_layout = QHBoxLayout(file_info_tab)
        file_info_layout.setContentsMargins(0, 0, 0, 0)
        self.file1_info = QTextEdit()
        self.file2_info = QTextEdit()
        for w in [self.file1_info, self.file2_info]:
            w.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; font-size: 12px;")
            file_info_layout.addWidget(w)
        self.addTab(file_info_tab, self.lang.translate("file_info"))
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(comparison_tab)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        self.comparison_text = QTextEdit()
        self.comparison_text.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; font-size: 12px;")
        comparison_layout.addWidget(self.comparison_text)
        self.addTab(comparison_tab, self.lang.translate("comparison_details"))

    def update_details(self, res):
        self.file1_info.setText(get_file_info(res['Path1']))
        self.file2_info.setText(get_file_info(res['Path2']))
        details = res['Details']

        # Ana sonuç değerlerini al, yoksa res sözlüğünden veya varsayılan değer kullan
        total = details.get('total', float(res.get('total', 0)))
        category = details.get('category', res.get('category', 'N/A'))
        file_type = details.get('file_type', 'unknown')

        # Ağırlıklı skorları al, yoksa varsayılan değer kullan
        metadata = details.get('metadata', float(res.get('metadata', 0)))
        hash_val = details.get('hash', float(res.get('hash', 0)))
        content = details.get('content', float(res.get('content', 0)))
        structure = details.get('structure', float(res.get('structure', 0)))

        # Manipülasyon analizi için güvenli erişim
        manipulation = details.get('manipulation', {})
        detected = manipulation.get('detected', False) if isinstance(manipulation, dict) else False
        manip_score = manipulation.get('score', 0) if isinstance(manipulation, dict) else 0
        manip_type = manipulation.get('type', 'N/A') if isinstance(manipulation, dict) else 'N/A'

        text = (f"🔍 {self.lang.translate('detailed_comparison')}\n==========================\n"
                f"{self.lang.translate('file1')}: {res['file1']}\n"
                f"{self.lang.translate('file2')}: {res['file2']}\n"
                f"{self.lang.translate('total_similarity')}: {total:.2f}%\n"
                f"{self.lang.translate('result')}: {category}\n"
                f"{self.lang.translate('file_type')}: {file_type}\n\n"
                f"📊 {self.lang.translate('weighted_scores')}:\n"
                f"- {self.lang.translate('metadata')}: {metadata:.2f}%\n"
                f"- {self.lang.translate('hash')}: {hash_val:.2f}%\n"
                f"- {self.lang.translate('content')}: {content:.2f}%\n"
                f"- {self.lang.translate('structure')}: {structure:.2f}%\n\n"
                f"🔎 {self.lang.translate('manipulation_analysis')}:\n"
                f"- {self.lang.translate('detection')}: {'Evet' if detected else 'Hayır'}\n"
                f"- {self.lang.translate('score')}: {manip_score:.2f}%\n"
                f"- {self.lang.translate('type')}: {manip_type}")
        if file_type == 'solidworks' and 'details' in details:
            sw_details = details['details']
            text += (f"\n\n📊 {self.lang.translate('solidworks_detailed_analysis')}:\n---------------------------\n"
                     f"- {self.lang.translate('feature_tree')}: {sw_details.get('feature_tree', 0):.2f}%\n"
                     f"- {self.lang.translate('sketch_data')}: {sw_details.get('sketch_data', 0):.2f}%\n"
                     f"- {self.lang.translate('geometry')}: {sw_details.get('geometry', 0):.2f}%")
        self.comparison_text.setText(text)

    def update_texts(self):
        self.setTabText(0, self.lang.translate("file_info"))
        self.setTabText(1, self.lang.translate("comparison_details"))

    def clear(self):
        """Detaylı analiz panelindeki bilgileri temizler."""
        self.file1_info.clear()
        self.file2_info.clear()
        self.comparison_text.clear()