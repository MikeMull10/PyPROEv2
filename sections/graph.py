from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QHBoxLayout, QPushButton, QTextEdit, QDialog, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from qfluentwidgets import TextEdit, PushButton


class MplWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, nav=False):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.points = []
        super().__init__(self.fig)
    
    def delete_fig(self):
        plt.close(self.fig)
    
    def __del__(self):
        self.delete_fig()

    def plot(self, points):
        self.points = points
        self.axes.scatter(*[points[:, i] for i in range(len(points[0]))])

class ToggleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stack = QStackedWidget()

        self.text_edit = TextEdit()
        self.text_edit.setPlaceholderText("Results...")

        self.graph = MplWidget()

        self.stack.addWidget(self.text_edit)  # index 0
        self.stack.addWidget(self.graph)      # index 1

        self.btns = QHBoxLayout()

        self.toggle_btn = PushButton("Toggle View")
        self.toggle_btn.clicked.connect(self.toggle_view)

        self.popout_btn = PushButton("View in Fullscreen")
        self.popout_btn.clicked.connect(self.create_popout)

        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.popout_btn.setCursor(Qt.PointingHandCursor)

        self.btns.addWidget(self.toggle_btn)
        self.btns.addWidget(self.popout_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        layout.addLayout(self.btns)

        self.setLayout(layout)

        self.stack.setCurrentIndex(0)

    def toggle_view(self):
        current = self.stack.currentIndex()
        self.stack.setCurrentIndex(1 if current == 0 else 0)
    
    def create_popout(self):
        if self.stack.currentIndex() == 0:
            self.show_text_popup()
        else:
            self.show_graph_popup()

    def show_text_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Text")
        dialog.resize(800, 600)
        layout = QVBoxLayout(dialog)

        editor = TextEdit()
        editor.setPlainText(self.text_edit.toPlainText())  # copy current text
        layout.addWidget(editor)

        save_btn = PushButton("Close")
        layout.addWidget(save_btn)

        def save_and_close():
            self.text_edit.setPlainText(editor.toPlainText())  # push changes back
            dialog.accept()

        save_btn.clicked.connect(save_and_close)

        dialog.exec()

    def show_graph_popup(self):
        dialog = QDialog()
        dialog.setWindowTitle("Optimization Results Graph")
        layout = QVBoxLayout()

        graphWidget = MplWidget(self, width=5, height=4, dpi=100)

        single = len(self.graph.points) == 1
        x = [p[0] for p in self.graph.points]
        y = [p[1] for p in self.graph.points]

        graphWidget.axes.scatter(x, y, c="b", marker="o", s=20 if single else 5)
        graphWidget.axes.set_title("Pareto Front" if not single else "Solution")
        graphWidget.axes.set_xlabel("$f_1(x)$" if not single else "$X_1$")
        graphWidget.axes.set_ylabel("$f_2(x)$" if not single else "$X_2$")
        graphWidget.axes.grid(True)

        toolbar = NavigationToolbar(graphWidget, dialog)
        toolbar.setStyleSheet(
            """
            QToolButton {
                background-color: transparent;
                color: white;
            }
        """
        )
        for child in toolbar.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("color: white;")

        layout.addWidget(toolbar)
        layout.addWidget(graphWidget)
        dialog.setLayout(layout)

        dialog.exec()
