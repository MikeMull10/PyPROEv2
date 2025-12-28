from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

from components.clickabletitle import ClickableTitleLabel
from components.polyreg import PolyTypes, poly_lookup
from components.doetable import DOETable
from components.formsections import FunctionsSection, FunctionItem
from components.rbf import RBFType, generate_rbf
from sections.designofexperiments import make_row

from qfluentwidgets import ComboBox, PrimaryPushButton

from pprint import pprint as pp

class MetamodelPage(QWidget):
    def __init__(self, doe_table: DOETable=None, parent=None):
        super().__init__()
        self.setObjectName("Metamodel")
        self.parent = parent
        self.doe_table = doe_table
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
        self.calculate_btn.clicked.connect(self.calculate)
        options_section.addWidget(self.calculate_btn)

        options_section.addStretch()

        self.results = QWidget()
        results_layout = QVBoxLayout(self.results)
        self.functions_section = FunctionsSection(parent=parent, clickable_title=True)
        self.functions_section.add_btn.deleteLater()

        results_layout.addWidget(self.functions_section)
        results_layout.addStretch()
        layout.addWidget(self.results)

        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        self.update_function_options()
        self.resize_function_btns()
    
    def update_function_options(self):
        self.function_type.clear()
        
        if self.method_type.currentIndex() == 0:
            self.function_type.addItems(["Linear Polynomial", "Quadratic Polynomial with No Interaction", "Quadratic Polynomial with Interaction"])
            self.poly_order_row.hide()
        else:
            self.function_type.addItems(["Linear", "Cubic", "Thin Plate Spline", "Gaussian", "Multiquadratic", "Inversely Multiquadratic",
                                         "Compactly Supported (2,0)", "Compactly Supported (2,1)", "Compactly Supported (2,2)",
                                         "Compactly Supported (3,0)", "Compactly Supported (3,1)", "Compactly Supported (3,2)", "Compactly Supported (3,3)"])
            self.poly_order_row.show()

    def toggle_collapse(self):
        self.showing ^= True
        self.setVisible(self.showing)
        if self.toggle_call: self.toggle_call()
    
    def calculate(self):
        method_type = self.method_type.currentIndex()

        if method_type == 0:  # Polynomial Regression
            self.do_poly_reg()
        
        else:                 # Radial Basis Function
            self.do_rbf()
    
    def do_poly_reg(self):
        poly_type = PolyTypes(self.function_type.currentIndex())

        func = poly_lookup.get(poly_type, None)
        if not func:
            return

        independent_vars = self.doe_table.get_independent()
        dependent_vars = self.doe_table.get_dependent()
        var_names: list[str] = [var.symbol for var in self.doe_table.variables]

        if len(independent_vars) == 0 or len(dependent_vars) == 0:
            return
        
        # --- Clear Current Items ---
        self.functions_section.clear()

        # --- Populate Functions ---
        results = func(independent_vars, dependent_vars, var_names)
        for i, res in enumerate(results, start=1):
            self.functions_section.add_row(name=f"F{i}", value=res)
        
        # --- Remove Buttons ---
        for i in range(self.functions_section.row_container.count()):
            item: FunctionItem = self.functions_section.row_container.itemAt(i).widget()
            if hasattr(item, "up_arrow"): item.up_arrow.deleteLater()
            if hasattr(item, "down_arrow"): item.down_arrow.deleteLater()
            if hasattr(item, "remove_btn"): item.remove_btn.deleteLater()
        
        self.resize_function_btns()

    def do_rbf(self):
        rbf = RBFType(self.function_type.currentIndex())

        independent_vars = self.doe_table.get_independent()
        dependent_vars = self.doe_table.get_dependent()
        var_names: list[str] = [var.symbol for var in self.doe_table.variables]

        if len(independent_vars) == 0 or len(dependent_vars) == 0:
            return
        
        # --- Clear Current Items ---
        self.functions_section.clear()

        # --- Populate Functions ---
        for i in range(dependent_vars.shape[1]):
            self.functions_section.add_row(name=f"F{i + 1}", value=generate_rbf(independent_vars, dependent_vars[:, i], rbf, epsilon=1.0, variable_names=var_names))
        
        # --- Remove Buttons ---
        for i in range(self.functions_section.row_container.count()):
            item: FunctionItem = self.functions_section.row_container.itemAt(i).widget()
            if hasattr(item, "up_arrow"): item.up_arrow.deleteLater()
            if hasattr(item, "down_arrow"): item.down_arrow.deleteLater()
            if hasattr(item, "remove_btn"): item.remove_btn.deleteLater()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_function_btns()
    
    def resize_function_btns(self):
        size: QSize = self.functions_section.size()
        width = size.width()
        print(width, width // 8)

        for i in range(self.functions_section.row_container.count()):
            item: FunctionItem = self.functions_section.row_container.itemAt(i).widget()
            item.value_box.clamp_factor = width // 8
            item.value_box.set_display_text()
