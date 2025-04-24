from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvasQTAgg(Figure(figsize=(10, 10), dpi=100))
        vertical_layout = QVBoxLayout()
        #vertical_layout.setSpacing(0)
        vertical_layout.addWidget(self.canvas)
        self.canvas.axes = self.canvas.figure.add_subplot(1, 1, 1)
        self.setLayout(vertical_layout)