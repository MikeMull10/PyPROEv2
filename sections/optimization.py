from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QPushButton
)
from PySide6.QtCore import Qt

from testing.inputfnc2 import InputFile

class OptimizationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Optimization")

        self._setup_layout()

    def _setup_layout(self):
        main = QHBoxLayout(self)

        layout = QVBoxLayout()
        solver_type = QComboBox()
        solver_type.addItems(["SciPy", "GimOPT"])

        solver = QComboBox()
        solver.addItems(["Single", "Multi", "NSGAII", "NSGAIII"])

        layout.addWidget(solver_type)
        layout.addWidget(solver)
        
        solve = QPushButton("Solve")
        # solve.pressed.connect()

        # layout.addStretch(1)
        layout.addWidget(solve)

        results = QVBoxLayout()
        results.addWidget(QLabel("Results", alignment=Qt.AlignCenter))

        main.addLayout(layout)
        main.addLayout(results)
    
    def _solve(self, input: InputFile):
        pass
