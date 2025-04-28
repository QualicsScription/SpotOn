import sys
from PyQt5.QtWidgets import QApplication
from src.ui.ui import ModernFileComparator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernFileComparator()
    window.show()
    sys.exit(app.exec_())