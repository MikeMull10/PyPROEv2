from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit
)
from PySide6.QtCore import Qt

from stylesheet.stylesheet import get_stylesheet

class FormulationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Formulation")
        self.setFixedWidth(500)

        main = QVBoxLayout(self)

        # layout = QVBoxLayout(self)
        # layout.addWidget(QLabel("Formulation", alignment=Qt.AlignCenter))
        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)

        self.layout: QTextEdit = QTextEdit()

        main.addWidget(self.layout)
