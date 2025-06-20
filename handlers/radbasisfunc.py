import math

from handlers.fullpolynomial import FullPolynomial
from handlers.matrix import LDLTSolver, Matrix


class RadialBasisFunction:
    """A class representing radial functions and their associated operations"""

    def __init__(self, handle_error: None):
        """Initialize the class"""
        # Types of RBF functions
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

        self.num_points = 0
        self.num_vars = 0
        self.num_terms = 0
        self.rb_func = 0
        self.poly_order = 0

        self.handle_error = handle_error

        # TODO: is this correct?
        self.EPSILON = float(0.1)

        self.matrix_vars: list[list[float]] = None
        self.matrix_funcs: list[float] = None
        self.coefficients: list[float] = None
        self.min_radius = float(0.0)
        self.max_radius = float(0.0)
        self.avg_radius = float(0.0)
        self.norm = float(0.0)
        self.norm_two = float(0.0)
        self.norm_three = float(0.0)
        self.polynomial: FullPolynomial = None
        self.poly_grads: list[FullPolynomial] = None

    def get_func_value(self, values: list[float]) -> float:
        """Evaluate the function with the given values"""
        var2 = float(0.0)

        if (
            self.coefficients == None
            and self.get_formulation(self.rb_func, self.poly_order) != 1
        ):
            return var2
        else:
            if self.poly_order > 0:
                self.polynomial.set_coefficients(
                    self.coefficients, self.num_points
                )
                var2 += self.polynomial.get_func_value(values)

            for var4 in range(self.num_points):
                var2 += self.coefficients[var4] * self.get_rbf_value(
                    values, self.matrix_vars[var4]
                )

            return var2

    def get_func_value_at(self, values: list[float], term: int) -> float:
        """Get the function value at the specific term

        Parameters
        ----------
        values : list[float]
            A list of the values to use in evaluation
        term : int
            The index of the term in the function to evaluate
        """
        return self.get_rbf_value(values, self.matrix_vars[term])

    def get_gradients(self) -> list | None:
        """No gradients for RBF; returns None"""
        return None

    def get_coefficients(self) -> list[float]:
        """Returns the coefficients for the radial basis function"""
        return self.coefficients

    def set_coefficients(self, coeffs: list[float]):
        """Set the coefficients for the radial basis function"""
        self.coefficients = coeffs
        # for var2 in range(len(self.coefficients)):
        #     self.coefficients[var2] = coeffs[var2]

    def get_num_terms(self) -> int:
        """Returns the number of terms in the radial basis function"""
        return self.num_points

    def get_num_vars(self) -> int:
        """Returns the number of variables in the radial basis function"""
        return self.num_vars

    def get_order(self) -> int:
        """Returns the order of the radial basis function"""
        return 0

    def get_min_radius(self) -> float:
        """Returns the minimum radius of the radial basis function"""
        return self.min_radius

    def get_max_radius(self) -> float:
        """Returns the maximum radius of the radial basis function"""
        return self.max_radius

    def get_avg_radius(self) -> float:
        """Returns the average radius of the radial basis function"""
        return self.avg_radius

    def get_norm(self) -> float:
        """Returns the norm of the radial basis function"""
        return self.norm

    def set_initial_data(self, matrix_a: Matrix, matrix_b: Matrix) -> None:
        """Initialize the data for the radial basis function"""
        self.matrix_vars = matrix_a.get_array()
        self.matrix_funcs = matrix_b.get_col_vector(0)
        self.num_points = matrix_a.size_rows()
        self.num_vars = matrix_a.size_cols()
        self.get_design_space_radii()
        self.norm = float(self.num_vars * self.max_radius)
        self.norm_two = self.norm * self.norm
        self.norm_three = self.norm * self.norm_two

    def set_epsilon(self, var1: float) -> None:
        """Set the epsilon for the radial basis function"""
        if var1 > 0.0 and var1 < 1.0:
            self.EPSILON = var1

    def get_formulation(self, func: int, order: int) -> int:
        """Get the formulation of the radial basis function"""
        self.rb_func = func
        self.poly_order = order
        if self.matrix_vars != None and self.matrix_funcs != None:
            if self.poly_order > 0:
                self.polynomial = FullPolynomial(
                    self.poly_order, self.num_vars, self.handle_error
                )
                self.num_terms = self.polynomial.get_num_terms()
            else:
                self.num_terms = 0

            var3: Matrix = None
            var4: Matrix = None
            var5: Matrix = None
            var6: Matrix = None

            var3 = Matrix(
                self.num_points + self.num_terms,
                self.num_points + self.num_terms,
                0.0,
                handle_error=self.handle_error,
            )


            var4 = Matrix(
                self.num_points, self.num_points, handle_error=self.handle_error
            )
            if self.num_terms > 0:
                var5 = Matrix(
                    self.num_points,
                    self.num_terms,
                    handle_error=self.handle_error,
                )


            var6 = Matrix(
                self.num_points + self.num_terms,
                1,
                0.0,
                handle_error=self.handle_error,
            )

            for var7 in range(self.num_points):
                for var8 in range(self.num_points):
                    var4.set(
                        var7,
                        var8,
                        self.get_rbf_value(
                            self.matrix_vars[var7], self.matrix_vars[var8]
                        ),
                    )

            if self.num_terms > 0:
                for var7 in range(self.num_points):
                    for var8 in range(self.num_terms):
                        var5.set(
                            var7,
                            var8,
                            self.polynomial.get_func_value_at(
                                self.matrix_vars[var7], var8
                            ),
                        )

            var3.set_submatrix(var4, 0, 0)
            if self.num_terms > 0:
                var3.set_submatrix(var5, 0, self.num_points)
                var3.set_submatrix(var5.transpose(), self.num_points, 0)

            var6.set_submatrix(
                Matrix(self.matrix_funcs, handle_error=self.handle_error), 0, 0
            )

            var9 = LDLTSolver(var3, handle_error=self.handle_error)

            self.coefficients = var9.solve(var6).get_col_vector(0)

            if self.num_terms > 0:
                self.polynomial.set_coefficients(
                    self.coefficients, self.num_points
                )

            if order > 0:
                self.poly_grads = self.polynomial.get_gradients()
            return 1
        else:
            self.handle_error("RBF: No initial data to construct function")
            return -2

    def get_design_space_radii(self) -> None:
        """Set the design space radii"""
        self.min_radius = float("1.0E38")
        self.max_radius = float(0.0)
        self.avg_radius = float(0.0)

        for var3 in range(self.num_points - 1):
            for var4 in range(var3 + 1, self.num_points):
                var1 = math.sqrt(
                    self.get_euclidean_dist_square(
                        self.matrix_vars[var3], self.matrix_vars[var4]
                    )
                )
                if self.min_radius > var1:
                    self.min_radius = var1

                if self.max_radius < var1:
                    self.max_radius = var1

                self.avg_radius += var1
        var3 = self.num_points * (self.num_points - 1) / 2
        self.avg_radius /= float(var3)

    def get_rbf_value(self, var1: list[float], var2: list[float]) -> float:
        """Evaluate the radial basis function with the euclidean square distance of the input lists"""
        var3 = self.get_euclidean_dist_square(var1, var2)
        var5 = float(0.0)

        match self.rb_func:
            case 0:
                var5 = self.rbf_linear(var3)
            case 1:
                var5 = self.rbf_cubic(var3)
            case 2:
                var5 = self.rbf_thin_plate_spline(var3)
            case 3:
                var5 = self.rbf_gaussian(var3)
            case 4:
                var5 = self.rbf_multiquadratic(var3)
            case 5:
                var5 = self.rbf_inverse_multiquadratic(var3)
            case 6:
                var5 = self.rbf_compactly_supported_20(var3)
            case 7:
                var5 = self.rbf_compactly_supported_21(var3)
            case 8:
                var5 = self.rbf_compactly_supported_22(var3)
            case 9:
                var5 = self.rbf_compactly_supported_30(var3)
            case 10:
                var5 = self.rbf_compactly_supported_31(var3)
            case 11:
                var5 = self.rbf_compactly_supported_32(var3)
            case 12:
                var5 = self.rbf_compactly_supported_33(var3)

        return var5

    def get_euclidean_dist_square(self, var1: list[float], var2: list[float]):
        """Get the euclidean distance of the input lists"""
        var3 = float(0.0)

        for var5 in range(self.num_vars):
            var3 += (var1[var5] - var2[var5]) * (var1[var5] - var2[var5])

        return var3

    def rbf_linear(self, var1: float) -> float:
        return self.norm - math.sqrt(var1)

    def rbf_cubic(self, var1: float) -> float:
        return self.norm_two - var1 * math.sqrt(var1)

    def rbf_thin_plate_spline(self, var1: float) -> float:
        return self.norm_two - var1 * math.log(1.0 + math.sqrt(var1))

    def rbf_gaussian(self, var1: float) -> float:
        return math.exp(-self.EPSILON * var1)

    def rbf_multiquadratic(self, var1: float) -> float:
        return math.sqrt(1.0 + var1)

    def rbf_inverse_multiquadratic(self, var1: float) -> float:
        return 1.0 / self.rbf_multiquadratic(var1)

    def rbf_compactly_supported_20(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 <= 1.0:
            var1 = var5 * var5
            var3 = (
                1.0 + 5.0 * var5 + 9.0 * var1 + 5.0 * var5 * var1 + var1 * var1
            )
            var3 *= math.pow(1.0 - var5, 5.0)

        return var3

    def rbf_compactly_supported_21(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 <= 1.0:
            var1 = var5 * var5
            var3 = 4.0 + 16.0 * var5 + 12.0 * var1 + 3.0 * var5 * var1
            var3 *= math.pow(1.0 - var5, 4.0)

        return var3

    def rbf_compactly_supported_22(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 < 1.0:
            var3 = 8.0 + 9.0 * var5 + 3.0 * var5 * var5
            var3 *= math.pow(1.0 - var5, 3.0)

        return var3

    def rbf_compactly_supported_30(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 <= 1.0:
            var1 = var5 * var5
            var7 = float(var5 * var1)
            var3 = (
                5.0
                + 35.0 * var5
                + 101.0 * var1
                + 147.0 * var7
                + 101.0 * var1 * var1
                + 35.0 * var1 * var7
                + 5.0 * var7 * var7
            )
            var3 *= math.pow(1.0 - var5, 7.0)

        return var3

    def rbf_compactly_supported_31(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 <= 1.0:
            var1 = var5 * var5
            var7 = float(var5 * var1)
            var3 = (
                6.0
                + 36.0 * var5
                + 82.0 * var1
                + 72.0 * var7
                + 30.0 * var1 * var1
                + 5.0 * var1 * var7
            )
            var3 *= math.pow(1.0 - var5, 6.0)

        return var3

    def rbf_compactly_supported_32(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 <= 1.0:
            var1 = var5 * var5
            var7 = float(var5 * var1)
            var3 = (
                8.0
                + 40.0 * var5
                + 48.0 * var1
                + 25.0 * var7
                + 5.0 * var1 * var1
            )
            var3 *= math.pow(1.0 - var5, 5.0)

        return var3

    def rbf_compactly_supported_33(self, var1: float) -> float:
        var3 = float(0.0)
        var5 = math.sqrt(var1) / self.norm

        if var5 <= 1.0:
            var1 = var5 * var5
            var7 = float(var5 * var1)
            var3 = 16.0 + 29.0 * var5 + 20.0 * var1 + 5.0 * var7
            var3 *= math.pow(1.0 - var5, 4.0)

        return var3

    def get_func_str(self) -> str:
        """Get the function string for the radial basis functions"""
        var1 = ""

        for var2 in range(self.num_points):
            if var2 > 0:
                var1 = f"{var1} + "  # removed \n here (after {var1}) so that these can be read into the formulation tab
            var1 = (
                f"{var1}{self.get_coeff_expr(var2)}*{self.get_rbf_expr(var2)}"
            )

        if self.poly_order > 0:
            var1 = f"{var1} + ({self.polynomial.get_func_str()})"  # removed \n here (after {var1}) so that these can be read into the formulation tab

        return var1

    def get_grad_expr(self, var1: int) -> str:
        """Get the expressions for the gradient functions"""
        var2 = ""
        for var3 in range(self.num_points):
            if var3 > 0:
                var2 = f"{var2}\n + "

            var4 = self.get_coeff_expr(var3)
            var5 = self.get_rbf_expr(var3)
            var6 = self.get_var_diff_expr(var1, var3)
            var7 = self.get_euclidean_dist_square_exp(var3)
            var8 = f"sqrt{var7}"
            var9 = f"(sqrt{var7}/{self.norm})"
            var2 = f"{var2}{var4}*"
            match self.rb_func:
                case 0:
                    var2 = f"{var2}(-{var6}/{var8})"
                case 1:
                    var2 = f"{var2}(-3*{var6}*{var8})"
                case 2:
                    var2 = f"{var2}(-(2*ln(1+{var8})+r/({var8}+1))*{var6})"
                case 3:
                    var2 = f"{var2}(-2*{var6}*{var5})"
                case 4:
                    var2 = f"{var2}({var6}/{var5})"
                case 5:
                    var2 = f"{var2}(-{var6}*{var5}^3)"
                case 6:
                    var2 = f"(-(1-{var9})^4*(12+48*{var9}+36*{var9}^2+9*{var9}^3)*{var6}/{self.norm_two})"
                case 7:
                    var2 = f"(-(1-{var9})^3*(56+63*{var9}+21*{var9}^2)*{var6}/{self.norm_two})"
                case 8:
                    var2 = f"(-15*(1-{var9}^2)^2*{var6}/({var8}*{self.norm}))"
                case 9:
                    var2 = f"(-(1-{var9})^6*(78+468*{var9}+1066*{var9}^2+936*{var9}^3+390*{var9}^4+65*{var9}^5)*{var6}/{self.norm_two})"
                case 10:
                    var2 = f"(-(1-{var9})^5*(88+440*{var9}+528*{var9}^2+275*{var9}^3+55*{var9}^4)*{var6}/{self.norm_two})"
                case 11:
                    var2 = f"(-(1-{var9})^4*(144+261*{var9}+180*{var9}^2+45*{var9}^3)*{var6}/{self.norm_two})"
                case 12:
                    var2 = f"(-35*(1-{var9}^2)^3*{var6}/({var8}*{self.norm}))"

        if self.poly_order > 0:
            var2 = f"{var2}\n + ({self.poly_grads[var1].get_func_str()})"

        return var2

    def get_coeff_expr(self, index: int) -> str:
        """Get the coefficient expression at the given index"""
        return (
            f"({self.coefficients[index]})"
        )

    def get_var_diff_expr(self, var1: int, var2: int) -> str:
        """Returns the string representation of the variable difference expression at the given column and row"""
        var3 = ""
        if self.matrix_vars[var2][var1] == 0.0:
            var3 = "-0"
        elif self.matrix_vars[var2][var1] < 0.0:
            var10000 = -self.matrix_vars[var2][var1]
            var3 = f"+{var10000}"
        else:
            var3 = f"-{self.matrix_vars[var2][var1]}"

        return f"(x{var1 + 1}{var3})"

    def get_euclidean_dist_square_exp(self, var1: int) -> str:
        """Returns a string with the euclidean square distance of the column indicated"""
        var10000 = self.get_var_diff_expr(0, var1)
        var2 = f"{var10000}^2"

        for var3 in range(1, self.num_vars):
            var2 = f"{var2} + {self.get_var_diff_expr(var3, var1)}^2"

        return f"({var2})"

    def get_rbf_expr(self, var1: int) -> str:
        """Return a string representative of the radial basis function"""
        var2 = ""
        var3 = self.get_euclidean_dist_square_exp(var1)
        var4 = f"(sqrt{var3})"
        var5 = f"(sqrt{var3}/{self.norm})"

        match self.rb_func:
            case 0:
                var2 = f"({self.norm} - {var4})"
            case 1:
                var2 = f"({self.norm_two} - {var3}*{var4})"
            case 2:
                var2 = f"({self.norm_two} -{var3}*ln(1+{var4}))"
            case 3:
                var2 = f"exp(-{self.EPSILON}*{var3})"
            case 4:
                var2 = f"sqrt({var3} + 1)"
            case 5:
                var2 = f"(1/sqrt({var3} + 1))"
            case 6:
                var2 = (
                    f"(1-{var5})^5*(1+5*{var5}+9*{var5}^2+5*{var5}^3+{var5}^4)"
                )
            case 7:
                var2 = f"(1-{var5})^4*(4+16*{var5}+12*{var5}^2+3*{var5}^3)"
            case 8:
                var2 = f"(1-{var5})^3*(8+9*{var5}+3*{var5}^2)"
            case 9:
                var2 = f"(1-{var5})^7*(5+35*{var5}+101*{var5}^2+147*{var5}^3+101*{var5}^4+35*{var5}^5+5*{var5}^6)"
            case 10:
                var2 = f"(1-{var5})^6*(6+36*{var5}+82*{var5}^2+72*{var5}^3+30*{var5}^4+5*{var5}^5)"
            case 11:
                var2 = f"(1-{var5})^5*(8+40*{var5}+48*{var5}^2+25*({var5}^3)+5*{var5}^4)"
            case 12:
                var2 = f"(1-{var5})^4*(16+29*{var5}+20*{var5}^2+5*{var5}^3)"

        return var2
