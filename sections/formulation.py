from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit
)
from PySide6.QtCore import Qt

from qfluentwidgets import TextEdit

class FormulationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Formulation")
        self.setFixedWidth(500)

        main = QVBoxLayout(self)

        self.layout: TextEdit = TextEdit()

        main.addWidget(self.layout)
