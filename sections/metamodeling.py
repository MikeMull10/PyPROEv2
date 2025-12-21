from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from components.clickabletitle import ClickableTitleLabel
from sections.designofexperiments import make_row

from qfluentwidgets import ComboBox, TextEdit, PrimaryPushButton

class MetamodelPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("Metamodel")
        self.parent = None
        self.showing = True
        self.toggle_call: callable = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        mmd_wrapper = QVBoxLayout()
        self.section_title = ClickableTitleLabel("Metamodeling")
        self.section_title.clicked.connect(self.toggle_collapse)
        mmd_wrapper.addWidget(self.section_title)

        self.option_section_widget = QWidget()
        options_section = QVBoxLayout(self.option_section_widget)
        mmd_wrapper.addWidget(self.option_section_widget)
        layout.addLayout(mmd_wrapper)

        # --- Method ---
        self.method_type = ComboBox()
        self.method_type.addItems(["Polynomial Regression", "Radial Basis Functions"])
        self.method_type.currentIndexChanged.connect(self.update_function_options)
        self.method_type_row = make_row("Method:", self.method_type)
        options_section.addWidget(self.method_type_row)
        options_section.addSpacing(5)

        # --- Functions ---
        self.function_type = ComboBox()
        self.function_type_row = make_row("Function:", self.function_type)
        self.update_function_options()
        options_section.addWidget(self.function_type_row)
        options_section.addSpacing(5)

        # --- Polynomial Order ---
        self.poly_order = ComboBox()
        self.poly_order.addItems(["0", "1"])
        self.poly_order_row = make_row("Polynomial Order:", self.poly_order)
        options_section.addWidget(self.poly_order_row)
        options_section.addSpacing(5)

        self.calculate_btn = PrimaryPushButton("Calculate")
        self.calculate_btn.setCursor(Qt.PointingHandCursor)
        options_section.addWidget(self.calculate_btn)

        options_section.addStretch()

        self.results = TextEdit()
        layout.addWidget(self.results)

        layout.setStretch(0, 2)
        layout.setStretch(1, 3)
    
    def update_function_options(self):
        self.function_type.clear()
        
        if self.method_type.currentIndex() == 0:
            self.function_type.addItems(["Linear Polynomial", "Quadratic Polynomial with No Interation", "Quadratic Polynomial with Interation"])
        else:
            self.function_type.addItems(["Linear", "Cubic", "Thin Plate Spline", "Gaussian", "Multiquadratic", "Inversely Multiquadratic",
                                         "Compactly Supported (2,0)", "Compactly Supported (2,1)", "Compactly Supported (2,2)",
                                         "Compactly Supported (3,0)", "Compactly Supported (3,1)", "Compactly Supported (3,2)", "Compactly Supported (3,3)"])

    def toggle_collapse(self):
        self.showing ^= True
        self.setVisible(self.showing)
        if self.toggle_call: self.toggle_call()
