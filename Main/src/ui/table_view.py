# Main/src/ui/table_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

class TableView(QWidget):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)

    def clear(self):
        self.table.clear()

    def add_result(self, result):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(result['file1']))
        self.table.setItem(row, 1, QTableWidgetItem(result['file2']))
        self.table.setItem(row, 2, QTableWidgetItem(str(result['total'])))
        self.table.setItem(row, 3, QTableWidgetItem(result['result']))