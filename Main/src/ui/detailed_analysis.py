from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit
from src.resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR, ACCENT_COLOR
from src.core.utils import get_file_info

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
        file_layout = QHBoxLayout(file_info_tab)
        file_layout.setContentsMargins(0, 0, 0, 0)
        self.file1_info = QTextEdit()
        self.file2_info = QTextEdit()
        for w in [self.file1_info, self.file2_info]:
            w.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; font-size: 12px;")
            file_layout.addWidget(w)
        self.addTab(file_info_tab, self.lang.get("file_info"))
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(comparison_tab)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        self.comparison_text = QTextEdit()
        self.comparison_text.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; font-size: 12px;")
        comparison_layout.addWidget(self.comparison_text)
        self.addTab(comparison_tab, self.lang.get("comparison_details"))

    def update_details(self, res):
        self.file1_info.setText(get_file_info(res['Path1']))
        self.file2_info.setText(get_file_info(res['Path2']))
        details = res['Details']
        text = (f"🔍 {self.lang.get('detailed_comparison')}\n==========================\n"
                f"{self.lang.get('file1')}: {res['Dosya 1']}\n"
                f"{self.lang.get('file2')}: {res['Dosya 2']}\n"
                f"{self.lang.get('total_similarity')}: {details['total']:.2f}%\n"
                f"{self.lang.get('result')}: {details['category']}\n"
                f"{self.lang.get('file_type')}: {details['file_type']}\n\n"
                f"📊 {self.lang.get('weighted_scores')}:\n"
                f"- {self.lang.get('metadata')}: {details['metadata']:.2f}%\n"
                f"- {self.lang.get('hash')}: {details['hash']:.2f}%\n"
                f"- {self.lang.get('content')}: {details['content']:.2f}%\n"
                f"- {self.lang.get('structure')}: {details['structure']:.2f}%\n\n"
                f"🔎 {self.lang.get('manipulation_analysis')}:\n"
                f"- {self.lang.get('detection')}: {'Evet' if details['manipulation']['detected'] else 'Hayır'}\n"
                f"- {self.lang.get('score')}: {details['manipulation']['score']:.2f}%\n"
                f"- {self.lang.get('type')}: {details['manipulation']['type']}")
        if details['file_type'] == 'solidworks' and 'details' in details:
            sw_details = details['details']
            text += (f"\n\n📊 {self.lang.get('solidworks_detailed_analysis')}:\n---------------------------\n"
                     f"- {self.lang.get('feature_tree')}: {sw_details.get('feature_tree', 0):.2f}%\n"
                     f"- {self.lang.get('sketch_data')}: {sw_details.get('sketch_data', 0):.2f}%\n"
                     f"- {self.lang.get('geometry')}: {sw_details.get('geometry', 0):.2f}%")
        self.comparison_text.setText(text)

    def update_texts(self):
        self.setTabText(0, self.lang.get("file_info"))
        self.setTabText(1, self.lang.get("comparison_details"))

    def clear(self):
        self.file1_info.clear()
        self.file2_info.clear()
        self.comparison_text.clear()