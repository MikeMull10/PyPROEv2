from sympy import (
    sin, cos, tan, cot, sec, csc,
    asin, acos, atan,
    sinh, cosh, tanh, asinh, acosh, atanh,
    exp, log, ln,
    sqrt, Abs, pi,
    Sum, symbols, sympify, diff, im, Derivative, re, sign
)

locals = {
    'sin': sin, 'cos': cos, 'tan': tan,
    'cot': cot, 'sec': sec, 'csc': csc,
    'asin': asin, 'acos': acos, 'atan': atan,
    'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
    'asinh': asinh, 'acosh': acosh, 'atanh': atanh,
    'exp': exp, 'log': log, 'ln': ln,
    'sqrt': sqrt, 'abs': Abs,
    'sum': Sum, 'pi': pi,
    'im': im, 'Derivative': Derivative, 're': re,
    'sign': sign,
}


def get_gradient_expressions(func_str: str, num_vars: int) -> list[str]:
    expr = get_expr(func_str, num_vars)
    if not expr: return None

    # Compute gradient
    gradient = [str(diff(expr, x)) for x in symbols(f'x1:{num_vars+1}', real=True)]
    return gradient

def get_expr(func_str: str, num_vars: int):
    # Define x1, x2, ..., xn
    x_vars = symbols(f'x1:{num_vars+1}', real=True)

    # Build a locals dictionary that includes all valid variable names
    local_dict = {f'x{i+1}': x_vars[i] for i in range(num_vars)}
    # Add functions explicitly used in math
    local_dict.update(locals)

    try:
        expr = sympify(func_str, locals=local_dict)
        return expr
    except Exception as e:
        raise ValueError(f"Failed to parse function string: {e}")

def get_eval(func_str: str, num_vars: int, values):
    x_vars = symbols(f'x1:{num_vars+1}')

    local_dict = {}
    for i in range(num_vars):
        local_dict[f'x{i+1}'] = x_vars[i]
        local_dict[f'X{i+1}'] = x_vars[i]
    local_dict.update(locals)

    expr = sympify(func_str, locals=local_dict)

    subs = {x_vars[i]: values[i] for i in range(num_vars)}
    val = expr.evalf(subs=subs)
    return val


if __name__ == "__main__":
    func = "(5000*0.6^3)/(3*210*10^9*((PI*(X1^4-(X1-2*X2)^4))/64))".replace("^", "**").lower()
    fun2 = "(7800*0.6*((PI*(X1^2-(X1-2*X2)^2))/4))-4.7".replace("^", "**").lower()
    fun3 = "5000*0.6*X1-250*10^6*2*((PI*(X1^4-(X1-2*X2)^4))/64)".replace("^", "**").lower()
    func = "abs(x1) + x2 ** 2"
    grads = get_gradient_expressions(func, 2)
    print(grads)

    # for i, g in enumerate([func, fun2, fun3], 1):
    #     print(f"d/dx{i} =", get_gradient_expressions(g, 2))

    func = "sum(x1, (i, 1, 5)) ** 2"

    # print(get_eval(func, 1, [1]))
