from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDialog, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from components.basicpopup import BasicPopup
from components.graph import MplWidget
from components.fnc_objects import Variable, Function
from components.inputfnc2 import InputFile
from sections.formulation import FormulationPage

from matplotlib.axes import Axes
from qfluentwidgets import MessageBoxBase, ComboBox, SubtitleLabel, FluentIconBase, PrimaryDropDownPushButton, PushButton, RoundMenu, Theme, theme

from enum import Enum
import numpy as np
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

        self.formpage = FormulationPage(parent=self)
        
        self.main = QHBoxLayout(self)
        self.main.setContentsMargins(4, 4, 4, 4)

        self.form_layout = QVBoxLayout()
        self.form_layout.addWidget(self.formpage)

        self.plot_btn = PrimaryDropDownPushButton("Plot")

        menu = RoundMenu()
        contours_action = QAction("Contours")
        surface_action = QAction("Surface")

        contours_action.triggered.connect(lambda: self.populate_graph(plot_type=PlotType.CONTOURS))
        surface_action.triggered.connect(lambda: self.populate_graph(plot_type=PlotType.SURFACE))
        menu.view.setCursor(Qt.PointingHandCursor)

        menu.addActions([contours_action, surface_action])

        self.plot_btn.setMenu(menu)
        self.plot_btn.setCursor(Qt.PointingHandCursor)

        self.popout_btn = PushButton("View Graph")
        self.popout_btn.clicked.connect(self.popout)
        self.popout_btn.setCursor(Qt.PointingHandCursor)

        btn_bar = QHBoxLayout()
        btn_bar.addWidget(self.plot_btn)
        btn_bar.addWidget(self.popout_btn)
        self.form_layout.addLayout(btn_bar)
        self.main.addLayout(self.form_layout)

        self.graph = MplWidget()
        self.main.addWidget(self.graph)

        self.main.setStretch(0, 4)
        self.main.setStretch(1, 5)

        self.XYZ = {'X': None, 'Y': None, 'Z': None}
        self.contour_Zs = []
        self.titles = {'X': None, 'Y': None, 'Z': None}
    
    def populate_graph(self, plot_type: PlotType):
        file = InputFile(self.formpage.convert_to_fnc(), is_file=False, check_nums=False, no_objectives_throws_error=(plot_type == PlotType.CONTOURS))
        if file.error:
            pop = BasicPopup(self, title="ERROR", message=f"Error with Formulation: {file.error_message}")
            pop.exec()
            return
        
        if plot_type == PlotType.SURFACE:
            
            if len(file.functions) == 0:
                pop = BasicPopup(parent=self.parent, title="ERROR", message=f"ERROR: No function. You must have at least one function to create a plot.")
                pop.exec()
                return
            
            elif len(file.functions) > 1:
                pop = ChoosePopup(parent=self, title="Select a Function to Graph", options=[fnc.name.upper() for fnc in file.functions])
                ok, index = pop.exec()
                if not ok:
                    return
                
                func = file.functions[index]
            
            else: # only 1 function
                func = file.functions[0]
            
            try:
                self.get_surface_plot(self.graph.axes, variables=file.variables, function=func)
            except Exception as e:
                pop = BasicPopup(parent=self.parent, title="ERROR", message=f"{e}")
                pop.exec()
        
        elif plot_type == PlotType.CONTOURS:

            if len(file.objectives) == 0:
                pop = BasicPopup(parent=self.parent, title="ERROR", message=f"ERROR: No objective function. You must have at least one objective function to create a plot.")
                pop.exec()
                return
            
            elif len(file.objectives) > 1:
                pop = ChoosePopup(parent=self, title="Select an Objective Function to Graph", options=[fnc.name.upper() for fnc in file.objectives])
                ok, index = pop.exec()
                if not ok:
                    return
                    
                obj = file.objectives[index]
            
            else: # only 1 objective function
                obj = file.objectives[0]
            
            try:
                self.get_contour_plot(self.graph.axes, variables=file.variables, objective=obj, equality_constraints=file.equality_constraints, inequality_constraints=file.inequality_constraints)
            except Exception as e:
                pop = BasicPopup(parent=self.parent, title="ERROR", message=f"{e}")
                pop.exec()
    
    def get_contour_plot(self, ax: Axes, variables: list[Variable], objective: Function, equality_constraints: list[Function], inequality_constraints: list[Function]) -> None:
        if len(variables) != 2:
            raise ValueError(f"Incorrect number of variables. Have {len(variables)}, need 2.")

        fig = ax.figure
        fig.clear()
        ax = fig.add_subplot(111)

        x1 = np.linspace(variables[0].min, variables[0].max, 101)
        x2 = np.linspace(variables[1].min, variables[1].max, 101)

        X, Y = np.meshgrid(x1, x2)
        Z = np.empty_like(X, dtype=float)

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = objective([X[i, j], Y[i, j]])

        self.XYZ = {'X': X, 'Y': Y, 'Z': Z}
        self.plot_type = PlotType.CONTOURS

        # Labels and title
        self.titles = {'X': latexify(variables[0].symbol), 'Y': latexify(variables[1].symbol), 'Z': latexify(objective.name.upper())}
        ax.set_xlabel(f"${self.titles['X']}$")
        ax.set_ylabel(f"${self.titles['Y']}$")
        ax.set_title(f"Contour Plot")
        
        # Contour plots
        f_contour = ax.contour(X, Y, Z, 30)
        ax.clabel(f_contour)

        # Constraints contours
        self.contour_Zs.clear()
        for fnc in equality_constraints + inequality_constraints:
            new_Z = np.empty_like(X, dtype=float)

            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    new_Z[i, j] = fnc([X[i, j], Y[i, j]])

            ax.contour(X, Y, new_Z, [0], colors='k')
            self.contour_Zs.append(new_Z)

        self.graph.draw_idle()
    
    def get_surface_plot(self, ax: Axes, variables: list[Variable], function: Function) -> None:
        if len(variables) != 2:
            raise ValueError(f"Incorrect number of variables. Have {len(variables)}, need 2.")
        
        fig = ax.figure
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
        self.plot_type = PlotType.SURFACE

        ax.clear()
        ax.plot_surface(X, Y, Z, cmap="viridis")

        self.titles = {'X': latexify(variables[0].symbol), 'Y': latexify(variables[1].symbol), 'Z': latexify(function.name.upper())}
        ax.set_xlabel(f"${self.titles['X']}$")
        ax.set_ylabel(f"${self.titles['Y']}$")
        ax.set_zlabel(f"${self.titles['Z']}$")
        ax.set_title(f"Surface Plot")

        self.graph.draw_idle()

    def popout(self):
        if any(v is None for v in self.XYZ.values()):
            return

        dialog = QDialog()
        dialog.setWindowTitle("Optimization Results Graph")
        dialog.resize(1200, 800)
        layout = QVBoxLayout()

        new_widget = MplWidget(self)
        fig = new_widget.axes.figure
        fig.clear()
        new_widget.axes = fig.add_subplot(111, projection="3d") if self.plot_type == PlotType.SURFACE else fig.add_subplot(111)

        new_widget.axes.clear()
        if self.plot_type == PlotType.SURFACE:
            new_widget.axes.plot_surface(self.XYZ['X'], self.XYZ['Y'], self.XYZ['Z'], cmap="viridis")

        else:
            f_contour = new_widget.axes.contour(self.XYZ['X'], self.XYZ['Y'], self.XYZ['Z'], 30)
            new_widget.axes.clabel(f_contour)

            for Z in self.contour_Zs:
                new_widget.axes.contour(self.XYZ['X'], self.XYZ['Y'], Z, [0], colors='k')

        new_widget.axes.set_xlabel(f"${self.titles['X']}$")
        new_widget.axes.set_ylabel(f"${self.titles['Y']}$")
        if self.plot_type == PlotType.SURFACE: new_widget.axes.set_zlabel(f"${self.titles['Z']}$")
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

