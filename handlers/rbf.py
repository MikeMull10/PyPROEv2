from handlers.matrix import Matrix
from handlers.radbasisfunc import RadialBasisFunction

class RBF:
    """A class representing a radial basis function"""

    def __init__(
        self,
        matrix_vars: Matrix,
        matrix_funcs: Matrix,
        rbfunction: int,
        order: int,
        handle_error: None,
    ):
        """Initialize with matrices of variables, functions, an rbfunction, and an order

        Parameters
        ----------
        matrix_vars : Matrix
            A matrix of the variables for the radial basis function
        matrix_funcs : Matrix
            A matrix of the functions for the radial basis function
        rbfunction : int
            The number for the radial basis function
        order : int
            The polynomial order of the radial basis function
        """
        self.RBF_OK = 1
        self.RBF_ERROR = -1
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

        self.matrix_vars = matrix_vars
        self.matrix_funcs = matrix_funcs
        self.num_points = self.matrix_vars.size_rows()
        self.num_vars = self.matrix_vars.size_cols()
        self.num_funcs = self.matrix_funcs.size_cols()
        self.rbfunction = rbfunction
        self.poly_order = order
        self.functions: list[RadialBasisFunction] = []
        self.handle_error = handle_error

    def get_rbf_functions(self) -> int:
        """Formulate basis functions"""
        self.functions = [None for _ in range(self.num_funcs)]

        for var1 in range(0, self.num_funcs):
            func = RadialBasisFunction(self.handle_error)
            func.set_initial_data(
                self.matrix_vars,
                Matrix(
                    self.matrix_funcs.get_col_vector(var1),
                    handle_error=self.handle_error,
                ),
            )
            if (
                func.get_formulation(
                    self.rbfunction, self.poly_order
                )
                != 1
            ):
                return -1
            self.functions[var1] = func
        return 1

    def get_func_value(self, values: list[float]) -> list[float]:
        """Evalue the function with a list of values"""
        var2 = [None for _ in range(self.num_funcs)]

        for var3 in range(self.num_funcs):
            var2[var3] = self.functions[var3].get_func_value(values)

        return var2

    def get_func_str(self) -> str:
        """Get the function string for the radial basis function"""
        var1 = ""

        for var2 in range(self.num_funcs):
            var1 = (
                f"{var1}f{var2 + 1} = {self.functions[var2].get_func_str()};\n"
            )

        return var1

    def get_grad_str(self) -> str:
        """Returns a string representinf the function's gradient(s)"""
        var1 = ""

        for var2 in range(self.num_funcs):
            for var3 in range(self.num_vars):
                var1 = (
                    f"{var1}gf{var2 + 1}-x{var3 + 1} ="
                    f" {self.functions[var2].get_grad_expr(var3)};\n"
                )
            var1 = f"{var1}\n"

        return var1

    def get_num_funcs(self) -> int:
        """Returns the number for functions in the radial basis function"""
        return self.num_funcs

    def get_num_vars(self) -> int:
        """Returns the number of variables in the radial basis function"""
        return self.num_vars

    def get_stats(self) -> str:
        """Returns the statics for the radius of design space"""
        var1 = (
            "RADIAL BASIS FUNCTION"
            " STATISTICS\n------------------------------------\n"
        )
        var1 = (
            f"{var1}  Radius of Design Space            \n    Minimum:"
            f" {self.functions[0].get_min_radius()}            \n    Maximum:"
            f" {self.functions[0].get_max_radius()}            \n    Average:"
            f" {self.functions[0].get_avg_radius()}            \n    Norm:"
            f" {self.functions[0].get_norm()}\n"
        )
        return var1
