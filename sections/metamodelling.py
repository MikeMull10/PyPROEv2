from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt

class MetamodelPage(QWidget):
    def __init__(self, setMaxWidth=False):
        super().__init__()

        self.setObjectName("Metamodel")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Metamodel", alignment=Qt.AlignCenter))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
