from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLayout, QApplication
)
from PySide6.QtCore import Qt, QTimer

from qfluentwidgets import SpinBox, DoubleSpinBox, ComboBox, PushButton, PrimaryPushButton

from testing.inputfnc2 import InputFile
from testing.optimize import Optimize as Opt
from testing.optimize import EvolutionType
from testing.optimization_data import Opt as OptStatus
from testing.optimization_data import Optimization as OptObj

from components.clickabletitle import ClickableTitleLabel

from sections.designofexperiments import make_row

from sections.graph import ToggleWidget, MplWidget

from multiprocessing import Process, Queue
import numpy as np

from enum import Enum

class METHOD_TYPE(Enum):
    SciPy  = 0
    GimOPT = 1

class METHOD(Enum):
    Single  = 0
    Multi   = 1
    NSGAII  = 2
    NSGAIII = 3

def run(queue: Queue, method_type: METHOD_TYPE, method: METHOD, file: str, settings: dict):
    file_str = file
    file: InputFile = InputFile(file, is_file=False)

    res = None
    ### --- SciPy ---
    if method_type == METHOD_TYPE.SciPy:
        match method:
            case METHOD.Single:
                if len(file.objectives) > 1:
                    queue.put(["You are a dumbass"])
                    return

                res = Opt.single(file, grid_size=settings.get('gridsize', 5), tolerance=settings.get('tolerance', 1e-20))
            case METHOD.Multi:
                if len(file.objectives) <= 1:
                    queue.put(["You are a dumbass"])
                    return
                
                res = Opt.multi(
                    input=file,
                    min_weight=settings.get('min_weight', 0.01),
                    increment=settings.get('increment', 0.01),
                    grid_size=settings.get('gridsize', 5),
                    tolerance=settings.get('tolerance', 1e-20),
                    ftol=settings.get('ftol', 1e-20)
                )
            case METHOD.NSGAII:
                if len(file.objectives) <= 1:
                    queue.put(["Error"])
                    return

                res = Opt.evolve(
                    file,
                    generations=settings.get('generations', 1000),
                    population=settings.get('population', 200),
                    crossover_rate=settings.get('crossover', 0.9),
                    mutation_rate=settings.get('mutation', 0.01),
                    partitions=settings.get('partition', 100),
                    algorithm=EvolutionType.NSGAII,
                )
            case METHOD.NSGAIII:
                if len(file.objectives) <= 1:
                    queue.put(["Error"])
                    return

                res = Opt.evolve(
                    file,
                    generations=settings.get('generations', 1000),
                    population=settings.get('population', 200),
                    crossover_rate=settings.get('crossover', 0.9),
                    mutation_rate=settings.get('mutation', 0.01),
                    partitions=settings.get('partition', 100),
                    algorithm=EvolutionType.NSGAIII,
                )
        
        if res:
            res.fnc = file_str
        queue.put([res])
        return
    
    ### --- GimOPT ---
    # TODO: Implement GimOPT :)

def clear_layout(layout: QLayout):
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)

        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
            continue

        child = item.layout()
        if child is not None:
            clear_layout(child)
            child.setParent(None)
            child.deleteLater()

    layout.invalidate()
    QApplication.processEvents()

class NoTrailingZerosSpinBox(DoubleSpinBox):
    def textFromValue(self, value: float) -> str:
        # Format without trailing zeros
        return ('{0:.10f}'.format(value)).rstrip('0').rstrip('.') 

class OptimizationPage(QWidget):
    def __init__(self, formpage=None):
        super().__init__()
        self.setObjectName("Optimization")
        self.section_title = ClickableTitleLabel("Optimization")
        self.section_title.clicked.connect(self.toggle_collapse)
        self.showing = True
        self.formpage = formpage

        self._setup_layout()

    def _setup_layout(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        opt_wrapper = QVBoxLayout()
        opt_wrapper.addWidget(self.section_title)
        opt_wrapper.setAlignment(Qt.AlignTop)
        self.options_section_widget = QWidget()
        opt_wrapper.addWidget(self.options_section_widget)
        self.layout = QVBoxLayout(self.options_section_widget)

        # --- Solver Type Row ---
        self.solver_type = ComboBox()
        self.solver_type.addItems(["SciPy", "GimOPT"])
        self.solver_type_row = make_row("Solver:", self.solver_type)
        self.layout.addWidget(self.solver_type_row)

        # --- Solver Row ---
        self.solver = ComboBox()
        self.solver.addItems(["Single", "Multi", "NSGAII", "NSGAIII"])
        self.solver.currentTextChanged.connect(self._rebuild)
        self.solver_row = make_row("Solver Type:", self.solver)
        self.layout.addWidget(self.solver_row)

        ### --- Solver Options ---
        # --- Grid Size Row ---
        self.gridsize = SpinBox()
        self.gridsize.setValue(5)
        self.gridsize.setMaximum(10000)
        self.gridsize.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.gridsize_row = make_row("Grid Size:", self.gridsize)
        self.gridsize_row.setToolTip("Determines the number of equally spaced samples generated along each dimension in the grid. A higher grid size increases the number of guesses by creating a finer grid, while a lower grid size reduces the number of guesses by creating a coarser grid.")
        self.layout.addWidget(self.gridsize_row)

        # --- Weight Minimum ---
        self.weight_min = NoTrailingZerosSpinBox()
        self.weight_min.setDecimals(6)
        self.weight_min.setSingleStep(0.01)
        self.weight_min.setMinimum(0)
        self.weight_min.setMaximum(1)
        self.weight_min.setValue(0.01)
        self.weight_min.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.weight_min_row = make_row("Minimum Weight:", self.weight_min)
        self.weight_min_row.setToolTip("Defines the lower bound for weights in weighted formulations.")
        self.layout.addWidget(self.weight_min_row)

        # --- Weight Increment ---
        self.weight_increment = NoTrailingZerosSpinBox()
        self.weight_increment.setDecimals(6)
        self.weight_increment.setSingleStep(0.01)
        self.weight_increment.setMinimum(1e-6)
        self.weight_increment.setMaximum(0.1)
        self.weight_increment.setValue(0.01)
        self.weight_increment.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.weight_increment_row = make_row("Weight Increment:", self.weight_increment)
        self.weight_increment_row.setToolTip("Defines the adjustment interval for weights.")
        self.layout.addWidget(self.weight_increment_row)

        # --- Iterations Row ---
        self.iterations = SpinBox()
        self.iterations.setMaximum(100000)
        self.iterations.setValue(1000)
        self.iterations.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.iterations_row = make_row("Iterations:", self.iterations)
        self.iterations_row.setToolTip("Defines the number of cycles the algorithm will run.")
        self.layout.addWidget(self.iterations_row)

        # --- Population Row ---
        self.population = SpinBox()
        self.population.setMinimum(1)
        self.population.setMaximum(10000)
        self.population.setValue(100)
        self.population.setSingleStep(100)
        self.population.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.population_row = make_row("Population:", self.population)
        self.population_row.setToolTip("Defines the number of candidate solutions in the optimization process.")
        self.layout.addWidget(self.population_row)

        # --- Crossover ---
        self.crossover = NoTrailingZerosSpinBox()
        self.crossover.setDecimals(10)
        self.crossover.setMinimum(0)
        self.crossover.setMaximum(1)
        self.crossover.setValue(0.9)
        self.crossover.setSingleStep(0.1)
        self.crossover.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.crossover_row = make_row("Crossover Rate:", self.crossover)
        self.crossover_row.setToolTip("Defines the frequency of random genetic changes.")
        self.layout.addWidget(self.crossover_row)

        # --- Mutation Row ---
        self.mutation = NoTrailingZerosSpinBox()
        self.mutation.setDecimals(10)
        self.mutation.setMinimum(1e-10)
        self.mutation.setMaximum(1)
        self.mutation.setValue(0.01)
        self.mutation.setSingleStep(0.1)
        self.mutation.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.mutation_row = make_row("Mutation Rate:", self.mutation)
        self.mutation_row.setToolTip("Controls the probability of recombination.")
        self.layout.addWidget(self.mutation_row)

        # --- Partitions Row ---
        self.partitions = SpinBox()
        self.partitions.setMinimum(0)
        self.partitions.setMaximum(1e6)
        self.partitions.setValue(100)
        self.partitions.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.partitions_row = make_row("Partitions:", self.partitions)
        self.layout.addWidget(self.partitions_row)

        self._rebuild()

        # --- Buttons ---
        self.start = PrimaryPushButton("Start")
        self.stop  = PushButton("Stop")
        self.stop.setEnabled(False)
        self.stop.pressed.connect(lambda: self._stop_solve())
        self.clear = PushButton("Clear")
        for btn, name in zip([self.start, self.stop, self.clear], ["btnOptStart", "btnOptStop", "btnOptClear"]):
            btn.setObjectName(name)
            btn.setCursor(Qt.PointingHandCursor)

        self.btns_layout = QHBoxLayout()
        self.btns_layout.addWidget(self.start)
        self.btns_layout.addWidget(self.stop)
        self.btns_layout.addWidget(self.clear)
        self.layout.addStretch()  # push buttons to bottom
        self.layout.addLayout(self.btns_layout)

        self.results_widget = QWidget()
        self.results = QVBoxLayout(self.results_widget)

        self.toggle = ToggleWidget()
        self.results.addWidget(self.toggle)

        main.addLayout(opt_wrapper)
        self.layout.addWidget(self.results_widget)
        if self.formpage:
            main.addWidget(self.formpage)
            main.setStretch(0, 1)
            main.setStretch(1, 1)

        ### --- Solving ---
        self.process: Process = None
        self.queue: Queue = Queue()

        self.timer: QTimer = QTimer()
        self.timer.timeout.connect(self._check_process)

    def _rebuild(self):
        text = self.solver.currentText()
        self.gridsize_row.setVisible(text in ["Single", "Multi"])
        self.weight_min_row.setVisible(text == "Multi")
        self.weight_increment_row.setVisible(text == "Multi")
        self.iterations_row.setVisible(text in ["NSGAII", "NSGAIII"])
        self.population_row.setVisible(text == "NSGAII")
        self.crossover_row.setVisible(text in ["NSGAII", "NSGAIII"])
        self.mutation_row.setVisible(text in ["NSGAII", "NSGAIII"])
        self.partitions_row.setVisible(text == "NSGAIII")
    
    def _solve(self, input: str):
        settings = {
            'gridsize': self.gridsize.value(),
            'min_weight': self.weight_min.value(),
            'increment': self.weight_increment.value(),
            'generations': self.iterations.value(),
            'population': self.population.value(),
            'crossover': self.crossover.value(),
            'mutation': self.mutation.value(),
            'partitions': self.partitions.value(),
        }

        self.process = Process(target=run, args=(self.queue, 
                                                 METHOD_TYPE.SciPy, 
                                                 METHOD(self.solver.currentIndex()),
                                                 input,
                                                 settings))
        self.process.start()

        # --- Enable Start & Stop Buttons ---
        self.start.setEnabled(False)
        self.stop .setEnabled(True)

        self.timer.start(100)
    
    def _stop_solve(self):
        if self.process:
            self.process.terminate()
            self.process.join()

        self.timer.stop()

        self.start.setEnabled(True)
        self.stop .setEnabled(False)

    def _check_process(self):
        if self.queue.empty():
            if not self.process.is_alive():
                # If the process has finished without sending data
                self.timer.stop()
                self.start.setEnabled(True)
                self.stop.setEnabled(False)
        else:
            # If the process has finished and sent a result
            [data] = self.queue.get()
            self.timer.stop()
            self.start.setEnabled(True)
            self.stop.setEnabled(False)

            self.handle_finish(data)
    
    def handle_finish(self, opt: OptObj):
        if opt.status == OptStatus.FAILED:
            return

        if opt['type'] == 'single':
            self.toggle.stack.setCurrentIndex(0)
        else:
            self.toggle.stack.setCurrentIndex(1)

        self.toggle.text_edit.setText(str(opt))

        match opt['type']:
            case 'single':
                self.toggle.graph.plot(np.array([opt['data'].x]))
            case 'multi':
                self.toggle.graph.plot(np.array(opt['data']['points']))
            case _:
                ...

        self.toggle.graph.draw()

    def toggle_collapse(self):
        self.showing ^= True
        
        if self.showing:
            self.options_section_widget.show()
            self.formpage.show()
        else:
            self.options_section_widget.hide()
            self.formpage.hide()
