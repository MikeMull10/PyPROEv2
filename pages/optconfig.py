from decimal import getcontext

import matplotlib
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton, QVBoxLayout, QLabel

from multiprocessing import Process, Queue

from algorithms.evolution import handle_evolve
from algorithms.multiobj import MultiOBJ
from algorithms.optimization import Optimization
from algorithms.slsqp import SLSQP
from components.mplwidget import MplWidget
from handlers.inputfnc import InputFile
from handlers.errorhandler import *
from pages.mainwindow import Ui_MainWindow

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar

from multiprocessing import Process, Queue
from handlers.stylesheet import *

getcontext().prec = 30

def run(queue: Queue, method: int, file_settings: dict, ui_data: dict):
        input_file = InputFile(file_settings['file'], file_settings['is_str'], None)

        if input_file.status != 0:
            queue.put([input_file.status, None, None])
            return

        if file_settings['normalize']:
            input_file.normalize()
        
        results = None
        match method:
            case 0:  # SLSQP
                if len(input_file.objectives) > 1:
                    queue.put([ERROR_TOO_MANY_OBJECTIVES, None, None])
                    return

                obj = input_file.get_objective()

                code, output = SLSQP.optimize(
                    objective_function=obj,
                    bounds=input_file.get_bounds(),
                    constraints=input_file.get_constraint_functions(),
                    all_functions=input_file.functions,
                    obj_gradient=input_file.get_objective_gradients()[ 0 ],
                    con_gradients=input_file.get_constraint_gradients(),
                    tolerance=ui_data.get('tolerance', 1e-20),
                    grid_size=ui_data['gridsize'],
                )

                if code != 0:
                    queue.put([code, None, None])
                    return

                results = output.format_results()
                points = [output.optimization_data["sol"]]

            case 1:  # WSF
                if len(input_file.objectives) <= 1:
                    queue.put([ERROR_ONLY_ONE_OBJECTIVE, None, None])
                    return

                obj = input_file.get_objective_functions()

                code, output = MultiOBJ.optimize(
                    input_file=input_file,
                    weights=[ui_data['weight-min'], ui_data['weight-inc']],
                    grid_size=ui_data['gridsize'],
                    tolerance=ui_data.get('tolerance', 1e-20),
                    ftol=ui_data.get('wsfftol', 1e-6),
                    max_iter=ui_data.get('wsfmaxiter', 100),
                )

                if code != 0:
                    queue.put([code, None, None])
                    return
                
                results = output.format_results()
                points = output.optimization_data["pf"]

            case 2:  # NSGAII
                output = handle_evolve(
                    input_file=input_file,
                    num_iter=ui_data['numIter'],
                    population=ui_data['population'],
                    crossover=ui_data['crossover'],
                    mutation=ui_data['mutation'],
                    algorithm="NSGAII",
                )
                results = output.format_results()
                points = output.optimization_data["sol"]

            case 3:  # NSGAIII
                output = handle_evolve(
                    input_file=input_file,
                    num_iter=ui_data['numIter'],
                    crossover=ui_data['crossover'],
                    mutation=ui_data['mutation'],
                    n_partitions=ui_data['nParts'],
                    algorithm="NSGAIII",
                )
                results = output.format_results()
                points = output.optimization_data["sol"]

        queue.put([0, results, points])

vals = {
    0: ['gridsize'],
    1: ['gridsize', 'weight-min', 'weight-inc'],
    2: ['numIter', 'population', 'crossover', 'mutation'],
    3: ['numIter', 'crossover', 'mutation', 'nParts'],
}

class OPT:
    """A class managing the optimization tab"""

    def __init__(self, ui: Ui_MainWindow, handle_error: ErrorHandler):
        self.OPT_OK = 1
        self.OPT_ERROR = -1
        
        self.input_file = None
        self.input_file_is_str = False
        self.result_file = None
        self.result_file_is_str = False
        self.opt_subprocess = None
        self.points = None
        self.ui = ui
        self.ERROR_HANDLER = handle_error

        self.process = None
        self.queue = Queue()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_process)

        self.ui.optStopBtn.clicked.connect(self.stop_task)
    
    def start_task(self):
        method = self.ui.opt_solverCombo.currentIndex()

        file_settings = {
            'file': self.input_file,
            'is_str': not self.input_file_is_str,
            'normalize': self.ui.normalize_function.currentIndex() == 1 and method == 1
        }

        ui_data = {}
        to_add = vals[method]

        # populate the ui data
        for add in to_add:
            match add:
                case 'gridsize':
                    ui_data['gridsize'] = int(self.ui.opt_grid_size.text())
                case 'weight-min':
                    try:
                        float(self.ui.weights.text())
                    except:
                        return ERROR_INVALID_WEIGHT_MINIMUM
                    ui_data['weight-min'] = float(self.ui.weights.text())
                case 'weight-inc':
                    try:
                        float(self.ui.weight_increment.text())
                    except:
                        return ERROR_INVALID_WEIGHT_INCREMENT
                    ui_data['weight-inc'] = float(self.ui.weight_increment.text())
                case 'numIter':
                    ui_data['numIter'] = self.ui.opt_solverData.value()
                case 'population':
                    ui_data['population'] = self.ui.population.value()
                case 'crossover':
                    ui_data['crossover'] = self.ui.crossover.value()
                case 'mutation':
                    ui_data['mutation'] = self.ui.mutation.value()
                case 'nParts':
                    ui_data['nParts'] = self.ui.nParts.value()

        self.process = Process(target=run, args=(self.queue, method, file_settings, ui_data))
        self.process.start()

        self.ui.opt_startBtn.setEnabled(False)
        self.ui.optStopBtn.setEnabled(True)

        self.timer.start(100)  # Check every 100 ms

        return 0

    def stop_task(self):
        if self.process:
            self.process.terminate()
            self.process.join()

        self.timer.stop()
        self.ui.opt_startBtn.setEnabled(True)
        self.ui.optStopBtn.setEnabled(False)

    def check_process(self):
        if self.queue.empty():
            if not self.process.is_alive():
                # If the process has finished without sending data
                self.timer.stop()
                self.ui.opt_startBtn.setEnabled(True)
                self.ui.optStopBtn.setEnabled(False)
        else:
            # If the process has finished and sent a result
            code, results, points = self.queue.get()
            self.timer.stop()
            self.ui.opt_startBtn.setEnabled(True)
            self.ui.optStopBtn.setEnabled(False)

            if code != 0:
                self.ERROR_HANDLER.handle(code)
                return

            self.handle_finish((results, points))

    def handle_finish(self, output: tuple):
        """Output optimization results to the screen and generate a graph"""
        results, points = output
        self.result_file = results
        self.points = points

        self.ui.optEdit.setText(self.get_opt_results())

        self.ui.graphWidget = MplWidget(self, width=5, height=4, dpi=100)

        single = len(points) == 1
        x = [p[0] for p in points]
        y = [p[1] for p in points]

        self.ui.graphWidget.axes.scatter(
            x, y, c="b", marker="o", s=20 if single else 5
        )
        self.ui.graphWidget.axes.set_title(
            "Pareto Front" if not single else "Solution"
        )
        self.ui.graphWidget.axes.set_xlabel("$f_1(x)$" if not single else "$X_1$")
        self.ui.graphWidget.axes.set_ylabel("$f_2(x)$" if not single else "$X_2$")
        self.ui.graphWidget.axes.grid(True)
        self.ui.graphWidget.fig.tight_layout()

        self.ui.graphWidget.setMaximumHeight(300)

        self.remove_button("View Graph")
        self.ui.viewGraph = QPushButton("View Graph")
        self.ui.viewGraph.clicked.connect(self.open_graph_dialog)
        self.ui.optOutputLayout.addWidget(self.ui.graphWidget)
        self.ui.optLayout.addWidget(self.ui.viewGraph)

        if self.ui.settings.value("Popup-Finish") == 'true':
            QMessageBox.information(
                self.ui.centralwidget,
                "Optimization Finished",
                "The optimization process has completed.",
                QMessageBox.Ok,
            )

        self.ui.opt_clearBtn.clicked.connect(self.ui.graphWidget.delete_fig)

    def open_graph_dialog(self):
        """Open a dialog with a full-size optimization output graph"""

        dialog = QDialog(self.ui.centralwidget)
        dialog.setStyleSheet(load_stylesheet())
        dialog.setWindowTitle("Optimization Results Graph")
        dialog.setStyleSheet(f"QDialog {{ background-color: {self.ui.settings.value('Popup-Color', '#051923')}; }}")
        layout = QVBoxLayout()

        graphWidget = MplWidget(self, width=5, height=4, dpi=100)

        single = len(self.points) == 1
        x = [p[0] for p in self.points]
        y = [p[1] for p in self.points]

        graphWidget.axes.scatter(x, y, c="b", marker="o", s=20 if single else 5)
        graphWidget.axes.set_title("Pareto Front" if not single else "Solution")
        graphWidget.axes.set_xlabel("$f_1(x)$" if not single else "$X_1$")
        graphWidget.axes.set_ylabel("$f_2(x)$" if not single else "$X_2$")
        graphWidget.axes.grid(True)

        toolbar = NavigationToolbar(graphWidget, dialog)
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
        layout.addWidget(graphWidget)
        dialog.setLayout(layout)
        
        self.ui.opt_clearBtn.clicked.connect(graphWidget.delete_fig)

        dialog.show()

    def get_opt_results(self) -> str:
        """Return the optimization results file"""
        if not self.result_file:
            return "No optimization results."
        else:
            return self.result_file

    def set_solver_options(self) -> None:
        """Add the options for each solver"""

        self.ui.optLayout.removeWidget(self.ui.population_lay_2)
        self.ui.population_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.weights_lay_2)
        self.ui.weights_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.inner_lay_2)
        self.ui.inner_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.outer_lay_2)
        self.ui.outer_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.crossover_lay_2)
        self.ui.crossover_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.mutation_lay_2)
        self.ui.mutation_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.grid_lay_2)
        self.ui.grid_lay_2.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.iterations_lay)
        self.ui.iterations_lay.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.weight_increment_widget)
        self.ui.normalize_lay.setParent(None)
        self.ui.optLayout.removeWidget(self.ui.normalize_lay)
        self.ui.weight_increment_widget.setParent(None)

        def add_evolutionary_opts(population: bool = True):
            """Adds the population, crossover, and mutation items"""
            self.ui.optLayout.insertWidget(3, self.ui.mutation_lay_2)
            self.ui.optLayout.insertWidget(3, self.ui.crossover_lay_2)

            if population:
                self.ui.optLayout.insertWidget(3, self.ui.population_lay_2)

            self.ui.optLayout.insertWidget(3, self.ui.iterations_lay)

        match self.ui.opt_solverCombo.currentIndex():
            case 0:  # SLSQP
                self.ui.optLayout.insertWidget(3, self.ui.grid_lay_2)
            case 1:  # WSF
                self.ui.optLayout.insertWidget(
                    3, self.ui.weight_increment_widget
                )
                self.ui.optLayout.insertWidget(3, self.ui.weights_lay_2)
                self.ui.optLayout.insertWidget(3, self.ui.grid_lay_2)
                self.ui.optLayout.insertWidget(3, self.ui.normalize_lay)
            case 2:  # NSGAII
                add_evolutionary_opts()
            case 3:  # NSGAIII
                self.ui.optLayout.insertWidget(3, self.ui.outer_lay_2)
                add_evolutionary_opts()

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
