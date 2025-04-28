# Main/src/ui/visual_analysis.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR

class VisualAnalysis(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        layout.addWidget(self.stats_text)

    def update_visual_analysis(self, results):
        self.ax.clear()
        if not results:
            self.canvas.draw()
            return

        scores = [float(r['Toplam']) for r in results]
        similarity_ranges = {}
        for score in scores:
            if score >= 95: similarity_ranges.setdefault('95-100', 0); similarity_ranges['95-100'] += 1
            elif score >= 75: similarity_ranges.setdefault('75-95', 0); similarity_ranges['75-95'] += 1
            elif score >= 50: similarity_ranges.setdefault('50-75', 0); similarity_ranges['50-75'] += 1
            elif score >= 25: similarity_ranges.setdefault('25-50', 0); similarity_ranges['25-50'] += 1
            else: similarity_ranges.setdefault('0-25', 0); similarity_ranges['0-25'] += 1

        labels = [f"{k}% ({v})" for k, v in sorted(similarity_ranges.items())]
        sizes = [similarity_ranges[k] for k in sorted(similarity_ranges.keys())]

        if sizes:
            self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            self.ax.axis('equal')
            self.canvas.draw()

        stats_text = f"""📊 BENZERLIK İSTATISTIKLERI 📊
==============================
Toplam Karşılaştırma: {len(results)}
Ortalama Benzerlik: {np.mean([float(r['Toplam']) for r in results]):.2f}%
Maksimum: {max(float(r['Toplam']) for r in results):.2f}%
Minimum: {min(float(r['Toplam']) for r in results):.2f}%
=============================="""
        self.stats_text.setText(stats_text)

    def clear_visual_analysis(self):
        self.ax.clear()
        self.canvas.draw()
        self.stats_text.clear()