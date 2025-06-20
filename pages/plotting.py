from decimal import getcontext
from pprint import pprint as pp

import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel

from algorithms.evolution import handle_evolve
from algorithms.multiobj import MultiOBJ
from algorithms.slsqp import SLSQP
from components.mplwidget import MplWidget, MplWidget2
from handlers.inputfnc import InputFile
from pages.mainwindow import Ui_MainWindow
from handlers.stylesheet import load_stylesheet, ICON_COLORS

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar

getcontext().prec = 30


class PLOT:
    """A class managing the plotting page"""

    def __init__(self, ui: Ui_MainWindow):
        self.input_file = None
        self.ui = ui
        self.canvas = None

        # Ensure plotGraphContainer is a QWidget and assign a QVBoxLayout to it
        if not hasattr(self.ui, "plotGraphLayout"):
            # self.ui.plotGraphContainer = QWidget()
            self.ui.plotGraphLayout = QVBoxLayout(self.ui.plotGraphContainer)
            self.ui.plotGraphContainer.setLayout(self.ui.plotGraphLayout)

    def generate_contour_graph(self) -> int:
        if self.input_file is None:
            return 1

        # Generate the contour plot
        file = InputFile(self.input_file)

        if file.status != 0:
            return file.status

        fig = file.get_contour_plot()
        fig2 = file.get_contour_plot()

        # create the graph
        return self.create_graph(file, fig, fig2)

    def generate_surface_graph(self, function_to_graph: str = "") -> int:
        if self.input_file is None:
            return 1
        elif function_to_graph == "":
            return 601

        # Generate the contour plot
        file = InputFile(self.input_file)

        if file.status != 0:
            return file.status

        fig = file.get_surface_plot(function_to_graph)
        fig2 = file.get_surface_plot(function_to_graph)

        # create the graph
        return self.create_graph(file, fig, fig2)

    def create_graph(self, file: InputFile, fig: matplotlib.figure, fig2: matplotlib.figure) -> int:
        if None in [file, fig]:
            return 1

        # Remove existing canvas if there is one
        if self.canvas:
            self.canvas.setParent(None)

        # Create a new FigureCanvas from the figure
        self.canvas = FigureCanvas(fig)

        # Get the layout from plotGraphContainer
        self.layout = self.ui.plotGraphLayout

        # Clear the existing layout if necessary
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Add the new canvas to the layout
        self.layout.addWidget(self.canvas)

        self.remove_button("Clear")
        self.ui.clearGraph = QPushButton("Clear")
        self.ui.clearGraph.clicked.connect(lambda: self.clear_graph(fig))
        self.ui.plotSettings.addWidget(self.ui.clearGraph)

        self.remove_button("View Graph")
        self.ui.viewGraph = QPushButton("View Graph")
        self.ui.viewGraph.clicked.connect(
            lambda: self.open_graph_dialog(self.ui, fig2)
        )
        self.ui.plotSettings.addWidget(self.ui.viewGraph)

        return 0

    def clear_graph(self, fig):
        self.remove_button("View Graph")
        self.remove_button("Clear")
        if self.canvas:
            # Remove the canvas from the layout
            self.ui.plotGraphLayout.removeWidget(self.canvas)

            # Delete the canvas widget
            self.canvas.deleteLater()

            # Set the reference to None
            self.canvas = None
        
        if fig:
            plt.close(fig)

    def open_graph_dialog(
        self, ui: Ui_MainWindow, figure: matplotlib.figure
    ) -> None:
        """Open a dialog with a full-size optimization output graph"""

        dialog = QDialog(ui.centralwidget)
        s = """
QDialog {
    background-color: $COLOR$;
}

QToolButton {
    background-color: transparent;
}
"""
        s = s.replace("$COLOR$", ui.settings.value("Popup-Color"))
        print(ui.settings.value("Popup-Color"))

        dialog.setStyleSheet(s)
        dialog.setWindowTitle("Plotting Results Graph")
        layout = QVBoxLayout()

        canvas = FigureCanvas(figure)

        toolbar = NavigationToolbar(canvas, dialog)

        for child in toolbar.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("color: white;")

        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        dialog.setLayout(layout)

        # Define a function to clean up the figure
        def cleanup():
            plt.close(figure)

        # Connect the dialog's finished signal to the cleanup function
        dialog.finished.connect(cleanup)

        dialog.show()

    def is_view_button_present(self, button_name: str):
        # Iterate through the layout to check if the button already exists
        for i in range(self.ui.plotSettings.count()):
            widget = self.ui.plotSettings.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == button_name:
                return True
        return False

    def remove_button(self, button_name: str):
        # Iterate through the layout to find the clear button
        for i in range(self.ui.plotSettings.count()):
            widget = self.ui.plotSettings.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == button_name:
                # Remove the widget from the layout
                self.ui.plotSettings.removeWidget(widget)
                # Delete the widget
                widget.deleteLater()
                break  # Exit the loop once the widget is found and removed
