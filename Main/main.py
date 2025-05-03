# Main/main.py - Beta 2.1.0
import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.ui import ModernFileComparator, __version__  # Import version

def setup_logging():
    """Configure logging for the application"""
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Dev', 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, 'file_comparator.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info(f"Starting SpotOn v{__version__}")
        return log_file
    except Exception as e:
        print(f"Logging configuration error: {e}")
        return 'file_comparator.log'  # Fallback to current directory

if __name__ == "__main__":
    try:
        import logging
        log_file = setup_logging()

        print(f"SpotOn Beta v{__version__} starting...")
        print(f"Logs will be saved to: {log_file}")

        app = QApplication(sys.argv)
        window = ModernFileComparator()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import logging
        from PyQt5.QtWidgets import QMessageBox
        logging.error(f"Application error: {e}")
        QMessageBox.critical(None, "Critical Error", f"Application error: {str(e)}")
        sys.exit(1)