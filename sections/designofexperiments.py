from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from components.basicpopup import BasicPopup
from components.doetable import DOETable
from components.clickabletitle import ClickableTitleLabel
from components.designpopup import DesignPopup
from components.ccd import central_composite, scale_to_bounds
from components.taguchi import get_oa
from components.hypercube import lhs
from components.fnc_objects import Function, Variable

from qfluentwidgets import SubtitleLabel, ComboBox, SpinBox, PushButton, PrimaryPushButton
import numpy as np
import itertools

from enum import Enum

class Flag(Enum):
    TABLE = 0
    VARIABLE = 1
    FUNCTION = 2

class MethodType(Enum):
    FACTORIAL = 0
    CENTRAL_COMPOSITE_SPHERICAL = 1
    CENTRAL_COMPOSITE_FACE = 2
    TAGUCHI = 3
    LATIN_HYPERCUBE = 4

# --- Row helper function ---
def make_row(label_text, widget):
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    label = SubtitleLabel(label_text)
    layout.addWidget(label)
    layout.addWidget(widget)
    row.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    return row

class DesignOfExperimentsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("DOE")
        self.parent = parent
        self.showing = True
        self.toggle_call: callable = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        doe_wrapper = QVBoxLayout()
        self.section_title = ClickableTitleLabel("Design of Experiments")
        self.section_title.clicked.connect(self.toggle_collapse)
        doe_wrapper.addWidget(self.section_title)
        self.option_section_widget = QWidget()
        options_section = QVBoxLayout(self.option_section_widget)
        options_section.setSpacing(10)
        doe_wrapper.addWidget(self.option_section_widget)
        layout.addLayout(doe_wrapper)

        # --- Method ---
        self.method_type = ComboBox()
        self.method_type.addItems(["Factorial", "Central Composite, Spherical", "Central Composite, Face-Centered", "Taguchi Orthogonal Array", "Latin Hypercube"])
        self.method_type_row = make_row("Method:", self.method_type)
        self.method_type.currentIndexChanged.connect(self.adjust_setting_visibility)
        options_section.addWidget(self.method_type_row)

        # --- Number of Variables ---
        self.variable_num = SpinBox()
        self.variable_num.setValue(1)
        self.variable_num.setRange(1, 100)
        self.variable_num_row = make_row("Variable Count:", self.variable_num)
        options_section.addWidget(self.variable_num_row)

        # --- Number of Functions ---
        self.functions_num = SpinBox()
        self.functions_num.setValue(1)
        self.functions_num.setRange(1, 50)
        self.functions_num_row = make_row("Function Count:", self.functions_num)
        options_section.addWidget(self.functions_num_row)

        # --- Number of Levels ---
        self.level_num = SpinBox()
        self.level_num.setValue(2)
        self.level_num.setRange(2, 20)
        self.level_num_row = make_row("Level Count:", self.level_num)
        options_section.addWidget(self.level_num_row)

        # --- Data Points ---
        self.data_points = SpinBox()
        self.data_points.setValue(1)
        self.data_points.setRange(1, 1e6)
        self.data_points_row = make_row("Data Points:", self.data_points)
        options_section.addWidget(self.data_points_row)

        # --- Center Points ---
        self.center_points = SpinBox()
        self.center_points.setValue(1)
        self.center_points.setRange(1, 1e3)
        self.center_points_row = make_row("Center Points:", self.center_points)
        self.center_points_row.setToolTip("Number of repeated runs at the center of the design space.\n\nCenter points are used to estimate experimental error and detect curvature in the response. Increasing this value improves model reliability but increases the total number of runs.")
        options_section.addWidget(self.center_points_row)

        # --- Levels (Taguchi) ---
        self.levels_taguchi = ComboBox()
        self.levels_taguchi.addItems(['2', '3', '4', '5'])
        self.levels_taguchi_row = make_row("Levels:", self.levels_taguchi)
        self.levels_taguchi_row.setToolTip("Number of Levels for the Taguchi Orthognal Array")
        options_section.addWidget(self.levels_taguchi_row)

        # --- Buttons ---
        self.create_design = PrimaryPushButton("Get Design")
        self.edit_design = PushButton("Edit Design")
        self.clear_btn = PushButton("Clear")
        self.add_point_btn = PushButton("Add Point")
        [btn.setCursor(Qt.PointingHandCursor) for btn in [self.create_design, self.edit_design, self.clear_btn, self.add_point_btn]]

        # --- Add Buttons to Layout ---
        design_layout = QHBoxLayout()
        design_layout.addWidget(self.create_design)
        design_layout.addWidget(self.edit_design)
        second_layout = QHBoxLayout()
        second_layout.addWidget(self.clear_btn)
        second_layout.addWidget(self.add_point_btn)
        
        options_section.addLayout(design_layout)
        options_section.addLayout(second_layout)

        options_section.addStretch()
        
        self.table = DOETable(parent=self.parent)
        layout.addWidget(self.table)

        layout.setStretch(0, 3)
        layout.setStretch(1, 7)

        # --- Button Functionality ---
        self.create_design.clicked.connect(self.get_design_popup)
        self.edit_design.clicked.connect(self.edit_design_popup)
        self.clear_btn.clicked.connect(self.table.clear)
        self.add_point_btn.clicked.connect(self.table.add_point)

        # --- Set Initial Setting Visibility ---
        self.adjust_setting_visibility()
    
    def adjust_setting_visibility(self) -> None:
        match MethodType(self.method_type.currentIndex()):
            case MethodType.FACTORIAL:
                self.level_num_row.show()
                self.data_points_row.hide()
                self.center_points_row.hide()
                self.levels_taguchi_row.hide()
            case MethodType.CENTRAL_COMPOSITE_SPHERICAL | MethodType.CENTRAL_COMPOSITE_FACE:
                self.level_num_row.hide()
                self.data_points_row.hide()
                self.center_points_row.show()
                self.levels_taguchi_row.hide()
            case MethodType.TAGUCHI:
                self.level_num_row.hide()
                self.data_points_row.hide()
                self.center_points_row.hide()
                self.levels_taguchi_row.show()
            case MethodType.LATIN_HYPERCUBE:
                self.level_num_row.hide()
                self.data_points_row.show()
                self.center_points_row.hide()
                self.levels_taguchi_row.hide()
    
    def toggle_collapse(self) -> None:
        self.showing ^= True
        self.setVisible(self.showing)
        if self.toggle_call: self.toggle_call()
    
    def get_design_popup(self) -> None:
        popup = DesignPopup(
            self.variable_num.value(),
            self.functions_num.value(),
            self.parent,
        )
        ok, vars, funcs = popup.exec()
        
        if ok:
            self.populate_data(vars, funcs)
            self.variable_num.setValue(len(vars))
            self.functions_num.setValue(len(funcs))
    
    def edit_design_popup(self) -> None:
        popup = DesignPopup(
            self.variable_num.value(),
            self.functions_num.value(),
            self.parent,
            variables=self.table.variables,
            functions=self.table.functions,
        )
        ok, vars, funcs = popup.exec()
        
        if ok:
            self.populate_data(vars, funcs)
    
    def populate_data(self, variables: list[Variable], functions: list[Function]) -> None:
        self.table.clear()
        variable_pool = []
        points = []
        levels = self.level_num.value()

        match MethodType(self.method_type.currentIndex()):
            case MethodType.FACTORIAL:
                for variable in variables:
                    variable_pool.append(np.linspace(variable.min, variable.max, levels))

                for point in itertools.product(*variable_pool):
                    points.append([*point])

            case MethodType.CENTRAL_COMPOSITE_SPHERICAL | MethodType.CENTRAL_COMPOSITE_FACE:
                ccd_points = central_composite(len(variables), "face" if MethodType(self.method_type.currentIndex()) == MethodType.CENTRAL_COMPOSITE_FACE else "spherical", self.center_points.value())

                points = scale_to_bounds(ccd_points, [v.min for v in variables], [v.max for v in variables])
            
            case MethodType.TAGUCHI:
                try:
                    toa_points = get_oa(len(variables), int(self.levels_taguchi.currentText()))
                except ValueError as ve:
                    pop = BasicPopup(parent=self.parent, title="ERROR", message=str(ve))
                    pop.exec()
                    return

                points = scale_to_bounds(toa_points, [v.min for v in variables], [v.max for v in variables])

            case MethodType.LATIN_HYPERCUBE:
                points = lhs(variables, self.data_points.value())

            case _:
                pop = BasicPopup(parent=self.parent, title="ERROR", message=f"MethodType not found for {self.method_type.currentText()}.")
                pop.exec()
                return
                
        if len(points) == 0:
            pop = BasicPopup(parent=self.parent, title="ERROR", message=f"No valid points using method {MethodType(self.method_type.currentIndex())}.")
            pop.exec()
            return

        data = []
        for point in points:
            data_point = [*point]
            for fun in functions:
                data_point.append(fun(point))
            
            data.append(data_point)
        
        headers = [var.symbol.upper() for var in variables] + [fun.name.upper() for fun in functions]
        self.table.variables = variables
        self.table.functions = functions
        self.table.populate([[str(d) for d in da] for da in data], headers=headers)
    
    def load_from_file(self, file_path: str) -> None:
        lines = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if len(line) > 0 and not line.startswith("#"):
                    lines.append(line)
        
        data = []
        headers = []
        if lines[0].startswith("!"):  # PyPROE X
            version = lines.pop(0).split('v')[ 1 ]

            headers = None
            data    = []
            vars : list[Variable] = []
            funcs: list[Function] = []
            if version == "0.0.0":
                flag: Flag = None
                for line in lines:
                    if "*TABLE" in line.upper():
                        flag = Flag.TABLE
                        continue
                    elif "*VARIABLE" in line.upper():
                        flag = Flag.VARIABLE
                        continue
                    elif "*FUNCTION" in line.upper():
                        flag = Flag.FUNCTION
                        continue
                
                    if flag == Flag.TABLE:
                        if not headers:
                            headers = line.split(';')
                            continue
                        data.append(line.split(';')[1:])
                    elif flag == Flag.VARIABLE:
                        sym, vals = line.split(':')
                        _min, _max = map(float, vals.split(',')[0:2])
                        vars.append(Variable(sym, _min, _max))
                    elif flag == Flag.FUNCTION:
                        sym, val = line.replace(';', '').split('=')
                        funcs.append(Function(sym, val, [var.symbol for var in vars]))
            
                self.table.variables = vars
                self.table.functions = funcs
                self.table.populate([[str(d) for d in da] for da in data], headers=headers)

        else:                         # Legacy
            num_points, num_vars, num_levels, num_funcs = map(int, lines.pop(0).split())

            variables: list[Variable] = []
            functions: list[Function] = []

            line: str
            to_use = []
            for line in lines:
                if line.upper().startswith('X'):  # Variable
                    x, minmax = line.split(':')
                    _min, _max = map(float, minmax.strip().split(',')[:2])
                    variables.append(Variable(x.strip(), _min, _max))
                elif line.upper().startswith('F'):  # Function
                    f, fnc_str = line.upper().replace(';', '').split('=')
                    functions.append(Function(f.strip(), fnc_str.strip(), [x.symbol for x in variables]))
                else:
                    to_use.append(line)

            start_index = len(to_use[0].split()) - num_vars - num_funcs
            for line in to_use:
                data.append(list(map(float, line.split()))[start_index:])
            
            for i in range(num_vars):
                headers.append(f"X{i + 1}")
            for i in range(num_funcs):
                headers.append(f"F{i + 1}")

            if len(variables) == 0:
                np_data = np.array(data)
                variables = [Variable(f"X{i + 1}", min(np_data[:, i]), max(np_data[:, i])) for i in range(num_vars)]
            self.table.variables = variables

            if len(functions) > 0: self.table.functions = functions
            self.table.populate(data=[[str(d) for d in da] for da in data], headers=headers)
    
    def save_to_file(self) -> str:
        return f"!PyPROE X v{self.parent.version}\n\n" + self.table.get_save_data()

    def is_empty(self) -> bool:
        return self.table.columnCount() + self.table.rowCount() == 0
