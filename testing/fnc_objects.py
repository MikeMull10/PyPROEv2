from __future__ import annotations
from handlers.function import Function

import re
import numpy as np

from sympy import (
    sin, cos, tan, cot, sec, csc,
    asin, acos, atan,
    sinh, cosh, tanh, asinh, acosh, atanh,
    exp, log, ln,
    sqrt, Abs, pi,
    Sum, symbols, sympify, lambdify,
    diff, im, Derivative, re, sign, E,
    IndexedBase
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
    
def get_expr(func_str: str, vars: list, constants: dict = None):
    x_vars = symbols(' '.join(vars), real=True)

    # Build a locals dictionary that includes all valid variable names
    local_dict = {f'{vars[i]}': x_vars[i] for i in range(len(vars))}

    # Allow indexing (i.e. x[i])
    # local_dict.update({
    #     'x': IndexedBase('x'),
    #     'i': symbols('i', integer=True)
    # })

    if constants:
        local_dict.update(constants)
    
    # Add functions explicitly used in math
    local_dict.update(locals)

    try:
        expr = sympify(func_str.lower(), locals=local_dict)
        return expr
    except Exception as e:
        print(func_str)
        raise ValueError(f"Failed to parse function string: {e}")

class Variable:
    def __init__(self, _symbol, _min: float, _max: float, _type, _increment: float=1e-6):
        self.symbol = _symbol
        self.min, self.max = float(_min), float(_max)
        self.type      = _type
        self.increment = float(_increment)
    
    def __repr__(self):
        return f"{self.symbol}: ({self.min}, {self.max}), {self.type}, {self.increment}"

class Constant:
    def __init__(self, _symbol: str, _value: float):
        self.symbol = _symbol
        self.value  = float(_value)
    
    def __repr__(self):
        return f"{self.symbol}: {self.value}"

class BasicFunction:
    def __init__(self, name: str, function: str):
        self.name = name
        self.text = function
        self.level = -1
    
    def __repr__(self):
        return f"{self.level} | {self.name} = {self.text}"

#TODO: Handle F1 vs F11 etc
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

        for f in functions:
            if f.name == self.value:
                this_func = f.text
        
        children = []
        for f in functions:
            if f.name in this_func:
                children.append(f.name)
        
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

class Function:
    registry = {}

    def __init__(self, name: str, function: str, variables: list, constants: dict=None):
        self.name = name.lower()
        self.text = function.lower()
        self.constants = constants or {}

        locals.update({fname: f.expr for fname, f in Function.registry.items()})

        # Detect variable names using sympy
        self.expr = get_expr(function, [v.lower() for v in variables], constants=self.constants)
        self.variables = sorted(self.expr.free_symbols, key=lambda s: str(s))  # sorted list of symbols

        # Create fast evaluation function
        self.fast_func = lambdify(self.variables, self.expr, modules='numpy')

        Function.registry[name] = self

    def eval(self, value_dict: dict) -> float:
        """
        Evaluate numerically using numpy-lambdified function.
        The dict must contain all required variable names.
        """
        # Match ordering to self.variables
        args = [value_dict[str(var)] for var in self.variables]
        return self.fast_func(*args)
    
    def gradients(self):
        return [diff(self.expr, v) for v in self.variables]
    
    def __call__(self, value_dict: dict) -> float:
        return self.eval(value_dict=value_dict)

    def __repr__(self):
        return f"{self.name} = {self.text}"

