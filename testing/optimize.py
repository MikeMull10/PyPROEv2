from testing.inputfnc2 import InputFile
from testing.fnc_objects import Function
from testing.optimization_data import Optimization, Opt

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.problems.functional import FunctionalProblem
from pymoo.optimize import minimize as pyminimize

from scipy.optimize import NonlinearConstraint, minimize, OptimizeResult
from scipy.stats.qmc import LatinHypercube
import numpy as np
import itertools

from time import perf_counter
import warnings

from enum import Enum

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

### This is WAYYY faster than just making new Functions each time
def generate_multi(functions: list[Function]) -> callable:
    def wrapper(x, weights: list[float]):
        return sum(
            w * f(x) for w, f in zip(weights, functions)
        )
    
    return wrapper

def generate_weighted_jacobian(functions: list[Function]) -> callable:
    def wrapper(vals: list[float], weights: list[float]):
        weighted_jacs = [w * np.array(f.jacobian(vals)) for w, f in zip(weights, functions)]
        return np.sum(weighted_jacs, axis=0)
    
    return wrapper

class EvolutionType(Enum):
    NSGAII  = 0
    NSGAIII = 1

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
        total, failed = 0, 0
        best: OptimizeResult = None
        for guess in gen_guesses(input.get_bounds(), samples=grid_size):
            total += 1
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
                failed += 1
        
        opt_end_time = perf_counter()
        # print(f"FAILED: {failed} / {grid_size ** len(input.variables)} ({(100 * failed / (grid_size ** len(input.variables))):2f}%)")
        if best is None:
            return Optimization(Opt.FAILED, f"No successful solution found with {grid_size ** len(input.variables)} initial points.")
        
        return Optimization(
            Opt.SUCCESS,
            {
                'type': 'single',
                'time': opt_end_time - opt_start_time,
                'data': best,
                'success_rate': 1 - failed / total
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
            return Optimization(Opt.FAILED, f"Not enough objective functions. Have 1 expected >1 ({len(input.objectives)}).")
        
        len_objectives = len(input.objectives)
        constraints = input.get_nonlinear_constraints()

        multi_func = generate_multi(input.functions)
        multi_jac = generate_weighted_jacobian(input.functions)

        opt_start_time = perf_counter()
        total, failed = 0, 0
        best_results: list[OptimizeResult] = []
        guesses = list(gen_guesses(input.get_bounds(), grid_size))
        for weight in generate_weight_combinations(len_objectives, min_weight=min_weight, step=increment):
            total += 1
            def objective(x):
                return multi_func(x, weight)
            def jacobian(x):
                return multi_jac(x, weight)

            best_result: OptimizeResult = None
            for guess in guesses:
                try:
                    result: OptimizeResult = minimize(
                        objective,
                        x0=guess,
                        method="SLSQP",
                        bounds=input.get_bounds(),
                        constraints=constraints,
                        jac=jacobian,
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
            else:
                failed += 1
        
        opt_end_time = perf_counter()

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
                },
                'success_rate': 1 - failed / total
            }
        )
    
    @staticmethod
    def evolve(input: InputFile,
               generations: int=1000,
               population: int=200,
               crossover_rate: float=0.9,
               mutation_rate: float=0.01,
               partitions: int=100,
               algorithm: EvolutionType=EvolutionType.NSGAII,
               seed: int=0,
    ) -> Optimization:
        problem = FunctionalProblem(
            n_var=len(input.variables),
            objs=input.objectives,
            constr_eq=input.equality_constraints,
            constr_ieq=input.inequality_constraints,
            xl=[var.min for var in input.variables],
            xu=[var.max for var in input.variables],
        )
        
        # SBX is simulated binary crossover - 90% probability of mutation
        # PM is polynomial mutation - 1% probability rate
        cross = SBX(crossover_rate)
        poly_mut = PM(prob=mutation_rate)
        algo = None

        results = {"crs": crossover_rate, "mut": mutation_rate}
        if algorithm == EvolutionType.NSGAII:
            algo = NSGA2(pop_size=population, crossover=cross, mutation=poly_mut)
            results["pop"] = population
        elif algorithm == EvolutionType.NSGAIII:
            ref_dirs = get_reference_directions("uniform", len(input.objectives), n_partitions=partitions)
            algo = NSGA3(pop_size=population, crossover=cross, mutation=poly_mut, ref_dirs=ref_dirs)
            results["n_parts"] = partitions
        else:
            raise Exception("Invalid algorithm. Please choose either NSGAII or NSGAIII.")

        t = perf_counter()
        res = pyminimize(
            problem,
            algo,
            ('n_gen', generations),
            seed=seed,
            verbose=False,
        )
        duration = perf_counter() - t

        if res.F is None or len(res.F) == 0:
            return Optimization(Opt.FAILED, {'error': 'No solutions found.'})

        results["sols"] = res.F
        results["time"] = duration
        results["alg"]  = "NSGAII" if algorithm == EvolutionType.NSGAII else "NSGAIII"

        return Optimization(
            Opt.SUCCESS,
            {
                'type': results['alg'],
                'time': results['time'],
                'data': {
                    'crossover_rate': results['crs'],
                    'mutation_rate': results['mut'],
                    'pop' if 'pop' in results else 'n_parts': results.get('pop', results.get('n_parts', None)),
                    'sols': results['sols']
                }
            }
        )
