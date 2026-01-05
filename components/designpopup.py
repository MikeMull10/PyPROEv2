from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSize

from components.formsections import VariablesSection, FunctionsSection, VariableItem, FunctionItem
from testing.fnc_objects import Variable, Function

from qfluentwidgets import MessageBoxBase, SmoothScrollArea


class DesignPopup(MessageBoxBase):
    def __init__(self, variable_count: int=0, function_count: int=0, parent=None, variables: list[Variable]=None, functions: list[Function]=None):
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
        self.variable_section = VariablesSection(clickable_title=False)
        if variables:
            [self.variable_section.add_row(v.min, v.max, v.symbol.upper()) for v in variables]
        else:
            [self.variable_section.add_row() for _ in range(variable_count)]

        self.var_scroll = SmoothScrollArea()
        self.var_scroll.setWidgetResizable(True)
        self.var_scroll.setWidget(self.variable_section)
        self.var_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.var_scroll.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.variable_section.setStyleSheet("QWidget{background: transparent}")
        self.variable_section.row_count_changed.connect(self.do_resize)

        layout.addWidget(self.var_scroll)

        # --- Functions ---
        self.function_section = FunctionsSection(parent, clickable_title=False, clamp_value=40)
        if functions:
            [self.function_section.add_row(f.name.upper(), f.text.upper()) for f in functions]
        else:
            [self.function_section.add_row() for _ in range(function_count)]

        self.fnc_scroll = SmoothScrollArea()
        self.fnc_scroll.setWidgetResizable(True)
        self.fnc_scroll.setWidget(self.function_section)
        self.fnc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fnc_scroll.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.function_section.setStyleSheet("QWidget{background: transparent}")
        self.function_section.row_count_changed.connect(self.do_resize)

        layout.addWidget(self.fnc_scroll)

        base_size: QSize = parent.size()
        base_x = 0.3 * base_size.width()
        self.min_height = 0.2 * base_size.height()
        self.max_height = 0.8 * base_size.height()
        self.var_scroll.setFixedWidth(base_x)
        self.fnc_scroll.setFixedWidth(base_x)
        self.do_resize()
        
        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

        self.viewLayout.addWidget(container)

        self.yesButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.setCursor(Qt.PointingHandCursor)

        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.yesButton.click)
        QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self.yesButton.click)
    
    def exec(self):
        ok = super().exec()

        variables: list[Variable] = []
        functions: list[Function] = []
        
        if ok:
            for i in range(self.variable_section.row_container.count()):
                item: VariableItem = self.variable_section.row_container.itemAt(i).widget()
                variables.append(item.get_variable_object())
            
            for i in range(self.function_section.row_container.count()):
                item: FunctionItem = self.function_section.row_container.itemAt(i).widget()
                functions.append(item.get_function_object(variables=variables))

        return ok, variables, functions

    def do_resize(self):
        most = max(self.variable_section.row_container.count(), self.function_section.row_container.count())

        # 60 seems to be the perfect amount to not utilize the scroll widget until the max height has been reached
        #   getting the height of one of the row items does not work because it ends up taking as much space as can, defeating the point entirely
        height = min(max(self.min_height, 60 * (most + 1)), self.max_height)

        self.var_scroll.setFixedHeight(height)
        self.fnc_scroll.setFixedHeight(height)