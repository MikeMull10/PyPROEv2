from handlers.function import find_highest_x, Function
from pprint import pprint as pp
import sympy as sp
import re


def create_expression(expr_str):
    expr_str = expr_str.lower()

    # Define mappings for math functions and constants
    function_map = {
        'exp': 'sp.exp',
        'sin': 'sp.sin',
        'cos': 'sp.cos',
        'tan': 'sp.tan',
        'log': 'sp.log',
        'abs': 'sp.Abs',
        'pi': 'sp.pi',
        'sqrt': 'sp.sqrt',
        'sign': 'sp.sign',
        're': 'sp.re',
        'im': 'sp.im',
        'Derivative': 'sp.Derivative'
    }
    
    # Replace each function name in the expression string with the corresponding SymPy function
    for func, sympy_func in function_map.items():
        expr_str = re.sub(r'\b' + func + r'\b', sympy_func, expr_str)
    
    # Replace '^' with '**' for exponentiation
    expr_str = expr_str.replace('^', '**')

    # Find all variable names in the string (assuming variables are alphanumeric and start with 'x')
    variables = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr_str)

    # Remove known function names and SymPy symbols from the list of variables
    known_symbols = set(function_map.keys()) | set(["sp", "pi", "Abs", "e", "inf", "nan"])
    variables = [var for var in variables if var not in known_symbols]

    # Create SymPy symbols for the variables dynamically
    symbols = {var: sp.symbols(var, real=True) for var in set(variables)}

    # Use eval to convert the string into a SymPy expression
    expr = eval(expr_str, {**symbols, "sp": sp})
    
    return expr, symbols


class GradientManager:
    def __init__(self, variables: "dict", functions: "dict"):
        self.variables = variables
        self.functions = functions

    def generate(self, force_simplify: bool = False, no_simplify: bool = False):
        """Generate gradients for the given variables and functions"""
        variables = {}

        vars = [v for v in self.variables]
        func = [f for f in self.functions]

        for v in vars:
            variables[v] = sp.symbols(v)

        grads = {}
        for _func in func:
            f_function = self.functions[_func].lower()
            f_function = f_function.replace("x", "X")
            f_function = f_function.replace("^", "**")

            variables[_func] = f_function

            for v in self.variables:
                g = sp.diff(variables[_func], variables[v])

                if (len(str(g)) <= 250 or force_simplify) and not no_simplify:
                    g = sp.simplify(sp.nsimplify(g))

                grads[f"G{ _func }_{ v }"] = g

        return grads

    @staticmethod
    def raw_generate(functions: dict, num_vars: int = -1):
        ret = {}

        if num_vars == -1:
            for f in functions:
                num_vars = max(num_vars, find_highest_x(functions[f]))

        for f in functions:
            func = functions[f]
            # Create the expression from the string
            expr, symbols = create_expression(func)

            # Compute the derivatives (gradients)
            gradients = {var: sp.diff(expr, sym) for var, sym in symbols.items()}

            for i in range(num_vars):
                if f"x{i + 1}" not in gradients.keys():
                    gradients[f"x{i + 1}"] = 0

            ret[f] = gradients
        
        # Sort the dictionary using custom sorting key
        sorted_keys = sorted(ret.keys(), key=lambda x: (int(re.search(r'(\d+)', x).group(1)), x))

        sort = {}
        for s in sorted_keys:
            sort[s] = ret[s]

        return sort
    
    @staticmethod
    def generate_gradient_functions(functions: dict, num_vars: int = -1):
        grads = GradientManager.raw_generate(functions, num_vars)

        gradient_functions = []
        for g in grads:
            try:
                sorted_keys = sorted(grads[g].keys(), key=lambda x: (int(re.search(r'(\d+)', x).group(1)), x))
            except:
                sorted_keys = grads[g].keys()

            for x in sorted_keys:
                gradient_functions.append(Function(f"G{g.upper()}_{str(x).upper()}", str(grads[g][x])))
        
        return gradient_functions
