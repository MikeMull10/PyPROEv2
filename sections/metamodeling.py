from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from components.clickabletitle import ClickableTitleLabel
from components.polyreg import PolyTypes, poly_lookup
from components.doetable import DOETable
from components.formsections import FunctionsSection, FunctionItem, VariablesSection
from components.rbf import RBFType, generate_rbf
from sections.designofexperiments import make_row
from sections.formulation import ResetIcon
from testing.fnc_objects import Variable

from qfluentwidgets import ComboBox, PrimaryPushButton, ToolButton, PrimaryToolButton, SmoothScrollArea, FluentIcon as FI

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

        scroll = SmoothScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(1e5)
        scroll.setStyleSheet("QScrollArea{background: transparent; border: none}")
        results_layout.addWidget(scroll)

        self.functions_section = FunctionsSection(parent=parent, clickable_title=True)
        self.functions_section.add_btn.deleteLater()
        self.functions_section.reset_btn = ToolButton(ResetIcon())
        self.functions_section.next_btn  = PrimaryToolButton(FI.RIGHT_ARROW)
        self.functions_section.reset_btn.setCursor(Qt.PointingHandCursor)
        self.functions_section.next_btn .setCursor(Qt.PointingHandCursor)
        self.functions_section.top_bar.addWidget(self.functions_section.reset_btn)
        self.functions_section.top_bar.addWidget(self.functions_section.next_btn)
        self.functions_section.reset_btn.clicked.connect(self.functions_section.clear)
        self.functions_section.next_btn.clicked.connect(self.send_to_optimization)

        self.functions_section.setStyleSheet("QWidget{background: transparent}")
        scroll.setWidget(self.functions_section)
        scroll.setAlignment(Qt.AlignTop)
        self.functions_section.main_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.results)

        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        self.update_function_options()
    
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
        
        # --- Remove Buttons & Update Clamp Factor ---
        for i in range(self.functions_section.row_container.count()):
            item: FunctionItem = self.functions_section.row_container.itemAt(i).widget()
            item.value_box.clamp_factor = 65
            item.value_box.set_display_text()
            if hasattr(item, "up_arrow") and item.up_arrow is not None:
                item.up_arrow.setParent(None)
                item.up_arrow.deleteLater()
                item.up_arrow = None

            if hasattr(item, "down_arrow") and item.down_arrow is not None:
                item.down_arrow.setParent(None)
                item.down_arrow.deleteLater()
                item.down_arrow = None

            if hasattr(item, "remove_btn") and item.remove_btn is not None:
                item.remove_btn.setParent(None)
                item.remove_btn.deleteLater()
                item.remove_btn = None
    
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
    
    def send_to_optimization(self):
        vars = self.parent.doe.table.variables

        var_section: VariablesSection = self.parent.frm.var_section
        v: Variable
        for v in vars:
            var_section.add_row(v.min, v.max, v.symbol)

        fnc_section: FunctionsSection = self.parent.frm.fnc_section
        for i in range(self.functions_section.row_container.count()):
            item: FunctionItem = self.functions_section.row_container.itemAt(i).widget()
            fnc_section.add_row(item.name_box.text(), item.value_box.equation_text)
