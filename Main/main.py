# Main/main.py
import sys
from PyQt5.QtWidgets import QApplication
from src.ui.ui import ModernFileComparator  # Updated import path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernFileComparator()
    window.show()
    sys.exit(app.exec_())