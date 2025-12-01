from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class MainPage(QWidget):
    def __init__(self, formpage=None, doepage=None, metapage=None, optpage=None):
        super().__init__()

        self.setObjectName("main")

        # --- Central widget with scrollable pages ---
        container = QWidget()
        v_container = QWidget()
        hbox = QHBoxLayout(container)
        vbox = QVBoxLayout(v_container)
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        vbox.setSpacing(0)

        # Add sub-pages
        if doepage:
            vbox.addWidget(doepage)
        if metapage:
            vbox.addWidget(metapage)
        if optpage:
            vbox.addWidget(optpage)

        if formpage:
            hbox.addWidget(formpage)
        hbox.addWidget(v_container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        # --- Add scroll area to the layout of this QWidget ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
