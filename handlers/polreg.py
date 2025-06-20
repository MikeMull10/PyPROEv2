from handlers.fullpolynomial import FullPolynomial
from handlers.matrix import LDLTSolver, Matrix
from handlers.orthogpoly import OrthogonalPolynomial
from handlers.statistics import Statistics


class PR:
    """A class representing polynomial regression"""

    def __init__(
        self,
        matrix_vars: "Matrix",
        matrix_funcs: "Matrix",
        num_pr_funcs: int,
        polynomial_order: int,
        handle_error: None,
    ):
        """Initialize with a matrices for variables and functions, the number for functions, and polynomial order

        Parameters
        ----------
        matrix_vars : Matrix
            A matrix of the variables for polynomial regression
        matrix_funcs : Matrix
            A matrix of the functions for polynomial regression
        num_pr_funcs : int
            The number of functions for polynomial regression
        polynomial_order : int
            The polynomial order of the regression
        """
        self.PR_OK = 1
        self.PR_ERROR = -1
        self.PR_LINEAR = 0
        self.PR_QUADRATIC_FULL = 1
        self.PR_QUADRATIC_ORTHOGONAL = 2
        self.matrix_vars: Matrix = matrix_vars
        self.matrix_funcs: Matrix = matrix_funcs

        self.num_points = self.matrix_vars.size_rows()
        self.num_vars = self.matrix_vars.size_cols()
        self.num_funcs = self.matrix_funcs.size_cols()
        self.num_terms: int = None
        self.pr_func: int = num_pr_funcs
        self.poly_order: int = polynomial_order

        self.hii: list[float] = []
        self.functions: list[FullPolynomial | OrthogonalPolynomial] = []
        self.gradients: list[list[OrthogonalPolynomial]] = []
        self.handle_error = handle_error

    def get_pr_funcs(self):
        """Initialize the functions for polynomial regression"""
        var1 = None
        if self.pr_func != 2:
            var1 = FullPolynomial(
                self.poly_order, self.num_vars, self.handle_error
            )
        else:
            var1 = OrthogonalPolynomial(
                self.poly_order, self.num_vars, self.handle_error
            )

        self.num_terms = var1.get_num_terms()
        if self.num_terms > self.num_points:
            return -1
        else:
            var2 = Matrix(
                self.num_points, self.num_terms, handle_error=self.handle_error
            )
            var3 = self.matrix_vars.get_array()

            for var4 in range(self.num_points):
                for var5 in range(self.num_terms):
                    var2.set(
                        var4, var5, var1.get_func_value_at(var3[var4], var5)
                    )

            var10 = var2.transpose()
            self.hii = [None for i in range(self.num_points)]
            self.get_hat_matrix(var2, var10)
            var11 = var10.times(var2)
            var6 = var10.times(self.matrix_funcs)
            var7 = LDLTSolver(var11, handle_error=self.handle_error)
            var8 = var7.solve(var6)
            self.functions = [None for _ in range(self.num_funcs)]
            self.gradients = [[] for _ in range(self.num_funcs)]

            for var9 in range(self.num_funcs):
                if self.pr_func != 2:
                    self.functions[var9] = FullPolynomial(
                        self.poly_order, self.num_vars, self.handle_error
                    )
                else:
                    self.functions[var9] = OrthogonalPolynomial(
                        self.poly_order, self.num_vars, self.handle_error
                    )

                self.functions[var9].set_coefficients(var8.get_col_vector(var9))
                self.gradients[var9] = self.functions[var9].get_gradients()

            return 1

    def get_hat_matrix(self, matrix_a: Matrix, matrix_b: Matrix) -> None:
        """Set the hat matrix for regression"""
        var3 = matrix_b.times(matrix_a)
        var4 = var3.inverse()
        var5 = matrix_a.times(var4.times(matrix_b))

        for var6 in range(var5.size_rows()):
            self.hii[var6] = var5.get(var6, var6)

    def get_func_value(self, values: list[float]) -> list[float]:
        """Returns the evaluations of each function with the given values"""
        return [
            self.functions[i].get_func_value(values)
            for i in range(self.num_funcs)
        ]

    def get_func_str(self) -> str:
        """Return all the polynomial function strings"""
        var1 = ""
        for var2 in range(self.num_funcs):
            var1 = (
                f"{var1}f{var2 + 1} = {self.functions[var2].get_func_str()};\n"
            )
        return var1

    def get_grad_str(self) -> str:
        """Return all the function strings for the gradient functions"""
        var1 = ""

        for var2 in range(self.num_funcs):
            for var3 in range(self.num_vars):
                var1 = (
                    f"{var1}gf{var2 + 1}-x{var3 + 1} ="
                    f" {self.gradients[var2][var3].get_func_str()};\n"
                )
            var1 = f"{var1}\n"

        return var1

    def get_stats(self) -> str:
        """Return the statistics for the polynomial functions"""
        var3 = (
            "POLYNOMIAL FUNCTION"
            " STATISTICS\n------------------------------------\n"
        )

        for var4 in range(self.num_funcs):
            var5 = Statistics(
                self.matrix_vars.get_array(),
                self.matrix_funcs.get_col_vector(var4),
                self.functions[var4],
                self.hii,
            )
            var3 = f"{var3}f{var4 + 1}(x):\n{var5.get_stats()}\n"

        return var3

    def get_num_funcs(self) -> int:
        """Returns the number of functions for the polynomial regression"""
        return self.num_funcs

    def get_num_terms(self) -> int:
        """Returns the number of terms for the polynomial regression"""
        return self.num_terms

    def get_num_vars(self) -> int:
        """Returns the number of variables for the polynomial regression"""
        return self.num_vars
