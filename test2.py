from testing.fnc_objects import Function
import timeit

if __name__ == "__main__":
    eq = "sum(x1 + x2, (i, 1, 2))"
    vs = ["X1", "X2"]

    f = Function("F1", eq, vs)
    vals = {'x1': 2.0, 'x2': 3.0}
    print(f)
    print(f.eval(vals))
    print(f.fast_eval(vals))

    slow = timeit.timeit(lambda: f.eval(vals), number=1000)
    fast = timeit.timeit(lambda: f.fast_eval(vals), number=1000)

    print(f"Sympy time: {slow:.5f}s")
    print(f"Numpy exec function time: {fast:.5f}s")