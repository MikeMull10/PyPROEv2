import re
from pprint import pprint as pp

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import NonlinearConstraint, minimize

from handlers.gradmanager import GradientManager
from handlers.function import Function

data = []

OBJECTIVE = 0
EQUALITY_CONSTRAINT = 1
INEQUALITY_CONSTRAINT = 2


# create a callable object that essentially returns the value of the equation it is given
def create_function_from_string(equation_str: str) -> callable:
    # Define the function name
    function_name = "generated_function"

    # Define the function string, including the import statement for NumPy
    function_str = f"""
import numpy as np

def {function_name}(x):
    try:
        return {equation_str}
    except ZeroDivisionError:
        x = np.asarray(x)  # Ensure x is a NumPy array
        x = np.where(x == 0.0, 1e-15, x)  # Replace 0 values with 1e-15
        return {equation_str}  # Recalculate with modified x
"""

    # Create a local namespace to execute the function string
    local_namespace = {}
    exec(function_str, globals(), local_namespace)

    # Return the created function from the local namespace
    return local_namespace[function_name]


def create_constraint_from_string(constraint: str, all_functions: dict, size: int):
    for k, v in [[f, all_functions[f]] for f in all_functions][::-1]: # do it in reverse so that F1 does not replace F11 (or similar cases) and cause errors
        constraint = constraint.replace(k, v)
    
    constraint = clean(constraint, size)

    return create_function_from_string(constraint)


def add_spaces_to_expression(expression):
    expression = expression.upper()
    spaced_expression = ""
    operators = set("+-*/^()")

    for char in expression:
        if char in operators:
            spaced_expression += f" {char} "
        else:
            spaced_expression += char

    # Replace multiple spaces with a single space
    spaced_expression = " ".join(spaced_expression.split())

    rep = "abs pow log ln sin cos tan asin acos atan sinh cosh tanh sqrt ceil floor exp sign".upper().split(
        " "
    )

    for r in rep:
        spaced_expression = spaced_expression.replace(f"{ r } ", f"{ r }")

    spaced_expression = spaced_expression.replace("* *", "^")
    spaced_expression = spaced_expression.replace("- -", "+")
    spaced_expression = spaced_expression.replace("E - ", "E-")

    if spaced_expression[ 0:2 ] == "- ":
        spaced_expression = "-" + spaced_expression[ 2: ]

    return spaced_expression


# santize the function that should be passed to create_function_from_string
#   this replaces all special functions like pi or sin with the numpy versions to increase speed
def clean(function: str, num_vars: int):
    if not isinstance(function, str):
        function = str(function)

    function = function.lower()

    function = function.replace("^", "**")
    function = function.replace("\n", "")

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


def san(func: str):
    """Replace "x" with "X" and "^" with "**" for internal function evaluation"""
    func = func.lower().replace("x", "X").replace("^", "**")
    rep = (
        "pi abs pow log ln sin cos tan asin acos atan sinh cosh tanh sqrt ceil"
        " floor exp".split(" ")
    )

    for r in rep:
        func = func.replace(r, f"np.{r}")

    return func


def sanitize(func: str):
    """Replace "x" with "X" and "^" with "**" for internal function evaluation"""
    return func.lower().replace("x", "X").replace("^", "**")


def find(_data: list[str], _str: str):
    """Finds the lines associated with a given string.

    Parameters
    ----------
    _data : list[str]
        The lines from an input file
    _str : string
        The key to look for in the lines
    """
    for i, d in enumerate(_data):
        if _str in d:
            if "INEQUALITY-CONSTRAINT" in d and _str != "INEQUALITY-CONSTRAINT":
                continue
            return i
    return -1


def inc(val: float):
    """Returns the rounded-down log10 of the provided value

    Parameters
    ----------
    val: float
        The value to be evaluated
    """
    return np.floor(np.log10(val))


def check_valid_function(function: str):
    function = function.replace("x", "")
    try:
        sp.simplify(function)
    except Exception as e:
        return 3
    return 0


def group_by_sections(first_array, second_array):
    groups = {}
    
    for i in range(len(first_array)):
        section_name = first_array[i][0]
        start_index = first_array[i][1]
        
        # Determine the end index for slicing
        if i + 1 < len(first_array):
            end_index = first_array[i + 1][1]
        else:
            end_index = len(second_array)
        
        # Slice the second array and assign to the group
        groups[section_name] = second_array[start_index:end_index]
    
    return groups


class InputFile:
    def __init__(self, input_str: str, is_file: bool = True, handle_error=None):
        """Reads in either a file or data for an optimization problem.

        Parameters
        ----------
        input_str : str
            Either the path to a file, or the data containing the problem that needs to be optimized.
        is_file : bool
            Indicator whether the input_str is a file path (True) or the data itself (False). By default, it thinks the input_str is a file path.
        """
        self.status = 0  # for error handling - 0 means good to go

        if is_file:
            if input_str == "None" or input_str is None:
                self.status = 1
                return
            self.file_name = input_str
            self.raw_data = self.get_raw_data(input_str)
        else:
            self.file_name = ""
            self.raw_data = []
            data = input_str.split("\n")
            for d in data:
                if d == "" or d[0] == "#":
                    continue
                self.raw_data.append(d)

        self.data = {}
        self.handle_error = handle_error

        self.sort_data()

        if self.status != 0:
            self.variables = {}
            self.objectives = {}
            self.equality_constraints = {}
            self.inequality_constraints = {}
            self.functions = {}
            self.gradients = {}
            return

        self.variables = self.data["VARIABLE"]
        self.objectives = self.data["OBJECTIVE"]
        self.equality_constraints = self.data["EQUALITY-CONSTRAINT"]
        self.inequality_constraints = self.data["INEQUALITY-CONSTRAINT"]
        self.functions = self.data["FUNCTION"]

        if len(self.data["GRADIENT"]) == 0:
            self.data["GRADIENT"] = self.calculate_gradients()

        self.gradients = self.data["GRADIENT"]
        self.objective_function_min_max = []
        self.normalized = False

        for t in [self.variables, self.objectives, self.functions]:
            if len(t.keys()) == 0:
                self.status = 3
                break

        self.objective_function = self.get_objective()

    @staticmethod
    def get_raw_data(file_name: str):
        """Read in the raw data from the file

        Parameters
        ----------
        file_name : str
            The name of the file to be read
        """
        data = []
        with open(file_name) as file:
            for line in file:
                line = line.strip()

                if line == "":
                    continue
                elif line[0] == "#":
                    continue

                data.append(line)

            file.close()

        return data

    def sort_data(self):
        """
        Takes the data read in and sorts it into usable data by doing the following:

        For each type of input needed [ VARIABLE, OBJECTIVE, EQUALITY-CONSTRAINT, INEQUALITY-CONSTRAINT, FUNCTION, GRADIENT ],
            find the line with the type of input in the string,
            if applicable, get the number of lines of that type to be read in,
            loop that many times to parse all of the necessary data

        For GRADIENT,
            if no gradient is provided, one will be calculated using the finite difference method from scipy
        """
        data = self.raw_data

        ### Get the TITLES
        _variable = find(data, "VARIABLE")
        _objective = find(data, "OBJECTIVE")
        _equality = find(data, "EQUALITY-CONSTRAINT")
        _inequality = find(data, "INEQUALITY-CONSTRAINT")
        _function = find(data, "FUNCTION")
        _gradient = find(data, "GRADIENT")

        titles = [
            ["VARIABLE", _variable],
            ["OBJECTIVE", _objective],
            ["EQUALITY-CONSTRAINT", _equality],
            ["INEQUALITY-CONSTRAINT", _inequality],
            ["FUNCTION", _function],
            ["GRADIENT", _gradient],
        ]

        for t in titles:
            self.data[t[0]] = {}
        
        titles = sorted(titles, key=lambda x: x[1])

        sections = group_by_sections(titles, data)
        for t in titles:
            t[1] = sections[t[0]][1:]

        for name, lines in titles:
            if len(lines) == 0:
                continue
            
            match name:
                case "VARIABLE":
                    for line in lines:
                        v, info = line.split(':')
                        info = [x.replace(";", "").strip() for x in info.split(",")]

                        if len(info) < 3: info += ['REAL']
                        if len(info) < 4: info += [1e-6]

                        info[0], info[1], info[3] = (
                            float(info[0]),
                            float(info[1]),
                            float(info[3]),
                        )

                        self.data["VARIABLE"][v.upper()] = info[0:2]
                
                case "OBJECTIVE":
                    for line in lines:
                        v, e = line.replace(";", "").split("=")

                        self.data["OBJECTIVE"][v.strip().upper()] = e.strip().upper()
                
                case "EQUALITY-CONSTRAINT":
                    for line in lines:
                        v, e = line.replace(";", "").split("=")

                        self.data["EQUALITY-CONSTRAINT"][v.strip().upper()] = e.strip().upper()

                case "INEQUALITY-CONSTRAINT":
                    for line in lines:
                        v, e = line.replace(";", "").split("=")

                        self.data["INEQUALITY-CONSTRAINT"][v.strip().upper()] = e.strip().upper()
                
                case "FUNCTION":
                    _func = ""
                    for line in lines:
                        _func += line
                        if ';' in line:
                            n, f = _func.replace(';', '').split('=')
                            self.data["FUNCTION"][n.strip().upper()] = f.strip().upper()
                            _func = ""
                
                case "GRADIENT":
                    _grad = ""
                    for line in lines:
                        _grad += line
                        if ';' in line:
                            n, f = _grad.replace(';', '').split('=')
                            self.data["GRADIENT"][n.strip().upper().replace('-', '_')] = f.strip()
                            _grad = ""

        if "GRADIENT" not in self.data.keys(): return
        
        # if self.data["GRADIENT"] == {}:
        #     self.data["GRADIENT"] = GradientManager.generate_gradient_functions(self.data["FUNCTION"], len(self.data["VARIABLE"]))

    def get_objective(self, obj: int = OBJECTIVE) -> list[str]:
        """Get the type of objective provided from the file data

        Parameters
        ----------
        obj : int
            The kind of objective to find in the data
        """
        info = (
            "OBJECTIVE"
            if obj == OBJECTIVE
            else (
                "EQUALITY-CONSTRAINT"
                if obj == EQUALITY_CONSTRAINT
                else "INEQUALITY-CONSTRAINT"
            )
        )

        func = self.data[info][list(self.data[info].keys())[0]]

        if func in self.functions.keys():
            return self.functions[func]

    def get_objective_functions(self) -> list[str]:
        """Returns the objective functions for the file"""
        funcs = list(self.objectives.values())
        return [self.functions[f] for f in funcs]

    def get_functions(self) -> list[str]:
        """Returns the functions for the file"""
        return list(self.functions.values())

    def get_bounds(self) -> list[list[float | int]]:
        """Returns the boundds for the input file"""
        ret = []
        for var in self.variables:
            v = self.variables[var]
            ret.append([v[0], v[1]])

        return ret

    def has_constraints(self) -> bool:
        """Returns whether or not the file has contraints"""
        return (
            len(self.equality_constraints.keys())
            + len(self.inequality_constraints.keys())
        ) > 0

    def get_constraint_functions(self) -> list[list[str | list[str]]]:
        """Returns all inequality and equality constraints for the file"""
        ret = []

        for eq in self.equality_constraints.values():
            ret.append(["eq", eq])
        for ineq in self.inequality_constraints.values():
            ret.append(["ineq", ineq])

        return ret

    def get_constraint_function_names(self) -> list[str]:
        """Returns all inequality and equality function names from the file"""
        ret = []

        for eq in self.equality_constraints.keys():
            ret.append(self.equality_constraints[eq])
        for ineq in self.inequality_constraints.keys():
            ret.append(self.inequality_constraints[ineq])

        return ret

    def constraint_type(self, constraint: str) -> str | None:
        """For a given constraint name, returns "eq" or "ineq" (or None) depending on that constraint's type

        Parameters
        ----------
        constraint : str
            The name of the constraint to find the type for
        """
        for eq in self.equality_constraints.keys():
            if self.equality_constraints[eq] == constraint:
                return "eq"
        for ineq in self.inequality_constraints.keys():
            if self.inequality_constraints[ineq] == constraint:
                return "ineq"
        return None

    def get_objective_gradients(self) -> list[str]:
        """Returns the objective gradients for the file"""
        objective_functions = [self.objectives[ob] for ob in self.objectives]

        g = []
        for grad in self.gradients:
            if (
                grad[1:].split("_")[0] in objective_functions
            ):  # checks if the function is an objective function by looking between the G and _X# ex. GF1_X1 -> F1
                g.append([grad, self.gradients[grad]])

        ret = {}
        for _name, _function in g:
            function_name = _name[1:].split("_")[0]
            if function_name not in list(ret.keys()):
                ret[function_name] = [_function]
            else:
                ret[function_name].append(_function)

        return [v for v in ret.values()]

    def get_constraint_gradients(self) -> list[str]:
        """Returns the constraint gradients for the file"""
        constraint_functions = [
            self.equality_constraints[con] for con in self.equality_constraints
        ]
        constraint_functions += [
            self.inequality_constraints[con]
            for con in self.inequality_constraints
        ]
        
        for i in range(len(constraint_functions)):
            constraint_functions[i] = re.match(r"F\d+", constraint_functions[i]).group()

        c = []
        for grad in self.gradients:
            if (
                grad[1:].split("_")[0] in constraint_functions
            ):  # checks if the function is an objective function by looking between the G and _X# ex. GF1_X1 -> F1
                c.append([grad, self.gradients[grad]])

        ret = {}
        for _name, _function in c:
            function_name = _name[1:].split("_")[0]
            if function_name not in list(ret.keys()):
                ret[function_name] = [_function]
            else:
                ret[function_name].append(_function)

        return [v for v in ret.values()]

    def get_contour_plot(self, contour_levels=[0], bounds=[[0, 0], [0, 0]]):
        """Creates a matlab plot based on the inputfile

        Parameters
        ----------
        contour_levels : list
            A list defining the specific contour levels you want to plot.
        bounds : list = [ [ min_x, max_x ], [ min_y, max_y ] ]
            The bounds desired for the graph.
        """
        title = (
            self.file_name
            if "/" not in self.file_name
            else self.file_name.split("/")[-1]
        )
        if ".fnc" in title:
            title = title.split(".fnc")[0]

        defined_bounds = bounds != [
            [0, 0],
            [0, 0],
        ]  # Check if the bounds were manually defined
        aranges = []
        for i, v in enumerate(self.variables.values()):
            _inc = 10 ** (inc(v[0]) - 1)
            _min = bounds[i][0] if defined_bounds else v[0] - 10 ** inc(v[0])
            _max = bounds[i][1] if defined_bounds else v[1] + 10 ** inc(v[0])
            if _inc == 0.0: return None
            aranges.append(np.arange(_min, _max, _inc))

        vars = []
        variables = {}
        for i, var in enumerate(self.variables):
            vars.append(var)
            variables[var] = np.meshgrid(*aranges)[i]

        obj = self.get_objective()

        constraint_functions = []
        ### Find Equality Constraints
        for eq in self.equality_constraints.values():
            _func: str = eq  # get the equality function
            for f in self.functions:
                _func = _func.replace(f, self.functions[f])
            constraint_functions.append(_func)
        for ineq in self.inequality_constraints.values():
            _func: str = ineq  # get the inequality function
            for f in self.functions:
                _func = _func.replace(f, self.functions[f])
            constraint_functions.append(_func)

        # Define functions
        functions = {}

        f = sanitize(obj)
        for v in variables:
            f = f.replace(v, f"variables[ '{ v }' ]")
        functions["f"] = f

        i = 0
        for con in constraint_functions:
            con = sanitize(con)
            for v in variables:
                con = con.replace(v, f"variables[ '{ v }' ]")
            functions[f"g{ i }"] = con
            i += 1

        for var in self.variables:
            functions[f"g{ i }"] = (
                f"-variables[ '{ var }' ] + { self.variables[ var ][ 0 ] }"
            )
            functions[f"g{ i + 1 }"] = (
                f"variables[ '{ var }' ] - { self.variables[ var ][ 1 ] }"
            )
            i += 2

        fig = Figure()
        ax = fig.add_subplot(111)

        # Labels and title
        ax.set_xlabel(vars[0])
        ax.set_ylabel(vars[1])
        ax.set_title(f"Contour Plot for {title}")

        # Contour plots
        pi = np.pi
        f_contour = ax.contour(
            *[variables[v] for v in vars], eval(functions["f"].replace("sqrt", "np.sqrt")), 30
        )
        ax.clabel(f_contour)

        # Constraints contours
        for key, expr in functions.items():
            if key != "f":  # Exclude 'f' from constraints
                ax.contour(
                    *[variables[v] for v in vars],
                    eval(expr.replace("sqrt", "np.sqrt")),
                    contour_levels,
                    colors="k",
                )

        return fig

    def get_surface_plot(self, function_to_graph: str = "F1"):
        if len(self.variables) != 2:
            return None

        v = self.variables
        x1 = np.arange(
            v["X1"][0], v["X1"][1] + v["X1"][0] / 10, v["X1"][0] / 10
        )
        x2 = np.arange(
            v["X2"][0], v["X2"][1] + v["X2"][0] / 10, v["X2"][0] / 10
        )

        x = np.meshgrid(x1, x2)

        func_str = clean(self.functions[function_to_graph], 2)

        func = eval(func_str)

        # Create a 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Plot the surface
        ax.plot_surface(*x, func, cmap="viridis")

        # Set labels
        ax.set_xlabel("X1")
        ax.set_ylabel("X2")
        ax.set_zlabel(function_to_graph)

        # return the plot
        return fig

    def calculate_gradients(self):
        ret = {}
        grads = GradientManager.generate_gradient_functions(self.functions, len(self.variables))

        for g in grads: ret[g.name] = g.text
        
        return ret

    def normalize(self):
        if self.normalized:
            return

        bounds = [[v[0], v[1]] for v in self.variables.values()]

        minmaxs = []
        funcs = list(self.objectives.values())
        for function in [self.functions[f] for f in funcs]:
            _function = create_function_from_string(
                clean(function, len(self.variables))
            )

            _min1 = minimize(
                _function,
                x0=[b[0] for b in bounds],
                bounds=bounds,
                method="SLSQP",
            ).fun
            _min2 = minimize(
                _function,
                x0=[b[1] for b in bounds],
                bounds=bounds,
                method="SLSQP",
            ).fun

            _max1 = -minimize(
                lambda x: -_function(x),
                x0=[b[0] for b in bounds],
                bounds=bounds,
                method="SLSQP",
            ).fun
            _max2 = -minimize(
                lambda x: -_function(x),
                x0=[b[1] for b in bounds],
                bounds=bounds,
                method="SLSQP",
            ).fun

            _min = min(_min1, _min2)
            _max = max(_max1, _max2)

            if np.inf in [_min, _max]: return

            minmaxs.append([_min, _max])

        for f, (_min, _max) in zip(funcs, minmaxs):
            old = self.functions[f]
            new = (
                f"( ( { old } ) - { _min } ) / ( { _max - _min } )"
                if _min != 0.0
                else f"( { old } ) / ( { _max - _min } )"
            )
            self.data["FUNCTION"][f] = new
            self.functions[f] = new

        self.objective_function_min_max = minmaxs

        gradients = self.calculate_gradients()

        for g in gradients:
            gradients[g] = add_spaces_to_expression(str(gradients[g]))

        self.data["GRADIENT"] = gradients
        self.gradients = gradients

        self.normalized = True

    def unnormalize_points(self, points):
        new_points = []
        for p in points:
            new_point = []

            for v, (_min, _max) in zip(p, self.objective_function_min_max):
                new_point.append((v * (_max - _min)) + _min)

            new_points.append(new_point)

        return new_points

    def generate_fnc_file(self):
        ret = ""

        ret += f"*VARIABLE: { len( self.variables ) }\n"
        for v in self.variables:
            ret += (
                f"{ v }: "
                + ", ".join([str(_) for _ in self.variables[v]])
                + "\n"
            )
        ret += f"\n"

        ret += f"*OBJECTIVE: { len( self.objectives ) }\n"
        for o in self.objectives:
            ret += f"{ o } = { self.objectives[ o ] };\n"
        ret += f"\n"

        ret += f"*EQUALITY-CONSTRAINT: { len( self.equality_constraints ) }\n"
        for eq in self.equality_constraints:
            ret += f"{ eq } = { self.equality_constraints[ eq ] };\n"
        ret += f"\n"

        ret += (
            f"*INEQUALITY-CONSTRAINT: { len( self.inequality_constraints ) }\n"
        )
        for ineq in self.inequality_constraints:
            ret += f"{ ineq } = { self.inequality_constraints[ ineq ] };\n"
        ret += f"\n"

        ret += f"*FUNCTION: { len( self.functions ) }\n"
        for f in self.functions:
            ret += f"{ f } = { self.functions[ f ] };\n"
        ret += f"\n"

        ret += f"*GRADIENT\n"
        i = 0
        for g in self.gradients:
            ret += f"{ g } = { self.gradients[ g ] };\n"
            i += 1

            if i % (len(self.variables)) == 0:
                ret += "\n"

        return ret[:-2]

    def __str__(self):
        """Summarize the function file by parameters found"""

        ret = ""
        for _type in [
            "VARIABLE",
            "OBJECTIVE",
            "EQUALITY-CONSTRAINT",
            "INEQUALITY-CONSTRAINT",
            "FUNCTION",
            "GRADIENT",
        ]:
            ret += f"{ _type }S: { len( self.data[ _type ] ) }\n"
            for var in self.data[_type]:
                ret += f"\t{ var } = { self.data[ _type ][ var ] }\n"

        return ret[:-1]
