import warnings
from pprint import pprint as pp
from time import time

import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from mpmath import mp
from scipy.optimize import NonlinearConstraint, minimize

from algorithms.optimization import Optimization
from algorithms.slsqp import *
from handlers.inputfnc import InputFile

warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="scipy.optimize._slsqp_py"
)
np.seterr(divide="ignore")
mp.dps = 50

GRID = 0
LHS = 1


def create_weighted_sum_function(functions):
    def weighted_sum(x, *weights):
        return sum(w * f(x) for w, f in zip(weights, functions))

    return weighted_sum


def create_grad_weighted_sum_function(grad_functions):
    def grad_weighted_sum(x, *weights):
        return sum(w * np.array(f(x)) for w, f in zip(weights, grad_functions))

    return grad_weighted_sum


def count_decimals(f):
    # Convert the float to a string
    s = str(f)

    # Find the position of the decimal point
    if "." in s:
        # Count the number of digits after the decimal point
        return len(s.split(".")[1])
    else:
        # If there's no decimal point, return 0
        return 0


def generate_combinations(num_objectives, min_weight, increment):
    _round_to = max(count_decimals(min_weight), count_decimals(increment))
    weight_range = np.arange(min_weight, 1.0 + increment, increment)
    ret = list(itertools.product(weight_range, repeat=num_objectives))
    return [[round(v, _round_to) for v in values] for values in ret]


def generate_weights(number_of_weights, min_weight=0.1, increment=0.1):
    _round_to = max(count_decimals(min_weight), count_decimals(increment))
    combos = generate_combinations(number_of_weights - 1, min_weight, increment)
    ret = []
    for c in combos:
        total = sum(c)

        if total > 1 - min_weight:
            continue

        ret.append(c + [round(1 - total, _round_to)])

    return [tuple(r) for r in ret]


def old_generate_combinations(size, min_value, increment):
    def helper(current_array, current_sum, depth):
        if depth == size:
            if abs(current_sum - 1) < 1e-9:
                results.append(tuple(current_array))
            return

        start_value = min_value
        max_possible_sum = 1
        while start_value <= max_possible_sum:
            helper(
                current_array + [start_value],
                current_sum + start_value,
                depth + 1,
            )
            start_value = round(start_value + increment, 10)

    results = []
    helper([], 0, 0)
    return results


class MultiOBJ:
    @staticmethod
    def optimize(
        input_file: InputFile,
        weights: list = [0.01, 0.01],
        grid_size: int = 5,
        tolerance: float = 1e-20,
        ftol: float = 1e-20,
        max_iter: int = 100,
        custom_gradients: bool = True,
        verbose = False,
    ):
        """Perform optimzation using scipy.minimize (SLSQP)

        Parameters
        ----------
        input_file : InputFile
            InputFile object that contains all of the data to be optimized.
        weights : list
            Weights in the form of [ min_weight, increment ]. Default is [ 0.01, 0.01 ].
        iterations : int
            The minimum number of times minimization will be performed to find the optimal solution.
        custom_gradients : bool
            Whether to use gradients from the file ( True ) or default minimization gradients ( False ).
        verbose : bool
            Whether debugging data should be printed as the optimization is performed.
        """
        t = (
            time()
        )  # save the time for figuring out how long this takes later on

        # Get input file data
        bounds = input_file.get_bounds()
        objectives = [
            create_function_from_string(clean(f, len(input_file.variables)))
            for f in input_file.get_objective_functions()
        ]
        cons = [
            [t, create_constraint_from_string(f, input_file.functions, len(input_file.variables))]
            for t, f in input_file.get_constraint_functions()
        ]

        if custom_gradients:
            obj_gradients = input_file.get_objective_gradients()
            con_gradients = input_file.get_constraint_gradients()

            size = len(input_file.variables)
            for oc in [obj_gradients, con_gradients]:
                for i in range(len(oc)):
                    for ii in range(len(oc[i])):
                        oc[i][ii] = clean(oc[i][ii], size)

            objective_function_gradients = []
            for function in obj_gradients:
                objective_function_gradients.append(
                    create_function_from_string(
                        f"[ { ', '.join( [ f for f in function ] ) } ]"
                    )
                )

            constraint_function_gradients = []
            for function in con_gradients:
                constraint_function_gradients.append(
                    create_function_from_string(
                        f"[ { ', '.join( [ f for f in function ] ) } ]"
                    )
                )

        # Get combinations
        # generate_combinations ( size, min_weight, increment )
        #       size is the number of objective functions
        #       min_weight is the minimum weight
        #       increment is the increment in the weight
        all_weights = generate_weights(len(objectives), *weights)

        # For each combo, perform SLSQP with the new objective function of: w1 * o1 + w2 * o2 + ... + wx * ox

        weighted_sum_function = create_weighted_sum_function(objectives)
        grad_weighted_sum_function = create_grad_weighted_sum_function(
            objective_function_gradients
        )

        if custom_gradients:
            nlcs = []
            for (_type, _function), grad in zip(
                cons, constraint_function_gradients
            ):
                nlcs.append(
                    NonlinearConstraint(
                        _function, 0 if _type == "eq" else -np.inf, 0, jac=grad
                    )
                )

            results = []

            for weight in all_weights:
                best = None
                
                for guess in gen_guesses(
                    bounds, samples=grid_size
                ):
                    try:
                        result = minimize(
                            weighted_sum_function,
                            x0=guess,
                            args=(weight),
                            method="SLSQP",
                            bounds=bounds,
                            jac=lambda x, *args: grad_weighted_sum_function(
                                x, *weight
                            ),
                            constraints=nlcs,
                            options={                   # I do not know why, but these parameters are the best. DO NOT TOUCH.
                                "maxiter": max_iter,    # Maximum number of iterations (default: 100)
                                "ftol": ftol,           # Tolerance for termination (function value) (default: 1e-20)
                            },
                            tol=tolerance,
                        )

                        if result.success:
                            if best is None or best.fun > result.fun:
                                best = result

                    except Exception as e:
                        print( f"ERROR: { e }" )

                if best:
                    results.append(best)

        x_values = [r.x for r in results]

        points = MultiOBJ.__calculate(input_file, x_values)
        if input_file.normalized:
            points = input_file.unnormalize_points(points)

        duration = time() - t
        if verbose:
            print(f"Total time taken: { duration }s")

        return 0, Optimization("multi", {"alg": "wsf", "pf": points, "sol": x_values}, duration)

    @staticmethod
    def __calculate(input_file: InputFile, x_values: list):
        ret = []
        functions = [
            create_function_from_string(clean(f, len(x_values[0])))
            for f in input_file.get_objective_functions()
        ]

        for x_val in x_values:
            point = []
            for function in functions:
                point.append(function(x_val))
            ret.append(point)

        return ret
