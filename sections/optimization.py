from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QSpacerItem, QSizePolicy, QPushButton, QLineEdit,
    QLayout, QApplication, QFormLayout, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIntValidator, QFont

from testing.inputfnc2 import InputFile
from testing.optimize import Optimize as Opt

from multiprocessing import Process, Queue

from enum import Enum

class METHOD_TYPE(Enum):
    SciPy  = 0
    GimOPT = 1

class METHOD(Enum):
    Single  = 0
    Multi   = 1
    NSGAII  = 2
    NSGAIII = 3

def run(queue: Queue, method_type: METHOD_TYPE, method: METHOD, file: InputFile, settings: dict):
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
                    queue.put(["You are a dumbass"])
                    return

                # TODO: Implement NSGAII
            case METHOD.NSGAIII:
                if len(file.objectives) <= 1:
                    queue.put(["You are a dumbass"])
                    return

                # TODO: Implement NSGAIII

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
            # detach + schedule destruction
            w.setParent(None)
            w.deleteLater()
            continue

        child = item.layout()
        if child is not None:
            clear_layout(child)          # recurse
            child.setParent(None)
            child.deleteLater()

        # QSpacerItem? nothing to do; it’s owned by the layout item and will be GC’d

    # tidy up geometry
    layout.invalidate()
    # let deleteLater() run if you need it to disappear immediately
    QApplication.processEvents()

class NoTrailingZerosSpinBox(QDoubleSpinBox):
    def textFromValue(self, value: float) -> str:
        # Format without trailing zeros
        return ('{0:.10f}'.format(value)).rstrip('0').rstrip('.') 

class OptimizationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Optimization")

        self._setup_layout()

    def _setup_layout(self):
        main = QHBoxLayout(self)
        self.set_max_height()

        self.layout = QVBoxLayout()

        # --- Row helper function ---
        def make_row(label_text, widget):
            row = QWidget()
            layout = QHBoxLayout(row)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)
            label = QLabel(label_text)
            layout.addWidget(label)
            layout.addWidget(widget)
            row.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            return row

        # --- Solver Type Row ---
        self.solver_type = QComboBox()
        self.solver_type.addItems(["SciPy", "GimOPT"])
        self.solver_type_row = make_row("Solver:", self.solver_type)
        self.layout.addWidget(self.solver_type_row)
        self.layout.addSpacing(10)

        # --- Solver Row ---
        self.solver = QComboBox()
        self.solver.addItems(["Single", "Multi", "NSGAII", "NSGAIII"])
        self.solver.currentTextChanged.connect(self._rebuild)
        self.solver_row = make_row("Solver Type:", self.solver)
        self.layout.addWidget(self.solver_row)
        self.layout.addSpacing(10)

        ### --- Solver Options ---
        # --- Grid Size Row ---
        self.gridsize = QSpinBox()
        self.gridsize.setValue(5)
        self.gridsize.setMaximum(10000)
        self.gridsize.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.gridsize_row = make_row("Grid Size:", self.gridsize)
        self.layout.addWidget(self.gridsize_row)
        self.layout.addSpacing(10)

        # --- Weight Minimum ---
        self.weight_min = NoTrailingZerosSpinBox()
        self.weight_min.setDecimals(6)
        self.weight_min.setSingleStep(0.01)
        self.weight_min.setMinimum(0)
        self.weight_min.setMaximum(1)
        self.weight_min.setValue(0.1)
        self.weight_min.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.weight_min_row = make_row("Minimum Weight:", self.weight_min)
        self.layout.addWidget(self.weight_min_row)
        self.layout.addSpacing(10)

        # --- Weight Increment ---
        self.weight_increment = NoTrailingZerosSpinBox()
        self.weight_increment.setDecimals(6)
        self.weight_increment.setSingleStep(0.01)
        self.weight_increment.setMinimum(1e-6)
        self.weight_increment.setMaximum(0.1)
        self.weight_increment.setValue(0.1)
        self.weight_increment.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.weight_increment_row = make_row("Weight Increment:", self.weight_increment)
        self.layout.addWidget(self.weight_increment_row)
        self.layout.addSpacing(10)

        # --- Iterations Row ---
        self.iterations = QSpinBox()
        self.iterations.setMaximum(100000)
        self.iterations.setValue(1000)
        self.iterations.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.iterations_row = make_row("Iterations:", self.iterations)
        self.layout.addWidget(self.iterations_row)
        self.layout.addSpacing(10)

        # --- Population Row ---
        self.population = QSpinBox()
        self.population.setMinimum(1)
        self.population.setMaximum(10000)
        self.population.setValue(100)
        self.population.setSingleStep(100)
        self.population.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.population_row = make_row("Population:", self.population)
        self.layout.addWidget(self.population_row)
        self.layout.addSpacing(10)

        self.mutation = QSpinBox()
        self.mutation.setMinimum(1)
        self.mutation.setMaximum(100)
        self.mutation.setValue(1)
        self.mutation.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.mutation_row = make_row("Mutation:", self.mutation)
        self.layout.addWidget(self.mutation_row)
        self.layout.addSpacing(10)

        self._rebuild()

        # --- Buttons ---
        self.start = QPushButton("Start")
        self.start.pressed.connect(lambda: self._solve(None))
        self.stop  = QPushButton("Stop")
        self.stop.setEnabled(False)
        self.stop.pressed.connect(lambda: self._stop_solve())
        self.clear = QPushButton("Clear")
        for btn, name in zip([self.start, self.stop, self.clear], ["btnOptStart", "btnOptStop", "btnOptClear"]):
            btn.setObjectName(name)
            btn.setCursor(Qt.PointingHandCursor)

            font = btn.font()
            font.setBold(True)
            font.setWeight(QFont.Weight.Bold)
            btn.setFont(font)

        self.btns_layout = QHBoxLayout()
        self.btns_layout.addWidget(self.start)
        self.btns_layout.addWidget(self.stop)
        self.btns_layout.addWidget(self.clear)
        self.layout.addStretch()  # push buttons to bottom
        self.layout.addLayout(self.btns_layout)

        main.addLayout(self.layout)
        # Add results panel as before
        results = QVBoxLayout()
        results.addWidget(QLabel("Results", alignment=Qt.AlignCenter))
        main.addLayout(results)

        ### --- Solving ---
        self.process: Process = None
        self.queue: Queue = Queue()

        self.timer: QTimer = QTimer()

    def _rebuild(self):
        text = self.solver.currentText()
        self.gridsize_row.setVisible(text in ["Single", "Multi"])
        self.weight_min_row.setVisible(text == "Multi")
        self.weight_increment_row.setVisible(text == "Multi")
        self.iterations_row.setVisible(text in ["NSGAII", "NSGAIII"])
        self.population_row.setVisible(text in ["NSGAII", "NSGAIII"])
        self.mutation_row.setVisible(text in ["NSGAII", "NSGAIII"])
    
    def _solve(self, input: InputFile):
        # TODO: Add prep
        settings = {}

        # self.process = Process(target=run, args=(self.queue, 
        #                                          METHOD_TYPE.SciPy, 
        #                                          METHOD.Single,
        #                                          input,
        #                                          settings))
        # self.process.start()

        # TODO: Enable/disable start/stop buttons
        self.start.setEnabled(False)
        self.stop .setEnabled(True)

        self.timer.start(100)
    
    def _stop_solve(self):
        self.start.setEnabled(True)
        self.stop .setEnabled(False)

    def set_max_height(self):
        app = QApplication.instance() or QApplication([])

        # Assuming self is your OptimizationPage QWidget
        screen = app.primaryScreen()
        screen_height = screen.size().height()

        # Set maximum height to one third of the screen height
        self.setMaximumHeight(screen_height // 3)
