from __future__ import annotations
from handlers.function import Function

import re as regex
import numpy as np

from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy import (
    sin, cos, tan, cot, sec, csc,
    asin, acos, atan,
    sinh, cosh, tanh, asinh, acosh, atanh,
    exp, log, ln,
    sqrt, Abs, pi,
    Sum, symbols, sympify, lambdify,
    diff, im, Derivative, re, sign, E, N
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
    'sign': sign, 'e': E,
}

def replace_isum(match: regex.Match):
    expr = match.group(1)  # mathmatical expression
    var  = match.group(2)  # index variable
    start = int(match.group(3))  # min
    end   = int(match.group(4))  # max

    result_terms = []
    for i in range(start, end + 1):
        # Replace all var[index_expr] with varN
        def replace_indexed(m):
            base = m.group(1)                   # e.g., 'x'
            index_expr = m.group(2)             # e.g., 'i+1'
            value = sympify(index_expr, locals={var: i})
            return f"{base}{int(value)}"

        # Replace all pattern like x[...] with xN
        transformed_expr = regex.sub(r'(\w+)\[(.*?)\]', replace_indexed, expr)
        result_terms.append(transformed_expr)

    return ' + '.join(result_terms)

def prepare_function(func_str: str):
    # Handle iSum
    pattern = r"(?i)iSum\s*\(\s*(.+?)\s*,\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*\)"

    return regex.sub(pattern, replace_isum, func_str, flags=regex.IGNORECASE)

def get_expr(func_str: str, vars: list, constants: dict = None):
    x_vars = symbols(' '.join(vars), real=True, seq=True)

    # Build a locals dictionary that includes all valid variable names
    local_dict = {f'{vars[i]}': x_vars[i] for i in range(len(vars))}

    if constants:
        local_dict.update(constants)
    
    # Add functions explicitly used in math
    local_dict.update(locals)

    try:
        expr = sympify(prepare_function(func_str).lower(), locals=local_dict)
        return expr
    except Exception as e:
        raise ValueError(f"Failed to parse function string: {e}.")

class Variable:
    def __init__(self, _symbol, _min: float, _max: float, _type: str = "NA", _increment: float=1e-6):
        self.symbol = _symbol
        self.min, self.max = float(_min), float(_max)
        self.type      = _type
        self.increment = float(_increment)
    
    def __repr__(self):
        return f"{self.symbol}: {self.min}, {self.max}"
        # return f"{self.symbol}: ({self.min}, {self.max}), {self.type}, {self.increment}"

class Constant:
    def __init__(self, _symbol: str, _value_expr):
        self.symbol = _symbol
        self.expr = None
        self.value = None

        # Allow implicit multiplication (e.g., 2pi)
        transformations = (standard_transformations + (implicit_multiplication_application,))

        try:
            # If _value_expr is a number already, just store it
            if isinstance(_value_expr, (int, float)):
                self.value = float(_value_expr)
                self.expr = self.value
            else:
                # Try sympify string expressions
                self.expr = parse_expr(_value_expr, transformations=transformations)
                self.value = float(N(self.expr))
        except Exception as e:
            print(e)
            raise ValueError(f"Failed to parse expression '{_value_expr}': {e}")

    def __repr__(self):
        return f"{self.symbol} = {self.expr} ≈ {self.value}"

class BasicFunction:
    def __init__(self, name: str, function: str):
        self.name = name
        self.text = function
        self.level = -1
    
    def __repr__(self):
        return f"{self.level} | {self.name} = {self.text}"

class Node:
    def __init__(self, value: str, parent: Node, functions: list[BasicFunction]):
        self.value: str = value
        self.parent: Node = parent
        self.children: list[Node] = []

        self.error = False

        self.level = 0
        curr: Node = self
        while (curr := curr.parent):
            self.level += 1
            if self.value == curr.value:
                self.error = True
                return

        this_func = None
        for f in functions:
            if f.name == self.value:
                this_func = f.text
        
        if this_func is None:
            self.error = True
            return
        
        children = []
        for f in functions:
            pattern = r'\b' + regex.escape(f.name) + r'\b'
            if regex.search(pattern, this_func, flags=regex.IGNORECASE):
                self.children.append(Node(f.name, self, functions))
        
        for c in children:
            self.children.append(Node(c, self, functions))
    
    def find_max(self):
        if len(self.children) == 0:
            return self.level

        return max(child_max.find_max() for child_max in self.children)

    def error_exists(self):
        if len(self.children) == 0:
            return self.error
        
        return True in [child.error_exists() for child in self.children]

    def __repr__(self):
        indent = '  ' * self.level
        result = f"{indent}{self.value}\n"
        for child in self.children:
            result += repr(child)
        return result

def get_fast_func(expr, variables):
    # Only keep variables that appear in the expression
    used_vars = [v for v in variables if v in expr.free_symbols]

    fast_func = lambdify(used_vars, expr, modules='numpy')

    def wrapper(vals: list[float]):
        # Filter the values down to only those used
        filtered_vals = [val for var, val in zip(variables, vals) if var in used_vars]
        return fast_func(*filtered_vals)

    return wrapper

class Function:
    registry = {}

    def __init__(self, name: str, function: str[Function], variables: list[str], constants: dict=None):
        if function.strip() == "": function = "0"

        self.name = name.lower()
        self.text = function.lower()
        self.constants = constants or {}

        locals.update({fname: f.expr for fname, f in Function.registry.items()})

        # Detect variable names using sympy
        self.expr = get_expr(function, [v.lower() for v in variables], constants=self.constants)
        self.variables = sorted(symbols(' '.join([v.lower() for v in variables]), real=True, seq=True), key=lambda s: str(s))

        # Create fast evaluation function
        self.fast_func = get_fast_func(self.expr, self.variables)
        
        # Gradients
        self.gradient_exprs = [diff(self.expr, v) for v in self.variables]
        self.gradient_funcs = [get_fast_func(grad, self.variables) for grad in self.gradient_exprs]

        if name != "":
            Function.registry[name] = self

    def eval(self, vals: list[float]) -> float:
        """
        Evaluate numerically using numpy-lambdified function.
        The list must contain all required variable names in alphabetical order (of variables).
        """
        if len(vals) != len(self.variables):
            raise ValueError(f"Not enough variables when evaluating function {self.name}. Have {len(vals)} expect {len(self.variables)}.")
        
        return self.fast_func(vals)
    
    def __call__(self, vals: list[float]) -> float:
        """
        Evaluate numerically using numpy-lambdified function.
        The list must contain all required variable names in alphabetical order (of variables).
        """
        return self.eval(vals=vals)
    
    def jacobian(self, vals: list[float]) -> np.ndarray:
        return np.array([f(vals) for f in self.gradient_funcs], dtype=float)

    def __repr__(self):
        return f"{self.name.upper()} = {self.text.upper()}"
