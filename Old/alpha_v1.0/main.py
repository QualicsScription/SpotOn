# Main/main.py
import sys
from PyQt5.QtWidgets import QApplication
from src.ui.ui import ModernFileComparator  # Updated import path

if __name__ == "__main__":
    try:
        import logging
        logging.basicConfig(
            filename='file_comparator.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        app = QApplication(sys.argv)
        window = ModernFileComparator()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import logging
        from PyQt5.QtWidgets import QMessageBox
        logging.error(f"Uygulama hatası: {e}")
        QMessageBox.critical(None, "Kritik Hata", f"Uygulama hatası: {str(e)}")
        sys.exit(1)