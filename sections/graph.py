from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MplWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, nav=False):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
    
    def delete_fig(self):
        plt.close(self.fig)
    
    def __del__(self):
        self.delete_fig()


class ToggleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # stacked widget
        self.stack = QStackedWidget()

        # text widget
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Results...")

        # graph widget
        self.graph = MplWidget()
        # self.graph.axes.plot([0, 1, 2, 3], [10, 1, 20, 3])  # example plot

        # add both to stack
        self.stack.addWidget(self.text_edit)  # index 0
        self.stack.addWidget(self.graph)      # index 1

        # toggle button
        self.toggle_btn = QPushButton("Toggle View")
        self.toggle_btn.clicked.connect(self.toggle_view)

        # layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)
        layout.addWidget(self.toggle_btn)

        self.setLayout(layout)

        # start with text
        self.stack.setCurrentIndex(0)

    def toggle_view(self):
        current = self.stack.currentIndex()
        self.stack.setCurrentIndex(1 if current == 0 else 0)
