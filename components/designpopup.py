from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize

from qfluentwidgets import MessageBoxBase, PushButton, PlainTextEdit
from components.formsections import VariablesSection, FunctionsSection, VariableItem, FunctionItem
from testing.fnc_objects import Variable, Function


class DesignPopup(MessageBoxBase):
    def __init__(self, variable_count: int=0, function_count: int=0, parent=None):
        """
        parent needs to be the main window
        """
        super().__init__(parent)

        # --- Main content container ---
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(15)

        # --- Variables ---
        self.variable_section = VariablesSection()
        [self.variable_section.add_row() for i in range(variable_count)]
        layout.addWidget(self.variable_section)

        # --- Functions ---
        self.function_section = FunctionsSection(parent)
        [self.function_section.add_row() for i in range(function_count)]
        layout.addWidget(self.function_section)

        # self.text_area = PlainTextEdit(self)
        # self.text_area.setPlaceholderText("*equation here*")

        # Get base size of the Application window and scale down a bit
        base_size: QSize = parent.size()
        base_x = 0.3 * base_size.width()
        base_y = 0.2 * base_size.height()
        self.variable_section.setFixedWidth(base_x)
        self.function_section.setFixedWidth(base_x)
        self.variable_section.setMinimumHeight(base_y)
        self.function_section.setMinimumHeight(base_y)

        # layout.addWidget(self.text_area)

        # Add main body to dialog
        self.viewLayout.addWidget(container)

    def get_equation_text(self):
        return
        return self.text_area.toPlainText()
    
    def exec(self):
        ok = super().exec()

        variables: list[Variable] = []
        functions: list[Function] = []
        
        if ok:
            for i in range(self.variable_section.row_container.count()):
                item: VariableItem = self.variable_section.row_container.itemAt(i).widget()
                variables.append(Variable(item.var_box.text(), float(item.min_box.text()), float(item.max_box.text())))
            
            for i in range(self.function_section.row_container.count()):
                item: FunctionItem = self.function_section.row_container.itemAt(i).widget()
                functions.append(Function(item.name_box.text(), item.value_box.equation_text, [var.symbol for var in variables]))

        return ok, variables, functions