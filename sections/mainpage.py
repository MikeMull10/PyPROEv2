from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from qfluentwidgets import ScrollArea, FluentStyleSheet, Theme, TitleLabel


class MainPage(QWidget):
    def __init__(self, formpage=None, doepage=None, metapage=None, optpage=None):
        super().__init__()

        self.setObjectName("Main")

        main = QHBoxLayout(self)

        left = QVBoxLayout()
        left.addWidget(formpage)

        right = QVBoxLayout()
        if doepage:
            right.addWidget(doepage)
        if metapage:
            right.addWidget(metapage)
        if optpage:
            right.addWidget(optpage)
        
        left.setContentsMargins(0, 0, 0, 0)
        right.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        right.setSpacing(0)

        main.addLayout(left)
        main.addLayout(right)
