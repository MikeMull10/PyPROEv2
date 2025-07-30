from time import perf_counter
from testing.fnc_objects import Function
from handlers.inputfnc import clean, create_function_from_string
from scipy.optimize import minimize

import numpy as np

def make_minimizer_function(expr_str: str, var_names: list[str]) -> callable:
    from sympy import symbols, sympify
    from sympy.utilities.lambdify import lambdify

    symbols_list = symbols(var_names)
    expr = sympify(expr_str)
    func = lambdify(symbols_list, expr, modules='numpy')

    def wrapper(x_array):
        return func(*x_array)

    return wrapper

if __name__ == "__main__":
    func_str = "sin(x1) + cos(x2)"

    # N = 1_000_000
    # new = Function("F1", func_str, ["X1", "X2"])

    # start = perf_counter()
    # a = [0.02, 0.002]
    # for i in range(N):
    #     new(a)
    # print(f"New x{N}: {perf_counter() - start}")

    # start = perf_counter()
    # a = np.array([0.02, 0.002])
    # for i in range(N):
    #     new(a)
    # print(f"Np x{N}: {perf_counter() - start}")

    # exit()

    func_str = "x**2 + y**2"
    f = Function("F1", func_str, ['x', 'y'])

    res = minimize(f, x0=[200.0, 1.0], jac=f.jacobian, method="SLSQP")
    print(f"Min: {res.x}")
