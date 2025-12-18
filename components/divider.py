from PySide6.QtWidgets import QFrame
from qfluentwidgets import Theme

"""
divider = QFrame()
divider.setFrameShape(QFrame.HLine)
divider.setFrameShadow(QFrame.Sunken)
divider.setFixedHeight(1)
divider.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
main_layout.addWidget(divider)
"""

class Divider(QFrame):
    def __init__(self, style: Theme=Theme.LIGHT, parent=None):
        super().__init__(parent=parent)
        self.style: Theme = style
        
        self.opacity = 100
        self.margin_left = 15
        self.margin_right = 50

        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setFixedHeight(2)
        
        self.update_style()

    def update_style(self):
        color = "255, 255, 255" if self.style == Theme.DARK else "0, 0, 0"
        self.setStyleSheet(f"background-color: rgba({color}, {self.opacity}); margin-left: {self.margin_left}px; margin-right: {self.margin_right}px;")