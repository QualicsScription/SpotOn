import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from src.resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR

class VisualAnalysis(QWidget):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig, self.ax = plt.subplots(figsize=(6, 4), facecolor=BACKGROUND_COLOR)
        self.fig.set_facecolor(BACKGROUND_COLOR)
        self.ax.set_facecolor(BACKGROUND_COLOR)
        self.ax.tick_params(colors=TEXT_COLOR)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        layout.addWidget(self.canvas)
        self.stats_text = QTextEdit()
        self.stats_text.setStyleSheet(f"background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; border: none; font-size: 12px;")
        self.stats_text.setMinimumHeight(150)
        layout.addWidget(self.stats_text)

    def update_visual(self, results):
        if not results:
            return
        self.ax.clear()
        scores = [float(r['Toplam']) for r in results]
        similarity_ranges = {'95-100': 0, '75-95': 0, '50-75': 0, '25-50': 0, '0-25': 0}
        for score in scores:
            similarity_ranges['95-100' if score >= 95 else '75-95' if score >= 75 else '50-75' if score >= 50 else '25-50' if score >= 25 else '0-25'] += 1
        labels, sizes = zip(*[(f"{k}% ({v})", v) for k, v in similarity_ranges.items() if v > 0])
        if sizes:
            self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, textprops={'color': TEXT_COLOR, 'fontsize': 10})
            self.ax.axis('equal')
            self.canvas.draw()
        self.stats_text.setText(f"📊 {self.lang.get('similarity_stats')}\n==============================\n"
                                f"{self.lang.get('total_comparisons')}: {len(results)}\n"
                                f"{self.lang.get('average_similarity')}: {np.mean(scores):.2f}%\n"
                                f"{self.lang.get('maximum')}: {max(scores):.2f}%\n"
                                f"{self.lang.get('minimum')}: {min(scores):.2f}%\n==============================")

    def clear(self):
        self.ax.clear()
        self.canvas.draw()
        self.stats_text.clear()