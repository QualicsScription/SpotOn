# Main/src/ui/table_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from ..resources.colors import BUTTON_COLOR, TEXT_COLOR

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
        self.tree.setHeaderLabels([self.lang.translate("file1"), self.lang.translate("file2"), self.lang.translate("metadata"),
                                  self.lang.translate("hash"), self.lang.translate("content"), self.lang.translate("structure"),
                                  self.lang.translate("total"), self.lang.translate("result")])

    def clear(self):
        self.tree.clear()

    def add_result(self, res):
        """Sonuç tablosuna yeni bir satır ekler."""
        try:
            # Dosya adlarını al
            file1 = res.get('file1', '')
            file2 = res.get('file2', '')

            # Diğer değerleri al, yoksa N/A kullan
            metadata = res.get('metadata', 'N/A')
            hash_val = res.get('hash', 'N/A')
            content = res.get('content', 'N/A')
            structure = res.get('structure', 'N/A')
            total = res.get('total', '0')
            category = res.get('category', 'N/A')

            # Tablo satırını oluştur
            item = QTreeWidgetItem([file1, file2, str(metadata), str(hash_val),
                                   str(content), str(structure), str(total), str(category)])

            # Benzerlik skoruna göre renklendirme
            try:
                total_score = float(total)
                color = "#a8e6cf" if total_score >= 95 else \
                        "#dcedc1" if total_score >= 75 else \
                        "#ffd3b6" if total_score >= 50 else \
                        "#ffaaa5" if total_score >= 25 else \
                        "#ff8b94"

                # Tüm hücreleri renklendir
                for i in range(8):
                    item.setBackground(i, QColor(color))
            except:
                pass

            # Tabloya ekle
            self.tree.addTopLevelItem(item)

        except Exception as e:
            import logging
            logging.error(f"Tablo satırı ekleme hatası: {e}")