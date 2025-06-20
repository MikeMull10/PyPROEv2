import sys

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# https://www.pythonguis.com/tutorials/pyside-plotting-matplotlib/


class MplWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, nav=False):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplWidget, self).__init__(self.fig)
    
    def delete_fig(self):
        plt.close(self.fig)
    
    def __del__(self):
        self.delete_fig()


class MplWidget2(FigureCanvasQTAgg):
    def __init__(self, figure):
        self.fig = figure
        super(MplWidget2, self).__init__(self.fig)
