from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QSpacerItem, QSizePolicy, QPushButton, QLineEdit,
    QLayout, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIntValidator

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


class OptimizationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Optimization")

        self._setup_layout()

    def _setup_layout(self):
        main = QHBoxLayout(self)

        self.layout: QVBoxLayout = QVBoxLayout()
        self.solver_type_layout = QVBoxLayout()
        self.solver_type_layout.addWidget(QLabel("Solver:"))
        self.solver_type = QComboBox()
        self.solver_type.addItems(["SciPy", "GimOPT"])
        self.solver_type_layout.addWidget(self.solver_type)
        self.solver_type_layout.setContentsMargins(0, 0, 0, 0)
        self.solver_type_layout.setSpacing(2)  # small space between label and combo box

        self.solver: QComboBox = QComboBox()
        self.solver.addItems(["Single", "Multi", "NSGAII", "NSGAIII"])

        self.solver.currentTextChanged.connect(self._rebuild)
        
        ### --- Solver Options ---
        self.gridsize: QLineEdit = QLineEdit()
        self.gridsize.setValidator(QIntValidator())
        self.gridsize.setText('5')
        self.gridsize.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        ### --- Start/Stop/Clear Buttons ---
        self.start = QPushButton("Start")
        self.stop  = QPushButton("Stop")
        self.clear = QPushButton("Clear")
        self.start.setObjectName("btnOptStart")
        self.stop.setObjectName("btnOptStop")
        self.clear.setObjectName("btnOptClear")
        self.btns_layout = QHBoxLayout()
        self.btns_layout.addWidget(self.start)
        self.btns_layout.addWidget(self.stop)
        self.btns_layout.addWidget(self.clear)
        [btn.setCursor(Qt.PointingHandCursor) for btn in [self.start, self.stop, self.clear]]

        ### --- Add Widgets ---
        self._build()
        self._rebuild()

        results = QVBoxLayout()
        results.addWidget(QLabel("Results", alignment=Qt.AlignCenter))

        main.addLayout(self.layout)
        main.addLayout(results)

        ### --- Solving ---
        self.process: Process = None
        self.queue: Queue = Queue()

        self.timer: QTimer = QTimer()
    
    def _solve(self, input: InputFile):
        # TODO: Add prep
        settings = {}

        self.process = Process(target=run, args=(self.queue, 
                                                 METHOD_TYPE.SciPy, 
                                                 METHOD.Single,
                                                 input,
                                                 settings))
        self.process.start()

        # TODO: Enable/disable start/stop buttons

        self.timer.start(100)

    def _build(self):
        clear_layout(self.layout)

        self.layout.addLayout(self.solver_type_layout)
        # self.layout.addStretch()
        self.layout.addWidget(self.solver)
        # self.layout.addStretch()
        self.layout.addWidget(self.gridsize)
        # self.layout.addStretch()
        self.layout.addLayout(self.btns_layout)
    
    def _rebuild(self):
        self.gridsize.setVisible(self.solver.currentText() in ["Single", "Multi"])
