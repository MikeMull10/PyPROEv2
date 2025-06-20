from decimal import Decimal
from handlers.polynomialregression import PolynomialRegression
from handlers.filewriter import TextFileWriter
from handlers.errorhandler import ErrorHandler
from handlers.doefile import DOEFile
from handlers.matrix import Matrix
from handlers.polreg import PR
from handlers.rbf import RBF
from pages.designexp import DOE
from pages.mainwindow import Ui_MainWindow


class MMD:
    """A class managing the metamodeling page"""

    def __init__(self, ui: Ui_MainWindow, handle_error):
        """Initialize the page with an instance of the UI"""
        self.MMD_OK = 1
        self.MMD_ERROR = -1
        self.MMD_PR = 0
        self.MMD_RBF = 1
        self.MMD_INVALID = -1
        self.PR_LINEAR = 0
        self.PR_QUADRATIC_FULL = 1
        self.PR_QUADRATIC_ORTHOGONAL = 2
        self.RBF_LINEAR = 0
        self.RBF_CUBIC = 1
        self.RBF_THIN_PLATE_SPLINE = 2
        self.RBF_GAUSSIAN = 3
        self.RBF_MULTIQUADRIC = 4
        self.RBF_INV_MULTIQUADRIC = 5
        self.RBF_COMPACT_SUPPORT_20 = 6
        self.RBF_COMPACT_SUPPORT_21 = 7
        self.RBF_COMPACT_SUPPORT_22 = 8
        self.RBF_COMPACT_SUPPORT_30 = 9
        self.RBF_COMPACT_SUPPORT_31 = 10
        self.RBF_COMPACT_SUPPORT_32 = 11
        self.RBF_COMPACT_SUPPORT_33 = 12
        self.Method = ["Polynomial Regression", "Radial Basis Functions"]
        self.PR_Funcs = [
            "Linear polynomial",
            "Quadratic polynomial no interaction",
            "Quadratic polynomial with interaction",
        ]
        self.RBF_Funcs = [
            "Linear",
            "Cubic",
            "Thin Plate Spline",
            "Gaussian",
            "Multiquadric",
            "Inverse Multiquadric",
            "Compactly Supported (2,0)",
            "Compactly Supported (2,1)",
            "Compactly Supported (2,2)",
            "Compactly Supported (3,0)",
            "Compactly Supported (3,1)",
            "Compactly Supported (3,2)",
            "Compactly Supported (3,3)",
        ]

        self.method = 0
        self.function_type = 0
        self.poly_order = 0
        self.num_points = 0
        self.num_vars = 0
        self.num_funcs = 0
        self.matrix_vars: Matrix = None
        self.matrix_funcs: Matrix = None
        self.pr: PolynomialRegression = None
        self.rbf: RBF = None
        self.ui = ui
        self.doe: DOEFile = None

        self._has_data = False
        self._observers = []
        self.var_bounds: list[list[float]] = []
        self.handle_error: ErrorHandler = handle_error

    # setting this as a property can bind it to
    # enabling/disabling UI buttons
    @property
    def has_data(self):
        return self._has_data

    @has_data.setter
    def has_data(self, value: bool):
        self._has_data = value
        for callback in self._observers:
            callback(self._has_data)

    def bindTo(self, callback):
        self._observers.append(callback)

    def read_design_file(self, filename: str, is_str=False) -> int:
        """Read in the given design file"""
        self.doe = DOEFile(filename, is_str=is_str)
        self.pr = PolynomialRegression(self.doe)
        
        # if is_str:
        #     return 1

        try:
            var2: DOE = DOE(self.ui, self.handle_error)

            if var2.doe_file_reader(filename, is_str=is_str) != 1:
                return -1
            else:
                self.matrix_vars = var2.get_var_matrix()
                self.matrix_funcs = var2.get_func_matrix()
                self.num_points = self.matrix_vars.size_rows()
                self.num_vars = self.matrix_vars.size_cols()
                self.num_funcs = self.matrix_funcs.size_cols()
                self.var_bounds = var2.var_bounds
                self.has_data = True
                return 1
        
        except Exception as e:
            self.handle_error.gen_error(e)

    def read_doe_tab(self, doe: DOE) -> int:
        """Read data from the doe page"""
        try:
            self.matrix_vars = doe.get_var_matrix()
            self.matrix_funcs = doe.get_func_matrix()
            self.num_points = self.matrix_vars.size_rows()
            self.num_vars = self.matrix_vars.size_cols()
            self.num_funcs = self.matrix_funcs.size_cols()
            self.has_data = True
            self.var_bounds = doe.var_bounds
            return 1
        except Exception as e:
            return -1

    def get_des_matrix(self, vars: Matrix, funcs: Matrix) -> int:
        """Get the design matrix for the given variable and function matrices"""
        self.matrix_vars = Matrix(vars, handle_error=self.handle_error)
        self.matrix_funcs = Matrix(funcs, handle_error=self.handle_error)
        self.num_points = self.matrix_vars.size_rows()
        self.num_vars = self.matrix_vars.size_cols()
        self.num_funcs = self.matrix_funcs.size_cols()
        self.has_data = True
        return 1

    def get_mmd_funcs(self, method: int, matrix_funcs: int, order: int) -> int:
        """Get metamodeling functions"""
        if not self.has_data:
            return -1
        else:
            self.method = method
            self.function_type = matrix_funcs
            self.poly_order = order
            
            if self.method == 0:
                self.poly_order = 1 if self.function_type == 0 else 2

                match self.function_type:
                    case 0:
                        self.pr.data = self.pr.linear()
                    case 1:
                        self.pr.data = self.pr.quad_no_int()
                    case 2:
                        self.pr.data = self.pr.quad_interaction()
                    case _:
                        return -1

            elif self.method == 1:
                # get all the auto-generated points
                var_array = self.matrix_vars.get_array()
                eval_vars = []
                for var2 in range(len(var_array)):
                    row = []
                    for var4 in range(self.num_vars):
                        bounds = [
                            Decimal(self.var_bounds[var4][0]),
                            Decimal(self.var_bounds[var4][1]),
                        ]

                        half = Decimal("0.5")

                        firsthalf = (half*(bounds[0] + bounds[1]) + (Decimal(var_array[var2][var4])*half*(bounds[1] - bounds[0]))) if self.var_bounds[var4] != [0,0] else 1

                        row.append(float(firsthalf))
                    eval_vars.append(row)
                    
                self.rbf = RBF(
                    Matrix(eval_vars),
                    self.matrix_funcs,
                    self.function_type,
                    self.poly_order,
                    self.handle_error,
                )
                if self.rbf.get_rbf_functions() != 1:
                    return -1

            return 1

    def get_func_value(self, vals: list[float]) -> list[float]:
        """Evaluate the function with the given values"""
        var2 = None
        if not self.has_data:
            return None
        else:
            if self.method == 0:
                var2 = self.pr.get_func_value(vals)
            elif self.method == 1:
                var2 = self.rbf.get_func_value(vals)
            return var2

    def get_func_str(self) -> str:
        """Returns a function string for the PR or RBF function"""
        var1 = None
        if self.method == 0:
            var1 = (
                f"# {self.PR_Funcs[self.function_type]}           "
                " \n#------------------------------------           "
                f" \n{self.pr.get_func_str()}"
                # f" \n{self.pr.get_func_grads()}"
            )
        elif self.method == 1:
            var1 = (
                f"# {self.RBF_Funcs[self.function_type]}              +"
                f" {self.poly_order}-order polynomial               "
                " \n#------------------------------------               "
                f" \n{self.rbf.get_func_str()}"
            )
        return var1

    def get_grad_str(self) -> str:
        """Returns a string with all the function gradients"""
        var1 = "# FUNCTION GRADIENTS\n#------------------------------------\n"
        if self.method == 0:
            var1 = f"{var1}{self.pr.get_func_grads()}"
        if self.method == 1:
            var1 = f"{var1}{self.rbf.get_grad_str()}"
        return var1

    def get_stats(self, _type: int = 0, _func: int = 0) -> str:
        """Returns a string with all the statistics about the function"""
        var1 = None
        if self.method == 0:
            var1 = self.pr.get_stats(_type, _func)
        elif self.method == 1:
            var1 = self.rbf.get_stats()
        return var1

    def get_num_funcs(self) -> int:
        """Returns the number of functions"""
        return self.num_funcs

    def get_num_vars(self) -> int:
        """Returns the number of variables"""
        return self.num_vars

    def mmd_func_writer(self, filename: str) -> int:
        """Write the function file to the given filename"""
        var4 = TextFileWriter(filename, self.handle_error)
        if not var4.is_file_open():
            return -1
        else:
            var4.WriteLine(self.mmd_full_func_file_str())

    def mmd_full_func_file_str(self):
        """Returns the full fnc file string"""
        var3 = (
            "######################################################################\n#"
            "  Optimization input file for GimOPT                              "
            "  #\n# "
            " ------------------------------------------------------------------#\n#"
            "  Metamodels Generated by HiPPO                                   "
            "  #\n#                                                            "
            "        #\n#     Hongbing Fang                                    "
            "              #\n#     Center for Advanced Vehicular Systems      "
            "                    #\n#     Mississippi State University         "
            "                         "
            " #\n######################################################################\n"
        )
        if self.method == 0:
            var3 = (
                f"{var3}\n# Method: Response Surface Methodology\n# Function:"
                f" {self.PR_Funcs[self.function_type]}\n"
            )
        elif self.method == 1:
            var3 = (
                f"{var3}\n# Method: Radial Basis Functions\n# Function:"
                f" {self.RBF_Funcs[self.function_type]} +"
                f" {self.poly_order}-order polynomial \n"
            )

        # var3 = f"{var3}\n# Number of Variables, Objectives, Inequality and Equality Constraints\
        # \n#---------------------------------------------------------------------\
        # \nVariables:       {self.num_vars}\
        # \nObjectives:      {self.num_funcs}\
        # \nIneqConstraints: 1\nEqConstraints:   0\
        # \n\n# Number of sets of variables for testing function values\
        # \n#---------------------------------------------------------------------\
        # \nTestVariables:\t{self.num_points}\n\n# Use approximate gradients ( Yes/No )\
        # \n#---------------------------------------------------------------------\
        # \nApproximateGradients: No\
        # \n\n# Normalize objectives and their gradients ( Yes/No )\
        # \n#---------------------------------------------------------------------\
        # \nNormalize: No\n\n# Modes for normalizing objectives\
        # \n#---------------------------------------------------------------------\n"

        # for var2 in range(self.num_funcs):
        #     var3 = f"{var3}1.0    "

        # var3 = f"{var3}\n\n# Objective weight (Wi) in WSF with fixed weight\n#---------------------------------------------------------------------\n"

        # for var2 in range(self.num_funcs):
        #     var3 = f"{var3}1.0    "

        var3 = f"*VARIABLE: {self.num_vars}\n"

        for i in range(len(self.var_bounds)):
            var3 = f"X{i+1}:\t{self.var_bounds[i][0]},\t{self.var_bounds[i][0]},\tREAL,\t0.000001\n"
        
        if self.method == 0:
            for i, (_min, _max) in enumerate(self.pr.doe_file.get_var_data()):
                var3 += f"X{ i + 1 }: { _min },\t{ _max }\n"

            var3 += f"\n*FUNCTION: { len( self.pr.data ) }\n{self.pr.get_func_str()}"

            var3 += f"\n*GRADIENT\n{self.pr.get_func_grads()}"
        elif self.method == 1:
            var3 = (
                f"{var3}\n\n\n# Objective"
                " Functions\n#---------------------------------------------------------------------\n"
            )

            var3 = f"{var3}{self.rbf.get_func_str()}"

            var3 = (
                f"{var3}\n# Constraint"
                " Functions\n#---------------------------------------------------------------------\nc1"
                " = -1.0;\n\n\n"
            )
            var3 = (
                f"{var3}# Gradient Functions of the"
                " objectives\n#---------------------------------------------------------------------\n"
            )
            if self.method == 0:
                var3 = f"{var3}{self.pr.get_func_grads()}"
            elif self.method == 1:
                var3 = f"{var3}{self.rbf.get_grad_str()}"

            var3 = (
                f"{var3}# Gradient Functions of the"
                " constraints\n#---------------------------------------------------------------------\n"
            )

            for var2 in range(self.num_vars):
                var3 = f"{var3}gc1-x{var2 + 1} = 0.0;\n"

            var3 = (
                f"{var3}\n\n# Lower bound, upper bound, and initial values of"
                " variables\n#---------------------------------------------------------------------\n"
            )

            for var2 in range(self.num_vars):
                var3 = f"{var3}-1.0    1.0    -0.5\n"

            var3 = (
                f"{var3}\n\n# Variables for testing objective and constraint"
                " functions\n#---------------------------------------------------------------------\n"
            )
            var5: list[list[float]] = self.matrix_vars.get_array()

            for var2 in range(self.num_points):
                for var6 in range(self.num_vars):
                    var3 = f"{var3}{var5[var2][var6]}\t"
                var3 = f"{var3}\n"

            var3 = f"{var3}\n\n# End of Function File\n"
        return var3

    def __str__(self):
        matrix_vars_str = str(self.matrix_vars.get_array())
        matrix_funcs_str = str(self.matrix_funcs.get_array())
        print(f"{matrix_vars_str}, {matrix_funcs_str}")
        return "\n".join([str(x) for x in [self.method, self.function_type, self.poly_order, self.num_points, self.num_vars, self.num_funcs]])
