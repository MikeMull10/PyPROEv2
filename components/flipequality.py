from PySide6.QtGui import Qt
from qfluentwidgets import PushButton, FluentIcon as FI

class FlipEquality(PushButton):
    def __init__(self):
        super().__init__()
        self.setText("≤")
        self.leq = True  # False -> greater than / equal to
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.flip)
    
    def flip(self):
        self.leq ^= True
        self.setText("≤" if self.leq else "≥")
