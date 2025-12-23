from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import MessageBoxBase, ComboBox, SubtitleLabel
from enum import Enum

class SaveType(Enum):
    DOE = 0
    FNC = 1


class SavePopup(MessageBoxBase):
    def __init__(self, parent=None):
        """
        parent needs to be the main window
        """
        super().__init__(parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(15)

        layout.addWidget(SubtitleLabel("What do you want to save?"))

        self.drop = ComboBox()
        self.drop.addItems(["Save Design of Experiments", "Save Formulation"])
        layout.addWidget(self.drop)

        self.viewLayout.addWidget(container)
    
    def exec(self) -> tuple[bool, SaveType]:
        ok = super().exec()

        return ok, SaveType(self.drop.currentIndex())