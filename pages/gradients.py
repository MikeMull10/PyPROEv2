from decimal import getcontext
from pprint import pprint as pp

import matplotlib
import numpy as np
from platypus.core import FixedLengthArray
from PySide6.QtCore import QThread
from PySide6.QtWidgets import (QDialog, QMessageBox, QPushButton, QVBoxLayout,
                               QWidget)

from algorithms.evolution import handle_evolve
from algorithms.multiobj import MultiOBJ
from algorithms.slsqp import SLSQP
from components.mplwidget import MplWidget, MplWidget2
from handlers.inputfnc import InputFile, add_spaces_to_expression
from pages.mainwindow import Ui_MainWindow

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar

from handlers.errorhandler import ErrorHandler

getcontext().prec = 30


class GRAD:
    """A class managing the gradients page"""

    def __init__(self, ui: Ui_MainWindow, eh: ErrorHandler):
        self.ui = ui
        self.eh = eh
        self.input_file = None
        self.file_data = ""

    def get_gradients(self) -> int:
        if self.input_file is None:
            return 1

        file = InputFile(self.input_file)

        if file.status != 0:
            return file.status  # make sure that the file is good

        gradients = file.calculate_gradients()

        for g in gradients:
            gradients[g] = add_spaces_to_expression(str(gradients[g]))

        file.gradients = gradients
        file.data["GRADIENTS"] = gradients

        txt = file.generate_fnc_file()
        self.ui.gradientOutput.setPlainText(txt)
        self.file_data = txt

        # if not self.is_view_button_present("Re-calculate"):
        #     self.ui.recalc = QPushButton("Re-calculate")
        #     self.ui.recalc.clicked.connect(self.re_calc_grads)
        #     self.ui.gradientSettings.addWidget(self.ui.recalc)

        return 0

    def gen_file(self):
        return self.file_data

    def re_calc_grads(self):
        text = self.ui.gradientOutput.toPlainText()

        if text == "": return 0

        file = InputFile(text, is_file=False)

        if file.status != 0:
            self.eh.handle(file.status)
            return file.status

        gradients = file.calculate_gradients()

        for g in gradients:
            gradients[g] = add_spaces_to_expression(str(gradients[g]))

        file.gradients = gradients
        file.data["GRADIENTS"] = gradients

        if file.status != 0:
            self.eh.handle(file.status)
            return file.status

        txt = file.generate_fnc_file()
        self.ui.gradientOutput.setPlainText(txt)
        self.file_data = txt

        return 0
    
    def normalize(self):
        if self.input_file is None:
            return 1

        file = InputFile(self.input_file)

        if file.status != 0:
            return file.status  # make sure that the file is good

        file.normalize()

        for f in file.functions:
            func = add_spaces_to_expression( file.functions[ f ] )
            file.functions[ f ] = func
            file.data[ 'FUNCTION' ][ f ] = func
        
        for g in file.gradients:
            grad = add_spaces_to_expression( file.gradients[ g ] )
            file.gradients[ g ] = grad
            file.data[ 'GRADIENT' ][ g ] = grad

        txt = file.generate_fnc_file()
        self.ui.gradientOutput.setPlainText(txt)
        self.file_data = txt
        
        return 0

    def get_blank_template(self):
        data  = "### BLANK TEMPLATE ###\n\n"
        data += "*VARIABLE:\n"
        data += "X1: 0, 1\n\n"
        data += "*OBJECTIVE:\n"
        data += "O1 = F1;\n\n"
        data += "*EQUALITY-CONSTRAINT:\n"
        data += "#EC1 = ;\n\n"
        data += "*INEQUALITY-CONSTRAINT:\n"
        data += "#INEC1 = ;\n\n"
        data += "*FUNCTION:\n"
        data += "F1 = X1;\n\n"
        data += "# PRESS `GENERATE GRADIENTS` to automatically generate the gradients for this problem."

        return data

    def is_view_button_present(self, button_name: str):
        # Iterate through the layout to check if the button already exists
        for i in range(self.ui.gradientSettings.count()):
            widget = self.ui.gradientSettings.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == button_name:
                return True
        return False

    def remove_button(self, button_name: str):
        # Iterate through the layout to find the clear button
        for i in range(self.ui.gradientSettings.count()):
            widget = self.ui.gradientSettings.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == button_name:
                # Remove the widget from the layout
                self.ui.gradientSettings.removeWidget(widget)
                # Delete the widget
                widget.deleteLater()
                break  # Exit the loop once the widget is found and removed
