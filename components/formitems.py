from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt

from qfluentwidgets import LineEdit, TextEdit, EditableComboBox, TitleLabel, SubtitleLabel, BodyLabel, PushButton, ToolButton, FluentIcon as FI

from components.equationbutton import EquationButton
from components.flipequality import FlipEquality

class DefaultItem(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
    
    def add_btns(self):
        self.up_arrow = ToolButton(FI.UP)
        self.down_arrow = ToolButton(FI.DOWN)
        self.remove_btn = ToolButton(FI.CLOSE)
        [btn.setCursor(Qt.PointingHandCursor) for btn in [self.up_arrow, self.down_arrow, self.remove_btn]]

        self.layout.addStretch()
        self.layout.addWidget(self.up_arrow)
        self.layout.addWidget(self.down_arrow)
        self.layout.addWidget(self.remove_btn)


class VariableItem(DefaultItem):
    def __init__(self, var_name: str, min_value: float = 0.0, max_value: float = 1.0):
        super().__init__()

        self.name = var_name
        self.min_value = min_value
        self.max_value = max_value

        self.min_box = LineEdit()
        self.min_box.setText(str(min_value))
        self.max_box = LineEdit()
        self.max_box.setText(str(max_value))
        self.var_box = LineEdit()
        self.var_box.setText(str(var_name))
        self.var_box.setFixedWidth(75)

        self.layout.addWidget(self.min_box)
        self.layout.addWidget(SubtitleLabel("≤"))
        self.layout.addWidget(self.var_box)
        self.layout.addWidget(SubtitleLabel("≤"))
        self.layout.addWidget(self.max_box)

        self.add_btns()

class ConstantItem(DefaultItem):
    def __init__(self, name: str, value: float):
        super().__init__()

        self.name = name
        self.value = value

        self.name_box = LineEdit()
        self.name_box.setText(self.name)
        self.name_box.setFixedWidth(75)
        self.value_box = LineEdit()
        self.value_box.setText(str(self.value))

        self.layout.addWidget(self.name_box)
        self.layout.addWidget(SubtitleLabel("="))
        self.layout.addWidget(self.value_box)
        self.layout.addWidget(SubtitleLabel(";"))

        self.add_btns()

class ObjectiveItem(DefaultItem):
    def __init__(self, name: str, value: float, value_options: list = []):
        super().__init__()

        self.name = name
        self.value = value

        self.name_box = LineEdit()
        self.name_box.setText(self.name)
        self.name_box.setFixedWidth(75)
        self.value_box = EditableComboBox()
        if value_options: self.value_box.addItems(value_options)
        self.value_box.setText(str(self.value))

        self.layout.addWidget(self.name_box)
        self.layout.addWidget(SubtitleLabel("="))
        self.layout.addWidget(self.value_box)
        self.layout.addWidget(SubtitleLabel(";"))

        self.add_btns()

    def update_options(self):
        ...

class EqualityItem(DefaultItem):
    def __init__(self, name: str, value: float, eq_value: float, parent=None):
        super().__init__()

        self.name = name
        self.value = value
        self.eq_value = eq_value
        self.parent = parent

        self.name_box = LineEdit()
        self.name_box.setText(self.name)
        self.name_box.setFixedWidth(75)
        self.value_box = EditableComboBox()
        self.value_box.setText(str(self.value))
        self.eq_box = LineEdit()
        self.eq_box.setText(str(self.eq_value))

        self.layout.addWidget(self.name_box)
        self.layout.addWidget(SubtitleLabel(":"))
        self.layout.addWidget(self.value_box)
        self.layout.addWidget(SubtitleLabel("="))
        self.layout.addWidget(self.eq_box)
        self.layout.addWidget(SubtitleLabel(";"))

        self.add_btns()

class InequalityItem(DefaultItem):
    def __init__(self, name: str, value: float, eq_value: float, parent=None):
        super().__init__()

        self.name = name
        self.value = value
        self.eq_value = eq_value
        self.parent = parent

        self.name_box = LineEdit()
        self.name_box.setText(self.name)
        self.name_box.setFixedWidth(75)
        self.value_box = EditableComboBox()
        self.value_box.setText(str(self.value))
        self.eq_box = LineEdit()
        self.eq_box.setText(str(self.eq_value))
        self.flip = FlipEquality()

        self.layout.addWidget(self.name_box)
        self.layout.addWidget(SubtitleLabel(":"))
        self.layout.addWidget(self.value_box)
        self.layout.addWidget(self.flip)
        self.layout.addWidget(self.eq_box)
        self.layout.addWidget(SubtitleLabel(";"))

        self.add_btns()

class FunctionItem(DefaultItem):
    def __init__(self, name: str, value: float, parent=None):
        super().__init__()

        self.name = name
        self.value = value
        self.parent = parent

        self.name_box = LineEdit()
        self.name_box.setText(self.name)
        self.name_box.setFixedWidth(75)
        self.value_box = EquationButton("", parent)
        self.value_box.equation_text = value
        self.value_box.set_display_text()

        self.layout.addWidget(self.name_box)
        self.layout.addWidget(SubtitleLabel("="))
        self.layout.addWidget(self.value_box)
        self.layout.addWidget(SubtitleLabel(";"))

        self.add_btns()

