import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QStatusBar, QToolBar, QPushButton, QGridLayout,
    QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt
from stylesheet.colors import *


class MiniPage(QWidget):
    """A simple mini-page widget with a title and placeholder content."""
    def __init__(self, title: str, color: str):
        super().__init__()

        self.setStyleSheet(f"background-color: {color}; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # remove padding inside the widget
        layout.setSpacing(0)                   # remove spacing between items in layout
        
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.setWindowTitle("PyPROE X")
        self.setGeometry(200, 200, 600, 400)  # x, y, width, height
        self.showMaximized()

        # --- Central widget ---
        self.central = QWidget()
        self.grid = QGridLayout(self.central)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)

        # 2x2 Pages
        self.grid.addWidget(MiniPage("Page 1", RED_3), 0, 0)
        self.grid.addWidget(MiniPage("Page 2", ORANGE_3), 0, 1)
        self.grid.addWidget(MiniPage("Page 3", YELLOW_3), 1, 0)
        self.grid.addWidget(MiniPage("Page 4", GREEN_3), 1, 1)

        self.setCentralWidget(self.central)
