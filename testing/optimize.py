from testing.inputfnc2 import InputFile
from testing.fnc_objects import Function

from scipy.optimize import NonlinearConstraint, minimize
from scipy.stats.qmc import LatinHypercube
import numpy as np

class Optimize:
    @staticmethod
    def single(
        input: InputFile,
        *,
        search_points: int=100,
        tolerance: float=1e-20,
    ) -> None:
        ...