from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from components.formsections import VariablesSection, VariableItem, FunctionsSection, FunctionItem

from qfluentwidgets import SmoothScrollArea, FluentIconBase, Theme, theme


class GraphIcon(FluentIconBase):
    def path(self, _theme=Theme.AUTO):
        return "assets/chart-white.svg" if theme() == Theme.DARK else "assets/chart-black.svg"

class PlottingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("Plotting")
        self.parent = parent

        self.var_section = VariablesSection()
        self.fnc_section = FunctionsSection(parent=self)
        
        self.main = QHBoxLayout(self)
        self.main.setContentsMargins(4, 4, 4, 4)

        scroll = SmoothScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.main.addWidget(scroll)
        
        self.formulation_layout = QVBoxLayout()
        self.formulation_layout.addWidget(self.var_section)
        self.formulation_layout.addWidget(self.fnc_section)
        self.formulation_layout.addStretch()

        scroll.setLayout(self.formulation_layout)