# Main/src/ui/table_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from ..resources.colors import BUTTON_COLOR, TEXT_COLOR

class TableView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Dosya 1', 'Dosya 2', 'Metadata', 'Hash', 'İçerik', 'Yapı', 'Toplam', 'Sonuç'])
        self.tree.setStyleSheet(f"color: {TEXT_COLOR};")
        for i in range(self.tree.columnCount()):
            self.tree.header().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.tree.itemDoubleClicked.connect(self.show_detail_view)
        layout.addWidget(self.tree)

    def show_results(self, results):
        self.tree.clear()
        for res in results:
            total_score = float(res['Toplam'])
            item = QTreeWidgetItem([
                res['Dosya 1'],
                res['Dosya 2'],
                res['Metadata'],
                res['Hash'],
                res['İçerik'],
                res['Yapı'],
                res['Toplam'],
                res['Sonuç']
            ])
            if total_score >= 95:
                item.setBackground(0, QColor('#a8e6cf'))
            elif total_score >= 75:
                item.setBackground(0, QColor('#dcedc1'))
            elif total_score >= 25:
                item.setBackground(0, QColor('#ffd3b6'))
            else:
                item.setBackground(0, QColor('#ffaaa5'))
            self.tree.addTopLevelItem(item)

    def clear_results(self):
        self.tree.clear()

    def show_detail_view(self, item, column):
        for res in self.parent.results:
            if res['Dosya 1'] == item.text(0) and res['Dosya 2'] == item.text(1):
                self.parent.notebook.setCurrentWidget(self.parent.detail_panel)
                self.parent.detail_panel.update_details(res)
                break