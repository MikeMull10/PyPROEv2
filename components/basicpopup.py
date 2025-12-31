from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from qfluentwidgets import MessageBoxBase, BodyLabel, SubtitleLabel


class BasicPopup(MessageBoxBase):
    def __init__(self, parent, title: str | None=None, message: str | None=None, hide_cancel: bool=True):
        """
        parent needs to be the main window
        """
        super().__init__(parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(15)

        if title: layout.addWidget(SubtitleLabel(title))
        if message: layout.addWidget(BodyLabel(message))

        self.viewLayout.addWidget(container)
        self.yesButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.setCursor(Qt.PointingHandCursor)
        if hide_cancel: self.cancelButton.hide()
    