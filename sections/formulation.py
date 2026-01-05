from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from qfluentwidgets import theme, Theme, SmoothScrollArea, SubtitleLabel, FluentIconBase, ToolButton, FluentIcon as FI

from components.formsections import FormSection, VariablesSection, ConstantsSection, ObjectivesSection, FunctionsSection, EqualitiesSection, InequalitiesSection, FunctionItem, ObjectiveItem, InequalityItem, EqualityItem
from components.function_parse import parse_function_offset
from components.divider import Divider
from components.basicpopup import BasicPopup
from testing.inputfnc2 import InputFile
import os, pyperclip

class ResetIcon(FluentIconBase):
    def path(self, _theme=Theme.AUTO):
        return "assets/reset-white.svg" if theme() == Theme.DARK else "assets/reset-black.svg"

class FormulationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.function_names = set()

        self.setObjectName("Formulation")

        main = QVBoxLayout(self)
        main.setContentsMargins(4, 4, 4, 4)

        scroll = SmoothScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background: transparent; border: none}")
        main.addWidget(scroll)

        # --- Testing Creating a Widget ---
        main_content = QWidget()
        main_content.setStyleSheet("QWidget{background: transparent}")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)

        title_row = QWidget()
        layout = QHBoxLayout(title_row)
        layout.setContentsMargins(0, 0, 0, 0)
        title = SubtitleLabel("Formulation")
        font = QFont()
        font.setPointSize(18)
        title.setFont(font)

        copy_btn  = ToolButton(FI.COPY)
        copy_btn.clicked.connect(self.copy_to_clipboard)
        copy_btn.setToolTip("Copy to Clipboard")
        copy_btn.setCursor(Qt.PointingHandCursor)

        paste_btn = ToolButton(FI.PASTE)
        paste_btn.clicked.connect(self.paste_from_clipboard)
        paste_btn.setToolTip("Paste from Clipboard")
        paste_btn.setCursor(Qt.PointingHandCursor)

        clear_btn = ToolButton(ResetIcon())
        clear_btn.clicked.connect(self.clear)
        clear_btn.setToolTip("Clear the Formulation section.")
        clear_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(title)
        layout.addWidget(copy_btn)
        layout.addWidget(paste_btn)
        layout.addWidget(clear_btn)

        scroll.setWidget(main_content)

        self.var_section = VariablesSection()
        self.con_section = ConstantsSection()
        self.obj_section = ObjectivesSection(function_name_update=self.update_function_names)
        self.eqs_section = EqualitiesSection(function_name_update=self.update_function_names)
        self.iqs_section = InequalitiesSection(function_name_update=self.update_function_names)
        self.fnc_section = FunctionsSection(parent, function_name_update=self.update_function_names)
        self.divider = Divider(style=theme())

        main_layout.addWidget(title_row)
        main_layout.addWidget(self.var_section)
        main_layout.addWidget(self.con_section)
        main_layout.addWidget(self.fnc_section)
        main_layout.addWidget(self.divider)
        main_layout.addWidget(self.obj_section)
        main_layout.addWidget(self.eqs_section)
        main_layout.addWidget(self.iqs_section)

        main_layout.addStretch()

    def update_options(self, box: ObjectiveItem | EqualityItem | InequalityItem) -> None:
        box_value = box.value_box.text()
        is_custom = box.value_box.currentIndex() == -1 or box_value in box.value_box.items

        box.value_box.clear()
        box.value_box.addItems(sorted(self.function_names))

        if is_custom or box_value in self.function_names:
            box.value_box.setText(box_value)
        else:
            box.value_box.setText("")
    
    def update_function_names(self) -> None:
        self.function_names.clear()
        for i in range(self.fnc_section.row_container.count()):
            item: FunctionItem = self.fnc_section.row_container.itemAt(i).widget()
            self.function_names.add(item.name)
        
        ### Objectives, Equality Constraints, and Inequality Constraints
        section_type: FormSection
        for section_type in [self.obj_section, self.eqs_section, self.iqs_section]:
            for i in range(section_type.row_container.count()):
                self.update_options(section_type.row_container.itemAt(i).widget())            

    def load_from_file(self, file_path: str, is_file=True) -> None:
        try:
            if is_file and not os.path.exists(file_path):
                raise FileNotFoundError
            
            file = InputFile(file_path, is_file=is_file)
            
            ### VARIABLES
            for var in file.variables:
                self.var_section.add_row(var.min, var.max, var.symbol.upper())
            
            ### CONSTANTS
            for con in file.constants:
                self.con_section.add_row(con.symbol.upper(), con.value)
            
            ### OBJECTIVES
            for obj in file.objectives:
                self.obj_section.add_row(obj.name.upper(), obj.text.upper())

            ### EQUALITY-CONSTRAINTS
            for eq in file.equality_constraints:
                function_name, operator, value = parse_function_offset(eq.text)
                if not function_name or not operator or not value:
                    function_name = eq.text
                    operator = ""
                    value = "0.0"
                else:
                    # flip operator because F1 - 5 = 0 means F1 = 5
                    operator = "-" if operator == "+" else ""
                
                self.eqs_section.add_row(eq.name.upper(), function_name.upper(), str(operator) + str(value).upper())

            ### INEQUALILTY-CONSTRAINTS
            for ineq in file.inequality_constraints:
                function_name, operator, value = parse_function_offset(ineq.text)
                if not function_name or not operator or not value:
                    function_name = ineq.text
                    operator = ""
                    value = "0.0"
                else:
                    # flip operator because F1 - 5 <= 0 means F1 <= 5
                    operator = "-" if operator == "+" else ""
                
                self.iqs_section.add_row(ineq.name.upper(), function_name.upper(), str(operator) + str(value).upper())

            ### FUNCTIONS
            for fun in file.functions:
                self.fnc_section.add_row(fun.name.upper(), fun.text.upper())

        except Exception as e:
            pop = BasicPopup(parent=self.parent, title="ERROR", message=f"Failed to load file: {e}.")
            pop.exec()

    def convert_to_fnc(self) -> str:
        fnc_str  = f"#{'-' * 50}\n"
        fnc_str += "# Input File Start\n"
        fnc_str += f"#{'-' * 50}\n\n"

        for section in [self.var_section, self.con_section, self.obj_section, self.eqs_section, self.iqs_section, self.fnc_section]:
            fnc_str += section.get_fnc() + "\n"

        fnc_str += f"#{'-' * 50}\n"
        fnc_str += "# Input File End\n"
        fnc_str += f"#{'-' * 50}"

        return fnc_str

    def is_empty(self) -> bool:
        return sum(section.row_container.count() for section in [self.var_section, self.con_section, self.obj_section, self.eqs_section, self.iqs_section, self.fnc_section]) == 0

    def clear(self) -> None:
        for section in [self.var_section, self.con_section, self.obj_section, self.eqs_section, self.iqs_section, self.fnc_section]:
            section.clear()

    def copy_to_clipboard(self):
        pyperclip.copy(self.convert_to_fnc())
    
    def paste_from_clipboard(self):
        self.load_from_file(pyperclip.paste(), is_file=False)
