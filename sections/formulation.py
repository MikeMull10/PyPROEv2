from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
from qfluentwidgets import ScrollArea, SmoothScrollArea, CardWidget, TextEdit, TitleLabel, SubtitleLabel, PushButton, ToolButton, FluentIcon as FI

from components.formsections import VariablesSection, ConstantsSection, ObjectivesSection, FunctionsSection, EqualitiesSection, InequalitiesSection
from components.function_parse import parse_function_offset
from testing.inputfnc2 import InputFile
import os

class FormulationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.setObjectName("Formulation")
        self.setFixedWidth(550)

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

        scroll.setWidget(main_content)

        self.var_section = VariablesSection()
        self.con_section = ConstantsSection()
        self.obj_section = ObjectivesSection()
        self.eqs_section = EqualitiesSection()
        self.iqs_section = InequalitiesSection()
        self.fnc_section = FunctionsSection(parent)
        
        main_layout.addWidget(self.var_section)
        main_layout.addWidget(self.con_section)
        main_layout.addWidget(self.obj_section)
        main_layout.addWidget(self.eqs_section)
        main_layout.addWidget(self.iqs_section)
        main_layout.addWidget(self.fnc_section)

        main_layout.addStretch()

    def load_from_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError

            file = InputFile(file_path)
            
            ### VARIABLES
            for var in file.variables:
                self.var_section.add_row(var.min, var.max, var.symbol.upper())
            
            ### CONSTANTS
            for con in file.constants:
                self.con_section.add_row(con.symbol.upper(), con.value.upper())
            
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
            print("Failed to load file:", e)
