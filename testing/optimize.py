from testing.inputfnc2 import InputFile
from testing.fnc_objects import Function
from testing.optimization_data import Optimization, Opt

from scipy.optimize import NonlinearConstraint, minimize, OptimizeResult
from scipy.stats.qmc import LatinHypercube
import numpy as np
import itertools

from time import perf_counter

def gen_guesses(bounds, samples: int = 5):
    return itertools.product(
        *[np.linspace(_min, _max, samples) for _min, _max in bounds]
    )

def generate_weight_combinations(n: int, min_weight: float, step: float):
    total_units = int(round((1.0 - n * min_weight) / step))

    for parts in integer_partitions(n, total_units):
        yield [round(min_weight + step * p, 10) for p in parts]

def integer_partitions(n: int, total: int):
    """Generate all compositions of `total` into `n` non-negative integers."""
    if n == 1:
        yield [total]
    else:
        for i in range(total + 1):
            for tail in integer_partitions(n - 1, total - i):
                yield [i] + tail

class Optimize:
    @staticmethod
    def single(
        input: InputFile,
        *,
        grid_size: int=5,
        tolerance: float=1e-20,
    ) -> Optimization:
        if len(input.objectives) == 0:
            return Optimization(Opt.FAILED, "No objective function.")
        elif len(input.objectives) > 1:
            return Optimization(Opt.FAILED, f"Too many objective functions. Have {len(input.objectives)} expected 1")

        constraints: list[NonlinearConstraint] = []
        for eq in input.equality_constraints:
            constraints.append(NonlinearConstraint(
                eq,
                0,
                0,
                jac=eq.jacobian,
            ))
        for ineq in input.inequality_constraints:
            constraints.append(NonlinearConstraint(
                ineq,
                -np.inf,
                0,
                jac=ineq.jacobian,
            ))

        opt_start_time = perf_counter()
        fails = 0
        best: OptimizeResult = None
        for guess in gen_guesses(input.get_bounds(), samples=grid_size):
            try:
                result: OptimizeResult = minimize(
                    input.objectives[0],
                    x0=guess,
                    method="SLSQP",
                    bounds=input.get_bounds(),
                    constraints=constraints,
                    jac=input.objectives[0].jacobian,
                    tol=tolerance,
                    options={"disp": False,
                             "maxiter": 1000,
                             "ftol": tolerance}
                )
            except Exception as e:
                print(f"Error: {e} when running single-obj optimization on:\n{input}")
            
            if result.success:
                if best is None:
                    best = result
                else:
                    if best.fun > result.fun:
                        best = result
            else:
                fails += 1
        
        opt_end_time = perf_counter()
        print(f"FAILED: {fails} / {grid_size ** len(input.variables)} ({(100 * fails / (grid_size ** len(input.variables))):2f}%)")
        if best is None:
            return Optimization(Opt.FAILED, f"No successful solution found with {grid_size ** len(input.variables)} initial points.")
        
        return Optimization(
            Opt.SUCCESS,
            {
                'type': 'single',
                'time': opt_end_time - opt_start_time,
                'data': best
            }
        )
    
    @staticmethod
    def multi(
        input: InputFile,
        min_weight: float=0.01,
        increment: float=0.01,
        *,
        grid_size: int=5,
        tolerance: float=1e-20,
        ftol: float=1e-20,
    ) -> Optimization:
        i = 0
        for w in generate_weight_combinations(3, min_weight=min_weight, step=increment):
            i += 1
            print(w)
        
        print(i)

        return Optimization()
