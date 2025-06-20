import numpy as np

import re

def find_highest_x(expression, prefix='x'):
    expression = expression.lower()
    # Regex to match variables like x<number>
    matches = re.findall(rf'{prefix}(\d+)', expression)
    # Convert matches to integers and find the maximum
    if matches:
        highest = max(int(num) for num in matches)
        return highest
    return 0

def create_function_from_string(equation_str: str) -> callable:
    # Define the function name
    function_name = "generated_function"

    # Define the function string, including the import statement for NumPy
    function_str = f"""
import numpy as np
def {function_name}(x):
    return {str(equation_str)}
"""

    # Create a local namespace to execute the function string
    local_namespace = {}
    exec(function_str, globals(), local_namespace)

    # Return the created function from the local namespace
    return local_namespace[function_name]

# santize the function that should be passed to create_function_from_string
#   this replaces all special functions like pi or sin with the numpy versions to increase speed
def clean(function: str) -> str:
    function = str(function).lower()
    num_vars = find_highest_x(function)

    function = function.replace("^", "**")
    function = function.strip()

    ### Use numpy for special functions
    rep = (
        "pi abs pow log ln sin cos tan asin acos atan sinh cosh tanh sqrt ceil"
        " floor exp sign".split(" ")
    )
    for r in rep:
        function = function.replace(r, f"np.{ r }")

    for var in range(1, num_vars + 1)[::-1]:  # do this in reverse so that x1 does not replace x11 (or similar cases) and break
        function = function.replace(f"x{ var }", f"x[{ var - 1 }]")

    return function

class Function:
    def __init__(self, name: str, function: str, defined_function: callable = None):
        self.name: str = name  # i.e. F1
        self.text: str = function
        self.func_def: callable = defined_function if defined_function else self.__create_callable(function)

        self.highest_x = find_highest_x(function)

    def __create_callable(self, function: str):
        return create_function_from_string(clean(function))

    def __str__(self):
        return self.text