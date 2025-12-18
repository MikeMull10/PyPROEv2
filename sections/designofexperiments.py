from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from components.doetable import DOETable
from components.clickabletitle import ClickableTitleLabel
from components.designpopup import DesignPopup
from components.ccd import central_composite, scale_to_bounds
from testing.fnc_objects import Function, Variable

from qfluentwidgets import SubtitleLabel, ComboBox, SpinBox, PushButton, PrimaryPushButton
import numpy as np
import itertools

from enum import Enum
from pprint import pprint as pp

class MethodType(Enum):
    FACTORIAL = 0
    CENTRAL_COMPOSITE_SPHERICAL = 1
    CENTRAL_COMPOSITE_FACE = 2
    TAGUCHI = 3
    LATIN = 4

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
        doe_wrapper.addWidget(self.option_section_widget)
        layout.addLayout(doe_wrapper)

        # --- Method ---
        self.method_type = ComboBox()
        self.method_type.addItems(["Factorial", "Central Composite, Spherical", "Central Composite, Face-Centered", "Taguchi Orthogonal Array", "Latin Hypercube"])
        self.method_type_row = make_row("Method:", self.method_type)
        self.method_type.currentIndexChanged.connect(self.adjust_setting_visibility)
        options_section.addWidget(self.method_type_row)
        options_section.addSpacing(5)

        # --- Number of Variables ---
        self.variable_num = SpinBox()
        self.variable_num.setValue(1)
        self.variable_num.setRange(1, 100)
        self.variable_num_row = make_row("Variable Count:", self.variable_num)
        options_section.addWidget(self.variable_num_row)
        options_section.addSpacing(5)

        # --- Number of Functions ---
        self.functions_num = SpinBox()
        self.functions_num.setValue(1)
        self.functions_num.setRange(1, 50)
        self.functions_num_row = make_row("Function Count:", self.functions_num)
        options_section.addWidget(self.functions_num_row)
        options_section.addSpacing(5)

        # --- Number of Levels ---
        self.level_num = SpinBox()
        self.level_num.setValue(2)
        self.level_num.setRange(2, 20)
        self.level_num_row = make_row("Level Count:", self.level_num)
        options_section.addWidget(self.level_num_row)
        options_section.addSpacing(5)

        # --- Data Points ---
        self.data_points = SpinBox()
        self.data_points.setValue(1)
        self.data_points.setRange(1, 100)
        self.data_points.setDisabled(True)
        self.data_points_row = make_row("Data Points:", self.data_points)
        options_section.addWidget(self.data_points_row)
        options_section.addSpacing(5)

        # --- Center Points ---
        self.center_points = SpinBox()
        self.center_points.setValue(1)
        self.center_points.setRange(1, 1e3)
        self.center_points_row = make_row("Center Points:", self.center_points)
        self.center_points_row.setToolTip("Number of repeated runs at the center of the design space.\n\nCenter points are used to estimate experimental error and detect curvature in the response. Increasing this value improves model reliability but increases the total number of runs.")
        options_section.addWidget(self.center_points_row)
        options_section.addSpacing(5)

        # --- Buttons ---
        self.create_design = PushButton("Get Design")
        self.edit_design = PushButton("Edit Design")
        self.clear_btn = PushButton("Clear")
        self.metamodel_btn = PrimaryPushButton("Metamodel")
        [btn.setCursor(Qt.PointingHandCursor) for btn in [self.create_design, self.edit_design, self.clear_btn, self.metamodel_btn]]

        # --- Add Buttons to Layout ---
        design_layout = QHBoxLayout()
        design_layout.addWidget(self.create_design)
        design_layout.addWidget(self.edit_design)
        second_layout = QHBoxLayout()
        second_layout.addWidget(self.clear_btn)
        second_layout.addWidget(self.metamodel_btn)
        
        options_section.addLayout(design_layout)
        options_section.addLayout(second_layout)

        options_section.addStretch()
        
        self.table = DOETable()
        layout.addWidget(self.table)

        layout.setStretch(0, 3)
        layout.setStretch(1, 7)

        # --- Button Functionality ---
        self.create_design.clicked.connect(self.get_design_popup)
        self.clear_btn.clicked.connect(self.table.clear)

        # --- Set Initial Setting Visibility ---
        self.adjust_setting_visibility()
    
    def adjust_setting_visibility(self):
        match MethodType(self.method_type.currentIndex()):
            case MethodType.FACTORIAL:
                self.level_num_row.show()
                self.data_points_row.hide()
                self.center_points_row.hide()
            case MethodType.CENTRAL_COMPOSITE_SPHERICAL | MethodType.CENTRAL_COMPOSITE_FACE:
                self.level_num_row.hide()
                self.data_points_row.hide()
                self.center_points_row.show()
    
    def toggle_collapse(self):
        self.showing ^= True
        self.setVisible(self.showing)
        if self.toggle_call: self.toggle_call()
    
    def get_design_popup(self):
        popup = DesignPopup(
            self.variable_num.value(),
            self.functions_num.value(),
            self.parent,
        )
        ok, vars, funcs = popup.exec()
        
        if ok:
            self.populate_data(vars, funcs)
    
    def populate_data(self, variables: list[Variable], functions: list[Function]):
        variable_pool = []
        levels = self.level_num.value()

        match MethodType(self.method_type.currentIndex()):
            case MethodType.FACTORIAL:
                for variable in variables:
                    variable_pool.append(np.linspace(variable.min, variable.max, levels))
            case MethodType.CENTRAL_COMPOSITE_SPHERICAL | MethodType.CENTRAL_COMPOSITE_FACE:
                points = central_composite(len(variables), "face" if MethodType(self.method_type.currentIndex()) == MethodType.CENTRAL_COMPOSITE_FACE else "spherical", self.center_points.value())

                for var in scale_to_bounds(points, [v.min for v in variables], [v.max for v in variables]):
                    variable_pool.append(var)

        pp(variable_pool)
        if len(variable_pool) == 0:
            return

        data = []
        for point in itertools.product(*variable_pool):
            data_point = [*point]
            print(data_point)
            for fun in functions:
                data_point.append(fun(point))
            
            data.append(data_point)
        
        headers = [var.symbol.upper() for var in variables] + [fun.name.upper() for fun in functions]
        self.table.populate([[str(d) for d in da] for da in data], headers=headers)
    
    def load_from_file(self, file_path: str):
        lines = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if len(line) > 0 and not line.startswith("#"):
                    lines.append(line)
        
        data = []
        headers = []
        if lines[0].startswith("!"):  # PyPROE X
            version = lines[0].split('v')[ 1 ]
        else:                         # Legacy
            num_points, num_vars, num_levels, num_funcs = map(int, lines.pop(0).split())

            for line in lines:
                data.append(list(map(float, line.split()))[1:])
            
            for i in range(num_vars):
                headers.append(f"X{i + 1}")
            for i in range(num_funcs):
                headers.append(f"F{i + 1}")

            #TODO: get/create variable and function objects
        
        self.table.populate(data=[[str(d) for d in da] for da in data], headers=headers)
