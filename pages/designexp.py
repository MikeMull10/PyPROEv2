import math
import random
import re
from decimal import Decimal

from algorithms.slsqp import clean, create_function_from_string
from handlers.filereader import TextFileReader
from handlers.matrix import Matrix
from handlers.errorhandler import ErrorHandler
from pages.mainwindow import Ui_MainWindow

def normalize_to_real_value(normalized_value, min_bound, max_bound):
    return min_bound + ((normalized_value + 1) / 2) * (max_bound - min_bound)


class DOE:
    """A class managing the design of experiments page"""

    def __init__(self, ui: Ui_MainWindow, handle_error: ErrorHandler):
        """Initialize with an instance of the ui"""
        self.DOE_OK = 1
        self.DOE_ERROR = -1
        self.DOE_USER_DEFINED = -1
        self.DOE_FACTORIAL = 0
        self.DOE_CC_SPHERICAL = 1
        self.DOE_CC_FACE_CENTERED = 2
        self.DOE_TAGUCHI = 3
        self.DOE_LATIN_HYPERCUBE = 4
        self.LEVELS2 = [-1.0, 1.0]
        self.LEVELS3 = [-1.0, 0.0, 1.0]
        self.LEVELS4 = [-1.0, -0.33333333, 0.33333333, 1.0]
        self.LEVELS5 = [-1.0, -0.5, 0.0, 0.5, 1.0]
        self.LEVELS6 = [-1.0, -0.6, -0.2, 0.0, 0.2, 0.6, 1.0]
        self.LEVELS7 = [
            -1.0,
            -0.66666667,
            -0.33333333,
            0.0,
            0.33333333,
            0.66666667,
            1.0,
        ]
        self.LEVELS8 = [
            -1.0,
            -0.71428571,
            -0.42857143,
            -0.14285714,
            0.14285714,
            0.42857143,
            0.71428571,
            1.0,
        ]
        self.LEVELS7 = [
            -1.0,
            -0.66666667,
            -0.33333333,
            0.0,
            0.33333333,
            0.66666667,
            1.0,
        ]
        self.LEVELS8 = [
            -1.0,
            -0.71428571,
            -0.42857143,
            -0.14285714,
            0.14285714,
            0.42857143,
            0.71428571,
            1.0,
        ]
        self.LEVELS9 = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]

        self.doe_type = -1
        self.num_vars = 1
        self.num_levels = 2
        self.num_points = 2
        self.orig_points = 2
        self.num_funcs = 1
        self.design_levels: list[float] = []
        self.has_data = False
        self.matrix_vars: list[list[float]] = [[]]
        self.matrix_funcs: list[list[float]] = [[]]
        self.func_defs: list[str] = []
        self.var_bounds: list[list[float]] = [[]]
        self.ui = ui
        self.handle_error: ErrorHandler = handle_error

    def doe_file_reader(self, filename: str, is_str: bool=False) -> int:
        """Initialize the page with information from the given file"""
        var2 = None
        var3 = None

        if not is_str:
            var4 = TextFileReader(filename, "#$*/|", self.handle_error)
            var4.set_skip_blank_line(True)
            var4.set_skip_comment_line(True)
            if not var4.is_file_open:
                return -1
        if not is_str:
            var4 = TextFileReader(filename, "#$*/|", self.handle_error)
            var4.set_skip_blank_line(True)
            var4.set_skip_comment_line(True)
            if not var4.is_file_open:
                return -1

            var2 = var4.read_line()
        else:
            var2 = filename

        if var2 == None:
            return self.wrong_format_ret(filename, var4)
        else:
            try:
                var3 = [i for i in re.split(" |,|\t|\n|\r", var2) if i != ""]
                self.num_points = self.orig_points = int(var3.pop(0))
                self.num_vars = int(var3.pop(0))
                self.num_levels = int(var3.pop(0))
                self.num_funcs = int(var3.pop(0))

                self.matrix_vars = [
                    [None for j in range(self.num_vars)]
                    for i in range(self.num_points)
                ]
                self.matrix_funcs = [
                    [None for j in range(self.num_funcs)]
                    for i in range(self.num_points)
                ]

                self.var_bounds = [[0,0 ] for _ in range(self.num_vars)]
                self.func_defs = ["0" for _ in range(self.num_funcs)]

                # read in the point data
                for var5 in range(self.num_points):
                    var2 = var4.read_line()
                    if var2 == None or var2 == "":
                        return self.wrong_format_ret(filename, var4)

                    var3 = [
                        i for i in re.split(" |,|\t|\n|\r", var2) if i != ""
                    ]
                    var3.pop(0)

                    for var6 in range(self.num_vars):
                        self.matrix_vars[var5][var6] = float(var3.pop(0))
                    # if the file was saved with the relative variable values, load them    
                    if len(var3) == (self.num_vars) + self.num_funcs:
                        var3 = var3[self.num_vars :]

                    for var6 in range(self.num_funcs):
                        self.matrix_funcs[var5][var6] = float(var3.pop(0))

                # read in the variable boundaries
                for var in range(self.num_vars):
                    line = var4.read_line()
                    if line != None and line != "":
                        # remove the title from the row
                        line_items = [
                            i for i in re.split(" |,|\t|\n|\r", line) if i != ""
                        ]
                        line_items.pop(0)

                        self.var_bounds[var] = [
                            float(line_items[0]),
                            float(line_items[1]),
                        ]

                # read in the function definitions
                for func in range(self.num_funcs):
                    line = var4.read_line()
                    if line != None and line != "":
                        # remove the title from the row
                        line_items = [
                            i for i in re.split("=|;", line) if i != ""
                        ]
                        line_items.pop(0)

                        self.func_defs[func] = line_items[0]

                self.doe_type = -1

                self.ui.designVarNum.setValue(self.num_vars)
                self.ui.levelCombo.setValue(self.num_levels)
                self.ui.designPointNum.setValue(self.num_points)
                self.ui.functionNum.setValue(self.num_funcs)

                var4.close()
                self.has_data = True
                return 1
            except Exception as e:
                return self.wrong_format_ret(filename, var4)

    def wrong_format_ret(self, filename: str, reader: TextFileReader) -> int:
        """Return an error on invalid file formatting"""
        self.handle_error.gen_error(
            f"Invalid format <{filename}>.\nLine #:"
            f" {reader.get_current_line_number()}"
        )
        reader.close()
        return -1

    def handle_add_point(self):
        """Add a point to the DOE table"""
        self.num_points += 1
        self.matrix_vars.append([0.0 for _ in self.matrix_vars[0]])

        new_func_row = [0.0 for _ in range(len(self.matrix_funcs[0]))] if self.matrix_funcs else []
        self.matrix_funcs.append(new_func_row)

    def handle_remove_point(self):
        """Remove the selected rows from the DOE table"""

        # reverse the order so the right rows get removed
        row_indices = [
            i.row()
            for i in self.ui.doeTable.selectionModel().selectedRows()
            if i.row() >= self.orig_points
        ][::-1]

        for index in row_indices:
            self.matrix_vars.pop(index)
            [func.pop(index) for func in self.matrix_funcs if func != []]

        self.num_points -= len(row_indices)

    def fifteenth_place_truncation(self, val: float) -> str:
        """Truncate the value to the 15th place, as that is the maximum .doe file precision"""
        # print(float(Decimal("%.15f" % val)))
        return float(Decimal("%.15f" % val))

    def display_des_matrix(self) -> str:
        """Returns a string representing the design matrix"""
        base = self.get_des_matrix_summary_str()

        # get all the auto-generated points
        for var2 in range(self.orig_points):
            var3 = f"{var2 + 1}\t"

            for var4 in range(self.num_vars):
                var3 = f"{var3}{self.fifteenth_place_truncation(self.matrix_vars[var2][var4])}\t"

            for var4 in range(self.num_vars):
                bounds = [
                    Decimal(self.var_bounds[var4][0]),
                    Decimal(self.var_bounds[var4][1]),
                ]

                half = Decimal("0.5")

                firsthalf = (half*(bounds[0] + bounds[1]) + (Decimal(self.matrix_vars[var2][var4])*half*(bounds[1] - bounds[0]))) if self.var_bounds[var4] != [0,0] else 1

                var3 = (
                    f"{var3}{self.fifteenth_place_truncation(firsthalf)}\t"
                    # f"{var3}{self.fifteenth_place_truncation(bounds[0] +((bounds[1] - bounds[0]) * Decimal(self.matrix_vars[var2][var4])))}\t"
                )
            for var4 in range(self.num_funcs):
                var3 = f"{var3}\t{self.fifteenth_place_truncation(self.matrix_funcs[var2][var4])}"

            base = f"{base}\n{var3}"

        # get any user-generated points
        for var2 in range(self.orig_points, self.num_points):
            var3 = f"{var2 + 1}\t"

            for var4 in range(self.num_vars):
                var3 = f"{var3}{self.fifteenth_place_truncation(self.matrix_vars[var2][var4])}\t"

            for var4 in range(self.num_vars):
                bounds = [
                    Decimal(self.var_bounds[var4][0]),
                    Decimal(self.var_bounds[var4][1]),
                ]

                half = Decimal("0.5")


                firsthalf = (half*(bounds[0] + bounds[1]) + (Decimal(self.matrix_vars[var2][var4])*half*(bounds[1] - bounds[0]))) if self.var_bounds[var4] != [0,0] else 1


                var3 = (
                    f"{var3}{self.fifteenth_place_truncation(firsthalf)}\t"
                    # f"{var3}{self.fifteenth_place_truncation(bounds[0] +((bounds[1] - bounds[0]) * Decimal(self.matrix_vars[var2][var4])))}\t"
                )

            for var4 in range(self.num_funcs):
                var3 = f"{var3}\t{self.fifteenth_place_truncation(self.matrix_funcs[var2][var4])}"

            base = f"{base}\n{var3}"

        # add ranges
        base += "\n# Variable Ranges\n"
        for var in range(len(self.var_bounds)):
            base += f"X{var+1}:\t{self.fifteenth_place_truncation(float(self.var_bounds[var][0]))},\t{self.fifteenth_place_truncation(float(self.var_bounds[var][1]))},\tREAL,\t0.000001\n"

        # add function values
        base += "\n# Function Definitions\n"
        for func in range(len(self.func_defs)):
            base += f"F{func + 1} = {self.func_defs[func]};\n"

        return base

    def get_des_matrix_model(self) -> tuple[list[float], list[str]]:
        """Returns the programmatic expression of the rows and headers for the design matrix"""
        rows = []

        self.matrix_funcs = [[[0] for _ in range(self.num_funcs)] for _ in range(self.orig_points)] if not self.matrix_funcs else self.matrix_funcs

        # evaluate everything for the originally generated points
        for row in range(self.orig_points):
            newRow = []

            # add the relative variable value
            for var in range(self.num_vars):
                newRow.append(
                    self.fifteenth_place_truncation(self.matrix_vars[row][var])
                )

            real_var_vals = []

            # add the absolute variable values
            for var in range(self.num_vars):
                # it is VERY IMPORTANT we use decimals here for precision
                bounds = [
                    Decimal(self.var_bounds[var][0]),
                    Decimal(self.var_bounds[var][1]),
                ]
                half = Decimal("0.5")

                evaluated_value = self.fifteenth_place_truncation(
                    float(
                        half * (bounds[0] + bounds[1])
                        + (half
                        * (bounds[1] - bounds[0])
                        * Decimal(self.matrix_vars[row][var]))
                    ) if self.var_bounds[var] != [0,0] else self.matrix_vars[row][var]
                )

                newRow.append(evaluated_value)
                real_var_vals.append(
                    float(
                        half * (bounds[0] + bounds[1])
                        + (half
                        * (bounds[1] - bounds[0])
                        * Decimal(self.matrix_vars[row][var]))
                    )
                )

            for func in range(self.num_funcs):
                if self.func_defs[func].strip() == "0":
                    newRow.append(self.matrix_funcs[row][func])
                else:
                    try:
                        evaluated_func = create_function_from_string(
                            clean(self.func_defs[func], len(self.matrix_vars[0]))
                        )(real_var_vals)
                        self.matrix_funcs[row][func] = evaluated_func

                        newRow.append(self.fifteenth_place_truncation(evaluated_func))
                    except Exception as e:
                        self.handle_error.gen_error(e)

            rows.append(newRow)

        # evaluate the user-added points
        for row in range(self.orig_points, self.num_points):
            newRow = []

            # add the relative variable value
            for var in range(self.num_vars):
                newRow.append(self.fifteenth_place_truncation(self.matrix_vars[row][var]))

            real_var_vals = []

            # add the absolute variable values
            for var in range(self.num_vars):     
                evaluated_value = self.fifteenth_place_truncation(
                    self.matrix_vars[row][var]
                )

            # calculate the real variable values
            for var4 in range(self.num_vars):

                bounds = [
                    Decimal(self.var_bounds[var4][0]),
                    Decimal(self.var_bounds[var4][1]),
                ]

                half = Decimal("0.5")


                firsthalf = (half*(bounds[0] + bounds[1]) + (Decimal(self.matrix_vars[row][var4])*half*(bounds[1] - bounds[0]))) if self.var_bounds[var4] != [0,0] else 1

                newRow.append(self.fifteenth_place_truncation(firsthalf))
                real_var_vals.append(self.fifteenth_place_truncation(firsthalf))

            for func in range(self.num_funcs):
                
                try:
                    evaluated_func = create_function_from_string(
                        clean(self.func_defs[func], len(self.matrix_vars[0]))
                    )(real_var_vals)
                    self.matrix_funcs[row].append(evaluated_func)
                    newRow.append(self.fifteenth_place_truncation(evaluated_func))

                except Exception as e:
                    if type(e) == ZeroDivisionError:
                        self.handle_error.gen_error("Cannot raise 0 to a negative power! Check your function definitions")
                    else:
                        self.handle_error.gen_error(e)
                    self.matrix_funcs[row].append(0)
                    newRow.append(0)

            rows.append(newRow)

        headers = []

        for var in range(self.num_vars):
            headers.append(f"X{var+1} (normalized)")

        for var in range(self.num_vars):
            headers.append(f"X{var+1} (real)")

        for func in range(self.num_funcs):
            headers.append(f"F{func+1}(X)")

        return rows, headers

    def set_var_bounds(self, ranges: list[list[float]]) -> None:
        """Set the variable bounds with the given list of ranges"""
        self.var_bounds = ranges

    def set_func_defs(self, func_defs: list[str]) -> None:
        """Assigns the function definition strings"""
        self.func_defs = func_defs

    def evaluate_func_defs(self, row: int) -> None:
        """Populates the function matrix with the given function definitions"""
        newVals = []
        for func in range(self.num_funcs):
            # reset if empty
            if self.func_defs[func] == "0":
                newVals.append(self.matrix_funcs[row][func])
            else:
                real_values = []
                for b, v in zip(self.var_bounds, self.matrix_vars[row]):
                    _min, _max = float(b[0]), float(b[1])
                    val = float(v)
                    real_values.append(normalize_to_real_value(val, _min, _max))

                value = create_function_from_string(
                clean(self.func_defs[func], len(self.matrix_vars[0]))
                )(real_values)
                newVals.append(float(value))
                self.matrix_funcs[row][func] = float(value)

        return [('%.15f' % i).rstrip('0').rstrip('.') for i in newVals]

    def get_des_matrix(
        self,
        doe_type: int,
        num_vars: int,
        num_levels: int,
        num_points: int,
        num_funcs: int,
    ):
        """Generate the appropriate design matrix given the type of problem

        Parameters
        ----------
        doe_type : int
            The type of the experimental design
        num_vars : int
            The number of variables in the design
        num_levels : int
            The number of levels in the design
        num_points : int
            The number of points in the design
        num_funcs : int
            The number of functions in the design
        """
        if (
            doe_type >= 0
            and doe_type <= 4
            and (doe_type != 4 or num_points >= 1)
            and num_vars > 0
        ):

            # minimum number of levels has to be 2
            if num_levels < 2:
                num_levels = 2

            self.doe_type = doe_type
            self.num_vars = num_vars
            self.num_levels = num_levels
            self.num_funcs = num_funcs

            match self.doe_type:
                case 0:
                    self.num_points = self.orig_points = int(
                        math.pow(float(self.num_levels), float(self.num_vars))
                    )
                    self.matrix_vars = [
                        [0 for _ in range(self.num_vars)]
                        for _ in range(self.num_points)
                    ]
                    self.gen_factorial_des_matrix(
                        self.matrix_vars, self.num_vars, self.num_levels
                    )
                case 1:
                    self.num_levels = 3
                    self.num_points = self.orig_points = int(
                        math.pow(2.0, float(self.num_vars))
                        + 2 * self.num_vars
                        + 1
                    )
                    self.matrix_vars = [
                        [0 for _ in range(self.num_vars)]
                        for _ in range(self.num_points)
                    ]
                    self.gen_ccspherical_des_matrix(
                        self.matrix_vars, self.num_vars
                    )
                case 2:
                    self.num_levels = 3
                    self.num_points = self.orig_points = int(
                        math.pow(2.0, float(self.num_vars))
                        + 2 * self.num_vars
                        + 1
                    )
                    self.matrix_vars = [
                        [0 for _ in range(self.num_vars)]
                        for _ in range(self.num_points)
                    ]
                    self.gen_cc_face_centered_des_matrix(
                        self.matrix_vars, self.num_vars
                    )
                case 3:
                    self.num_points = self.orig_points = (
                        self.get_taguchi_arr_pts(self.num_vars, self.num_levels)
                    )
                    if self.num_points <= 0:
                        self.has_data = False
                        return -1

                    self.matrix_vars = [
                        [0 for _ in range(self.num_vars)]
                        for _ in range(self.num_points)
                    ]
                    self.gen_taguchi_des_matrix(
                        self.matrix_vars, self.num_vars, self.num_levels
                    )
                case 4:
                    self.num_levels = self.num_points = self.orig_points = (
                        num_points
                    )
                    self.matrix_vars = [
                        [0 for j in range(self.num_vars)]
                        for i in range(self.num_points)
                    ]
                    self.gen_latin_hypercube_matrix(
                        self.matrix_vars, self.num_points, self.num_vars
                    )
                case _:
                    self.has_data = False
                    return -1

            self.matrix_funcs = [
                [0 for _ in range(self.num_funcs)]
                for _ in range(self.num_points)
            ]

            self.has_data = True
            return 1
        else:
            self.has_data = False
            return -1

    def gen_factorial_des_matrix(
        self, vars: list[list[float]], num_vars: int, lvl: int
    ) -> None:
        """Generates a factorial design matrix

        Parameters
        ----------
        I don't actually know what these parameters do
        """
        var4 = int(math.pow(float(lvl), float(num_vars)))
        self.design_levels = self.get_design_levels(lvl)

        for var5 in range(num_vars - 1, -1, -1):
            var6 = 0
            var7 = int(math.pow(float(lvl), float(num_vars - var5 - 1)))
            var8 = int(var4 / (var7 * lvl))

            for _ in range(var8):
                for level in range(lvl):
                    for _ in range(var7):
                        vars[var6][var5] = self.design_levels[level]
                        var6 += 1

    def gen_ccspherical_des_matrix(
        self, vars: list[list[float]], num_vars: int
    ):
        """Generate a CC Spherical design matrix with the given variables"""
        var3 = float(math.sqrt(float(num_vars)))
        self.gen_factorial_des_matrix(vars, num_vars, 2)
        var5 = int(math.pow(2.0, float(num_vars)))

        for var6 in range(0, 2 * num_vars, 2):
            for var7 in range(num_vars):
                vars[var5 + var6][var7] = var3 if var6 / 2 == var7 else 0.0
                vars[var5 + var6 + 1][var7] = -var3 if var6 / 2 == var7 else 0.0

        for var6 in range(num_vars):
            vars[var5 + 2 * num_vars][var6] = 0.0

        for var6 in range(var5 + 2 * num_vars + 1):
            for var7 in range(num_vars):
                var8 = vars[var6][var7] / var3
                var8 = (
                    (var8 + float(0.0000005))
                    if var8 > 0.0
                    else (var8 - float(0.0000005))
                )
                var10 = var8 * 1000000.0
                var8 = float(var10 / 1000000.0)
                vars[var6][var7] = var8

    def gen_cc_face_centered_des_matrix(
        self, vars: list[list[float]], num_vars: int
    ) -> None:
        """Generate a CC Face-Centered design matrix with the given variables"""
        self.gen_factorial_des_matrix(vars, num_vars, 2)
        var3 = int(math.pow(2.0, float(num_vars)))

        for var4 in range(0, 2 * num_vars, 2):
            for var5 in range(num_vars):
                vars[var3 + var4][var5] = 1.0 if var4 / 2 == var5 else 0.0
                vars[var3 + var4 + 1][var5] = -1.0 if var4 / 2 == var5 else 0.0

        for var4 in range(num_vars):
            vars[var3 + 2 * num_vars][var4] = 0.0

    def gen_taguchi_des_matrix(
        self, vars: list[list[float]], num_vars: int, num_levels: int
    ) -> None:
        """Generate a Taguchi design matrix with the given variables"""
        var4 = TextFileReader(
            "assets/TAGUCHI_ORTHOGONAL_ARRAY.TXT", "#$", self.handle_error
        )
        var4.set_skip_blank_line(True)
        var4.set_skip_comment_line(True)
        var5 = self.get_taguchi_arr_pts(num_vars, num_levels)
        var6 = f"*{num_levels}_LEVELS_L{var5}"
        var7 = None

        var8 = -1

        while var8 == -1 or var8.strip().lower() != var6.lower():
            var8 = var4.read_line()
            if var8 == None:
                var4.close()
                return

        for var9 in range(var5):
            var7 = var4.read_line()
            var10 = re.split("\s|,|\t|\n|\r", var7)
            var10.pop(0)

            for var11 in range(num_vars):
                vars[var9][var11] = float(var10.pop(0))

        var4.close()

    def gen_latin_hypercube_matrix(
        self, vars: list[list[float]], num_vars: int, var3: int
    ) -> None:
        """Generate a Latin Hybercube design matrix with the given variables"""
        var11 = random.random()

        var9 = 0
        for var4 in range(num_vars):
            var9 = float(-1.0) + float(var4) * 2.0 / float(num_vars - 1)
            var9 = var9 + (
                float(0.0000005) if var9 > 0.0 else -float(0.0000005)
            )
            var12 = float(var9 * 1000000.0)

            for var5 in range(var3):
                vars[var4][var5] = var12 / 1000000.0

        for var4 in range(num_vars):
            var8 = num_vars - var4
            for var5 in range(var3):
                var7 = int(math.abs(var11) % float(var8))
                var9 = vars[var4 + var7][var5]

                for var6 in range(var7, 0, -1):
                    vars[var4 + var6][var5] = vars[var4 + var6 - 1][var5]

                vars[var4][var5] = var9

    def get_des_matrix_summary_str(self) -> str:
        """Returns the summary string of the design matrix"""
        var1 = ""
        if not self.has_data:
            return var1
        else:
            match self.doe_type:
                case 0:
                    var1 = f"{var1}# FACTORIAL DESIGN"
                case 1:
                    var1 = f"{var1}# CENTRAL COMPOSITE DESIGN: SPHERICAL"
                case 2:
                    var1 = f"{var1}# CENTRAL COMPOSITE DESIGN: FACE CENTERED"
                case 3:
                    var1 = f"{var1}# TAGUCHI DESIGN"
                case 4:
                    var1 = f"{var1}# LATIN HYPERCUBE DESIGN"
                case _:
                    var1 = f"{var1}# USER DEFINED DESIGN"

            var1 = (
                f"{var1}\n#     Number of Data Points:   {self.num_points}    "
                f"        \n#     Number of Variables:     {self.num_vars}    "
                f"        \n#     Number of Design Levels: {self.num_levels}  "
                f"          \n#     Number of Functions:     {self.num_funcs} "
                "           \n#\n# NUM_POINTS    NUM_VARS    NUM_LEVELS   "
                f" NUM_FUNCS            \n      {self.num_points}           "
                f" {self.num_vars}           {self.num_levels}           "
                f" {self.num_funcs}            \n#\n#\n#No.\t"
            )

            # headers for variables
            for var2 in range(self.num_vars):
                var1 = f"{var1}X{var2+1}\t"

            for var2 in range(self.num_vars):
                var1 = f"{var1}X{var2+1} (real)\t"

            # headers for functions
            for var2 in range(self.num_funcs):
                var1 = f"{var1}\tf{var2+1}(X)"

            var1 = f"{var1}\n#"

            for var2 in range(self.num_vars + self.num_funcs + 2):
                var1 = f"{var1}--------"

            var1 = f"{var1}"
            return var1

    def get_var_matrix(self) -> Matrix:
        """Returns the variable matrix"""
        return Matrix(self.matrix_vars, handle_error=self.handle_error)

    def get_func_matrix(self) -> Matrix:
        """Returns the function matrix"""
        return Matrix(self.matrix_funcs, handle_error=self.handle_error)

    def get_control_info_str(self) -> str:
        """Returns the header for the top of .doe file"""
        if not self.has_data:
            return ""
        else:
            return (
                "           "
                " ######################################################################"
                "            \n#  DESIGN OF EXPERIMENTS                        "
                "                     #            \n#       HiPPO  ---  High"
                " Performance Processing Option               #            \n# "
                "      Hongbing Fang, CAVS, Mississippi State University       "
                "     #           "
                " \n######################################################################\n"
                "            #\n"
            )

    def get_design_levels(self, doe_type: int) -> list[list[float]]:
        """Returns the design levels for the given doe_type"""
        var6 = []
        match doe_type:
            case 2:
                var6 = self.LEVELS2
            case 3:
                var6 = self.LEVELS3
            case 4:
                var6 = self.LEVELS4
            case 5:
                var6 = self.LEVELS5
            case 6:
                var6 = self.LEVELS6
            case 7:
                var6 = self.LEVELS7
            case 8:
                var6 = self.LEVELS8
            case 9:
                var6 = self.LEVELS9
            case _:
                var3 = 2.0 / float(doe_type - 1)
                var6 = [float(-1) + float(i * var3) for i in range(doe_type)]
        return var6

    def get_taguchi_arr_pts(self, num_vars: int, num_levels: int) -> int:
        """Returns the array points for a Taguchi Orthogonal Array"""
        var3 = 0
        if num_levels == 2:
            if num_vars <= 3:
                var3 = 4
            elif num_vars <= 7:
                var3 = 8
            elif num_vars <= 11:
                var3 = 12
            elif num_vars <= 15:
                var3 = 16
            elif num_vars <= 31:
                var3 = 32
        elif num_levels == 3:
            if num_vars <= 4:
                var3 = 9
            elif num_vars <= 8:
                var3 = 18
            elif num_vars <= 13:
                var3 = 27
            elif num_vars <= 23:
                var3 = 36
            elif num_vars <= 26:
                var3 = 54
            elif num_vars <= 40:
                var3 = 81
        elif num_levels == 4:
            if num_vars <= 5:
                var3 = 16
            elif num_vars <= 10:
                var3 = 32
            elif num_vars <= 21:
                var3 = 64
        elif num_levels == 5:
            if num_vars <= 6:
                var3 = 25
            elif num_vars <= 12:
                var3 = 50
        return var3

    def __str__(self):
        ret = ""
        ret += f"doe_type = {self.doe_type}\n"
        ret += f"num_vars = {self.num_vars}\n"
        ret += f"num_levels = {self.num_levels}\n"
        ret += f"num_points = {self.num_points}\n"
        ret += f"orig_points = {self.orig_points}\n"
        ret += f"num_funcs = {self.num_funcs}\n"
        ret += f"design_levels = {self.design_levels}\n"
        ret += f"has_data = {self.has_data}\n"
        ret += f"matrix_vars = {self.matrix_vars}\n"
        ret += f"matrix_funcs = {self.matrix_funcs}\n"
        ret += f"func_defs = {self.func_defs}\n"
        ret += f"var_bounds = {self.var_bounds}"
        return ret
