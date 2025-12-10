from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize

from qfluentwidgets import MessageBoxBase, PushButton, PlainTextEdit

def clamp_text(text: str, size: int):
    ret = ""
    size -= 3

    if len(text) > size:
        ret += text[:int((2/3) * size)]
        ret += "..."
        ret += text[-int((1/3) * size):]
    else:
        ret = text

    return ret


class EquationEditorDialog(MessageBoxBase):
    def __init__(self, initial_text: str = "", parent=None):
        super().__init__(parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(15)

        self.text_area = PlainTextEdit(self)
        self.text_area.setPlaceholderText("*equation here*")
        self.text_area.setPlainText(initial_text)

        # Get base size of the Application window and scale down a bit
        base_size: QSize = parent.size()
        base_x, base_y = map(int, [0.9 * base_size.width(), 0.8 * base_size.height()])
        self.text_area.setFixedWidth(base_x)
        self.text_area.setFixedHeight(base_y)

        layout.addWidget(self.text_area)

        # Add main body to dialog
        self.viewLayout.addWidget(container)

    def get_equation_text(self):
        return self.text_area.toPlainText()


class EquationButton(PushButton):
    def __init__(self, equation_text: str = "", parent=None):
        super().__init__()

        self.equation_text = equation_text
        self.display_text = ""
        self.parent = parent

        self.set_display_text()
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)

        self.clicked.connect(self.open_editor)

    def set_display_text(self):
        t = self.equation_text.replace("\n", "").strip()
        if t:
            self.display_text = clamp_text(t, 40)
            self.setText(self.display_text)

    def set_equation(self, text: str):
        self.equation_text = text
        self.set_display_text()

    def open_editor(self):
        dialog = EquationEditorDialog(self.equation_text, self.parent)
        if dialog.exec():
            self.set_equation(dialog.get_equation_text())
