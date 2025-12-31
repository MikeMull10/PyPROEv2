from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from components.formsections import VariablesSection, VariableItem, FunctionsSection, FunctionItem
from testing.fnc_objects import Variable, Function

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
    
    def populate_graph(self):
        ...
    
    def get_surface_plot(self, variables: list[Variable], function: Function):
        if len(self.variables) != 2:
            return None

        v = self.variables
        x1 = np.arange(
            v["X1"][0], v["X1"][1] + v["X1"][0] / 10, v["X1"][0] / 10
        )
        x2 = np.arange(
            v["X2"][0], v["X2"][1] + v["X2"][0] / 10, v["X2"][0] / 10
        )

        x = np.meshgrid(x1, x2)

        func_str = clean(self.functions[function_to_graph], 2)

        func = eval(func_str)

        # Create a 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Plot the surface
        ax.plot_surface(*x, func, cmap="viridis")

        # Set labels
        ax.set_xlabel("X1")
        ax.set_ylabel("X2")
        ax.set_zlabel(function_to_graph)

        # return the plot
        return fig