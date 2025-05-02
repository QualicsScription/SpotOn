# Main/src/ui/visual_analysis.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from ..resources.colors import BACKGROUND_COLOR, TEXT_COLOR, BUTTON_COLOR

class VisualAnalysis(QWidget):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.parent = parent
        self.lang = lang
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
        """Görsel analiz panelini günceller."""
        self.ax.clear()
        if not results:
            self.canvas.draw()
            return

        try:
            scores = [float(r['total']) for r in results]
            similarity_ranges = {'95-100': 0, '75-95': 0, '50-75': 0, '25-50': 0, '0-25': 0}

            for score in scores:
                if score >= 95:
                    similarity_ranges['95-100'] += 1
                elif score >= 75:
                    similarity_ranges['75-95'] += 1
                elif score >= 50:
                    similarity_ranges['50-75'] += 1
                elif score >= 25:
                    similarity_ranges['25-50'] += 1
                else:
                    similarity_ranges['0-25'] += 1

            # Sadece değeri 0'dan büyük olan aralıkları göster
            filtered_ranges = {k: v for k, v in similarity_ranges.items() if v > 0}

            if filtered_ranges:
                labels = [f"{k}% ({v})" for k, v in sorted(filtered_ranges.items())]
                sizes = [filtered_ranges[k] for k in sorted(filtered_ranges.keys())]

                # Renk paleti
                colors = ['#a8e6cf', '#dcedc1', '#ffd3b6', '#ffaaa5', '#ff8b94']

                self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True,
                           startangle=90, colors=colors, textprops={'color': TEXT_COLOR})
                self.ax.axis('equal')

            self.canvas.draw()

            # İstatistik metnini güncelle
            stats_text = f"""📊 {self.lang.translate('similarity_stats')} 📊
==============================
{self.lang.translate('total_comparisons')}: {len(results)}
{self.lang.translate('average_similarity')}: {np.mean(scores):.2f}%
{self.lang.translate('maximum')}: {max(scores):.2f}%
{self.lang.translate('minimum')}: {min(scores):.2f}%
=============================="""
            self.stats_text.setText(stats_text)

        except Exception as e:
            import logging
            logging.error(f"Görsel analiz hatası: {e}")
            self.stats_text.setText(f"Görsel analiz hatası: {str(e)}")

    def clear_visual_analysis(self):
        self.ax.clear()
        self.canvas.draw()
        self.stats_text.clear()