from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from components.doetable import DOETable
from components.clickabletitle import ClickableTitleLabel
from components.designpopup import DesignPopup
from testing.fnc_objects import Function, Variable

from qfluentwidgets import SubtitleLabel, ComboBox, SpinBox, PushButton, PrimaryPushButton
import numpy as np
import itertools

from pprint import pp

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
        options_section.addWidget(self.method_type_row)
        options_section.addSpacing(5)

        # --- Number of Variables ---
        self.variable_num = SpinBox()
        self.variable_num.setValue(1)
        self.variable_num.setRange(1, 100)
        self.variable_num_row = make_row("Variable Count:", self.variable_num)
        options_section.addWidget(self.variable_num_row)
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

        # --- Number of Functions ---
        self.functions_num = SpinBox()
        self.functions_num.setValue(1)
        self.functions_num.setRange(1, 50)
        self.functions_num_row = make_row("Function Count:", self.functions_num)
        options_section.addWidget(self.functions_num_row)
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
    
    def toggle_collapse(self):
        self.showing ^= True
        
        if self.showing:
            self.option_section_widget.show()
            self.table.show()
        else:
            self.option_section_widget.hide()
            self.table.hide()
    
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

        for variable in variables:
            variable_pool.append(np.linspace(variable.min, variable.max, levels))

        data = []
        for point in itertools.product(*variable_pool):
            data_point = [*point]
            for fun in functions:
                data_point.append(fun(point))
            
            data.append(data_point)
        
        headers = [var.symbol.upper() for var in variables] + [fun.name.upper() for fun in functions]
        self.table.populate([[str(d) for d in da] for da in data], headers=headers)
