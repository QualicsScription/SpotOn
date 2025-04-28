from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from src.resources.colors import BUTTON_COLOR, TEXT_COLOR

class TableView(QWidget):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tree = QTreeWidget()
        self.tree.setStyleSheet(f"QTreeWidget {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; }} "
                               f"QTreeWidget::item {{ border: none; }} "
                               f"QTreeWidget::header {{ background: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; }} "
                               f"QTreeWidget::branch {{ background: {BUTTON_COLOR}; border: none; }}")
        self.update_headers()
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.itemDoubleClicked.connect(self.parent.show_detail_view)
        layout.addWidget(self.tree)

    def update_headers(self):
        self.tree.setHeaderLabels([self.lang.get("file1"), self.lang.get("file2"), self.lang.get("metadata"),
                                   self.lang.get("hash"), self.lang.get("content"), self.lang.get("structure"),
                                   self.lang.get("total"), self.lang.get("result")])

    def clear(self):
        self.tree.clear()

    def add_result(self, res):
        item = QTreeWidgetItem([res['Dosya 1'], res['Dosya 2'], res['Metadata'], res['Hash'], res['İçerik'], res['Yapı'], res['Toplam'], res['Sonuç']])
        total_score = float(res['Toplam'])
        item.setBackground(0, QColor("#a8e6cf" if total_score >= 95 else "#dcedc1" if total_score >= 75 else "#ffd3b6" if total_score >= 25 else "#ffaaa5"))
        self.tree.addTopLevelItem(item)