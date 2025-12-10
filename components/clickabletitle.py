from PySide6.QtCore import Signal, Qt
from qfluentwidgets import TitleLabel

class ClickableTitleLabel(TitleLabel):
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)