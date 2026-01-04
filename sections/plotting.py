from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDialog, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from components.formsections import VariablesSection, VariableItem, FunctionsSection, FunctionItem
from components.basicpopup import BasicPopup
from components.graph import MplWidget
from testing.fnc_objects import Variable, Function
from testing.inputfnc2 import InputFile
from sections.formulation import ResetIcon

from matplotlib.axes import Axes
from qfluentwidgets import MessageBoxBase, ComboBox, SubtitleLabel, SmoothScrollArea, FluentIconBase, PrimaryDropDownPushButton, ToolButton, PushButton, RoundMenu, Theme, theme

from enum import Enum
import numpy as np
import os
import re

def latexify(var_name: str) -> str:
    match = re.match(r"([A-Za-z]+)(\d+)", var_name)
    if match:
        letters, numbers = match.groups()
        return f"{letters}_{numbers}"
    else:
        return var_name


class PlotType(Enum):
    CONTOURS = 0
    SURFACE = 1

class GraphIcon(FluentIconBase):
    def path(self, _theme=Theme.AUTO):
        return "assets/chart-white.svg" if theme() == Theme.DARK else "assets/chart-black.svg"
    
class ChoosePopup(MessageBoxBase):
    def __init__(self, parent, title: str | None=None, options: list[str] | None=None, hide_cancel: bool=False):
        """
        parent needs to be the main window
        """
        super().__init__(parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(15)

        if title: layout.addWidget(SubtitleLabel(title))
        
        self.options_box = ComboBox()
        if options: 
            layout.addWidget(self.options_box)
            self.options_box.addItems(options)

        self.viewLayout.addWidget(container)
        self.yesButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.setCursor(Qt.PointingHandCursor)
        if hide_cancel: self.cancelButton.hide()
    
    def exec(self) -> tuple[bool, int]:
        return super().exec(), self.options_box.currentIndex()

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
        self.reset_layout = QHBoxLayout()
        self.reset_layout.addStretch()
        self.reset_btn = ToolButton(ResetIcon())
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.clear)
        self.reset_layout.addWidget(self.reset_btn)
        self.formulation_layout.addLayout(self.reset_layout)
        self.formulation_layout.addWidget(self.var_section)
        self.formulation_layout.addWidget(self.fnc_section)
        self.formulation_layout.addStretch()

        self.plot_btn = PrimaryDropDownPushButton("Plot")

        menu = RoundMenu()
        contours_action = QAction("Contours")
        surface_action = QAction("Surface")

        contours_action.triggered.connect(lambda: self.populate_graph(PlotType.CONTOURS))
        surface_action.triggered.connect(lambda: self.populate_graph(PlotType.SURFACE))

        menu.addActions([contours_action, surface_action])

        self.plot_btn.setMenu(menu)
        self.plot_btn.setCursor(Qt.PointingHandCursor)

        self.popout_btn = PushButton("View Graph")
        self.popout_btn.clicked.connect(self.popout)
        self.popout_btn.setCursor(Qt.PointingHandCursor)

        btn_bar = QHBoxLayout()
        btn_bar.addWidget(self.plot_btn)
        btn_bar.addWidget(self.popout_btn)
        self.formulation_layout.addLayout(btn_bar)

        scroll.setLayout(self.formulation_layout)

        self.graph = MplWidget()
        self.main.addWidget(self.graph)

        self.main.setStretch(0, 2)
        self.main.setStretch(1, 5)

        self.XYZ = {'X': None, 'Y': None, 'Z': None}
        self.titles = {'X': None, 'Y': None, 'Z': None}
    
    def populate_graph(self, plot_type: PlotType):
        vars: list[Variable] = []
        fncs: list[Function] = []

        for i in range(self.var_section.row_container.count()):
            item: VariableItem = self.var_section.row_container.itemAt(i).widget()
            vars.append(item.get_variable_object())

        for i in range(self.fnc_section.row_container.count()):
            item: FunctionItem = self.fnc_section.row_container.itemAt(i).widget()
            fncs.append(item.get_function_object(vars))

        if len(fncs) == 0:
            pop = BasicPopup(parent=self.parent, title="ERROR", message=f"ERROR: No function. You must have at least one function to create a plot.")
            pop.exec()
            return
        
        try:
            self.get_surface_plot(self.graph.axes, variables=vars, function=fncs[0])
        except Exception as e:
            pop = BasicPopup(parent=self.parent, title="ERROR", message=f"{e}")
            pop.exec()
    
    def get_surface_plot(self, ax: Axes, variables: list[Variable], function: Function) -> None:
        if len(variables) != 2:
            raise ValueError(f"Incorrect number of variables. Have {len(variables)}, need 2.")
        
        fig = ax.figure

        if not hasattr(ax, "plot_surface"):
            fig.clear()
            ax = fig.add_subplot(111, projection="3d")

        x1 = np.linspace(variables[0].min, variables[0].max, 11)
        x2 = np.linspace(variables[1].min, variables[1].max, 11)

        X, Y = np.meshgrid(x1, x2)
        Z = np.empty_like(X, dtype=float)

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = function([X[i, j], Y[i, j]])

        self.XYZ = {'X': X, 'Y': Y, 'Z': Z}

        ax.clear()
        ax.plot_surface(X, Y, Z, cmap="viridis")

        self.titles = {'X': latexify(variables[0].symbol), 'Y': latexify(variables[1].symbol), 'Z': latexify(function.name.upper())}
        ax.set_xlabel(f"${self.titles['X']}$")
        ax.set_ylabel(f"${self.titles['Y']}$")
        ax.set_zlabel(f"${self.titles['Z']}$")

        self.graph.draw_idle()

    def load_from_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError

            file = InputFile(file_path)
            
            ### VARIABLES
            for var in file.variables:
                self.var_section.add_row(var.min, var.max, var.symbol.upper())

            ### FUNCTIONS
            for fun in file.functions:
                self.fnc_section.add_row(fun.name.upper(), fun.text.upper())
            
            for i in range(self.fnc_section.row_container.count()):
                item: FunctionItem = self.fnc_section.row_container.itemAt(i).widget()
                item.value_box.clamp_factor = 30
                item.value_box.set_display_text()

        except Exception as e:
            pop = BasicPopup(parent=self.parent, title="ERROR", message=f"Failed to load file: {e}.")
            pop.exec()
    
    def popout(self):
        if None in self.XYZ.values():
            return

        dialog = QDialog()
        dialog.setWindowTitle("Optimization Results Graph")
        dialog.resize(1200, 800)
        layout = QVBoxLayout()

        new_widget = MplWidget(self)
        fig = new_widget.axes.figure
        fig.clear()
        new_widget.axes = fig.add_subplot(111, projection="3d")

        new_widget.axes.clear()
        new_widget.axes.plot_surface(self.XYZ['X'], self.XYZ['Y'], self.XYZ['Z'], cmap="viridis")

        new_widget.axes.set_xlabel(f"${self.titles['X']}$")
        new_widget.axes.set_ylabel(f"${self.titles['Y']}$")
        new_widget.axes.set_zlabel(f"${self.titles['Z']}$")
        new_widget.axes.grid(True)

        toolbar = NavigationToolbar(new_widget, dialog)
        toolbar.setStyleSheet(
            """
            QToolButton {
                background-color: transparent;
                color: white;
            }
        """
        )
        for child in toolbar.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("color: white;")

        layout.addWidget(toolbar)
        layout.addWidget(new_widget)
        dialog.setLayout(layout)

        dialog.exec()

    def clear(self):
        self.var_section.clear()
        self.fnc_section.clear()
