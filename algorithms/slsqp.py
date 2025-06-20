import itertools
import warnings
from time import time

import numpy as np
from mpmath import mp
from scipy.optimize import NonlinearConstraint, minimize
from scipy.stats.qmc import LatinHypercube

from algorithms.optimization import Optimization
from handlers.inputfnc import clean, create_function_from_string, create_constraint_from_string

warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="scipy.optimize._slsqp_py"
)
mp.dps = 50

MODE_IMPORT = 0
MODE_CUSTOM = 1
MODE_DEFAULT = 2


# generate random guesses using a grid pattern
def gen_guesses(bounds, samples: int = 5):
    return list(
        itertools.product(
            *[np.linspace(_min, _max, samples) for _min, _max in bounds]
        )
    )


# generates random guesses using the latin-hypercube sampling methodology
def lhs_guesses(bounds, samples: int = 10):
    dim = len(bounds)
    lhs = LatinHypercube(d=dim)
    sample = lhs.random(n=samples)
    scaled_samples = np.zeros_like(sample)
    for i, (low, high) in enumerate(bounds):
        scaled_samples[:, i] = low + sample[:, i] * (high - low)
    return scaled_samples


class SLSQP:
    @staticmethod
    def optimize(
        objective_function,
        bounds,
        constraints,
        all_functions,
        grid_size: int = 5,
        obj_gradient=None,
        con_gradients=[],
        tolerance: float=1e-20,
        verbose=False,
    ):
        if verbose:
            print(f"OPTIMIZING FOR FUNCTION:\n\t{ objective_function }")
        t = time()

        OBJ = create_function_from_string(
            clean(objective_function, len(bounds))
        )
        CONS = []

        if obj_gradient:
            obj_gradient = create_function_from_string(
                f"[ { ', '.join( [ clean( str( o ), len( bounds ) ) for o in obj_gradient ] ) } ]"
            )

        for i, (_type, _constraint) in enumerate(constraints):
            if len(con_gradients) > 0:
                con_gradients[i] = create_function_from_string(
                    f"[ { ', '.join( [ clean( str( c ), len( bounds ) ) for c in con_gradients[i] ] ) } ]"
                )

                CONS.append(
                    NonlinearConstraint(
                        create_constraint_from_string(
                            _constraint, all_functions, len(bounds)
                        ),
                        0 if _type == "eq" else -np.inf,
                        0,
                        jac=con_gradients[i],
                    )
                )
            else:
                CONS.append(
                    NonlinearConstraint(
                        create_constraint_from_string(
                            _constraint, all_functions, len(bounds)
                        ),
                        0 if _type == "eq" else -np.inf,
                        0,
                    )
                )

        best = None
        guesses = gen_guesses(bounds, samples=grid_size)
        for guess in guesses:
            try:
                if obj_gradient is not None:
                    result = minimize(
                        OBJ,
                        guess,
                        method="SLSQP",
                        bounds=bounds,
                        constraints=CONS,
                        jac=lambda x: obj_gradient(x),
                        tol=tolerance,
                        options={"disp": False, "maxiter": 1000, "ftol": tolerance},
                    )
                else:
                    result = minimize(
                        OBJ,
                        guess,
                        method="SLSQP",
                        bounds=bounds,
                        constraints=CONS,
                        tol=tolerance,
                        options={"disp": False, "maxiter": 1000, "ftol": tolerance},
                    )
            except Exception as e:
                print(f"Error: { e }")
            
            if result.success:
                if best is None:
                    best = result
                else:
                    if best.fun > result.fun:
                        best = result

        duration = time() - t
        if best is None:
            return 400, None

        if verbose:
            print(
                f"Time taken for { len( guesses ) } initial points:"
                f" { duration }s\n"
            )

        cons_values = []
        for _type, _constraint in constraints:
            c = create_constraint_from_string(_constraint, all_functions, len(bounds))
            cons_values.append(c(best.x))

        return 0, Optimization(
            "single",
            {
                "alg": 'single',
                "fun": best.fun,
                "sol": best.x,
                "con": cons_values,
                "con-names": constraints,
                "jac": best.jac,
            },
            duration,
        )
