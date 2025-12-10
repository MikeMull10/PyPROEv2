from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from components.doetable import DOETable
from components.clickabletitle import ClickableTitleLabel
from qfluentwidgets import SubtitleLabel, ComboBox, SpinBox

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
    def __init__(self):
        super().__init__()
        self.setObjectName("DOE")
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
        options_section.addSpacing(10)

        # --- Number of Variables ---
        self.variable_num = SpinBox()
        self.variable_num.setValue(1)
        self.variable_num.setRange(1, 100)
        self.variable_num_row = make_row("Variable Count:", self.variable_num)
        options_section.addWidget(self.variable_num_row)
        options_section.addSpacing(10)

        # --- Number of Levels ---
        self.level_num = SpinBox()
        self.level_num.setValue(2)
        self.level_num.setRange(2, 20)
        self.level_num_row = make_row("Level Count:", self.level_num)
        options_section.addWidget(self.level_num_row)
        options_section.addSpacing(10)

        # --- Data Points ---
        self.data_points = SpinBox()
        self.data_points.setValue(1)
        self.data_points.setRange(1, 100)
        self.data_points_row = make_row("Data Points:", self.data_points)
        options_section.addWidget(self.data_points_row)
        options_section.addSpacing(10)

        # --- Number of Functions ---
        self.functions_num = SpinBox()
        self.functions_num.setValue(1)
        self.functions_num.setRange(1, 50)
        self.functions_num_row = make_row("Function Count:", self.functions_num)
        options_section.addWidget(self.functions_num_row)
        options_section.addSpacing(10)

        options_section.addStretch()
        
        self.table = DOETable()
        layout.addWidget(self.table)

        layout.setStretch(0, 3)
        layout.setStretch(1, 7)
    
    def toggle_collapse(self):
        self.showing ^= True
        
        if self.showing:
            self.option_section_widget.show()
            self.table.show()
        else:
            self.option_section_widget.hide()
            self.table.hide()
