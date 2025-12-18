from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QPainter, QFontMetrics
from qfluentwidgets import TitleLabel, SubtitleLabel, IconWidget, FluentIcon as FI

class ClickableTitleLabel(TitleLabel):
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class ClickableSubtitleLabel(SubtitleLabel):
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class ClickableSubtitleLabelIcon(QWidget):
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.showing = True  # True = pointing down, False = pointing right

        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Icon
        self.iconWidget = IconWidget(FI.CARE_DOWN_SOLID, self)
        self.iconWidget.setFixedSize(16, 16)

        # Text
        self.label = SubtitleLabel(text, self)

        layout.addWidget(self.iconWidget)
        layout.addWidget(self.label)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.showing ^= True
        self.iconWidget.setIcon(FI.CARE_DOWN_SOLID if self.showing else FI.CARE_RIGHT_SOLID)

        self.clicked.emit()
        super().mousePressEvent(event)