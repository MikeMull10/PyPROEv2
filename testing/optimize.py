from testing.inputfnc2 import InputFile
from testing.fnc_objects import Function
from testing.optimization_data import Optimization, Opt

from scipy.optimize import NonlinearConstraint, minimize, OptimizeResult
from scipy.stats.qmc import LatinHypercube
import numpy as np
import itertools

from time import perf_counter
import warnings

warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="scipy.optimize._slsqp_py"
)
np.seterr(all='ignore')

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

        constraints: list[NonlinearConstraint] = input.get_nonlinear_constraints()

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
                if best is None or best.fun > result.fun:
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
        if len(input.objectives) == 0:
            return Optimization(Opt.FAILED, "No objective function.")
        elif len(input.objectives) == 1:
            return Optimization(Opt.FAILED, f"Not enough objective functions. Have 1 expected >1")
        
        len_objectives = len(input.objectives)
        constraints = input.get_nonlinear_constraints()

        i = 0
        opt_start_time = perf_counter()
        best_results: list[OptimizeResult] = []
        print(len_objectives)
        for weight in generate_weight_combinations(len_objectives, min_weight=min_weight, step=increment):
            func_str = ' + '.join(
                [f"{w} * {f.name}" for w, f in zip(weight, input.objectives)]
            )
            i += 1
            func = Function("", func_str, [v.symbol for v in input.variables], {con.symbol: con.value for con in input.constants})

            best_result: OptimizeResult = None
            for guess in gen_guesses(input.get_bounds(), grid_size):
                try:
                    result: OptimizeResult = minimize(
                        func,
                        x0=guess,
                        method="SLSQP",
                        bounds=input.get_bounds(),
                        constraints=constraints,
                        jac=func.jacobian,
                        tol=tolerance,
                        options={
                            "disp": False,
                            "maxiter": 1000,
                            "ftol": ftol,
                        }
                    )

                    if result.success:
                        if best_result is None or best_result.fun > result.fun:
                            best_result = result
                except Exception as e:
                    print(f"Error: {e} when running multi-obj optimization on:\n{input}")
                
            if best_result:
                best_results.append(best_result)
        
        opt_end_time = perf_counter()
        print(f"Testing: {i} -- {len(best_results)}")

        x_values = [res.x for res in best_results]
        points = []
        for x_val in x_values:
            point = []
            for obj_function in input.objectives:
                point.append(obj_function(x_val))
            points.append(point)

        return Optimization(
            Opt.SUCCESS,
            {
                'type': 'multi',
                'time': opt_end_time - opt_start_time,
                'data': {
                    'results': best_results,
                    'points': points
                }
            }
        )
