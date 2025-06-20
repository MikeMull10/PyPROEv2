import math


class OrthogonalPolynomial:
    """A class representing orthogonal polynomials"""

    def __init__(self, order: int, num_vars: int, handle_error: None):
        """Initialize an orthogonal polynomial

        Parameters
        ----------
        order : int
            The order of the polynomial
        num_vars : int
            The number of variables in the polynomial
        """
        self.EPSILON = float(0.00000001)
        self.order: int = order
        self.num_vars: int = num_vars
        self.is_roundoff_on = False
        self.round_off: float = None
        self.handle_error = handle_error

        if self.order >= 0 and self.num_vars > 0:
            self.num_terms = self.order * self.num_vars + 1
            self.coefficients = [float(0.0) for _ in range(self.num_terms)]
        else:
            self.order = 0
            self.num_terms = 0
            self.num_vars = 0
            self.coefficients = None

    def get_func_value(self, values: list[float]) -> float:
        """Evaluate the function total with a list of values

        Parameters
        ----------
        values : list[float]
            The values to use for each variable in the polynomial
        """
        total: float = float(0.0)
        if len(values) < self.num_vars:
            self.handle_error(
                f"ERROR: this polynomial has {self.num_vars} variables.\n\t"
                f" {len(values)} variables are given"
            )
        else:
            for term in range(self.num_terms):
                total += self.coefficients[term] * self.get_func_value_at(
                    values, term
                )

        if self.is_roundoff_on and math.abs(total) < self.round_off:
            total = float(0.0)

        return total

    def get_func_value_at(self, values: list[float], term: int) -> float:
        """Evaluate a function term with a list of values

        Parameters
        ----------
        values : list[float]
            The values to use for the term in the polynomial
        term : int
            The term in the function to evaluate
        """

        value: float = float(0.0)
        if self.num_terms != 0 and len(values) >= self.num_vars:
            if term == 0:
                value = 1.0
            else:
                var5 = (term - 1) % self.num_vars
                var6 = (term - 1) / self.num_vars + 1

                value = pow(values[var5], float(var6))
        else:
            self.handle_error(
                f"ERROR: this polynomial has {self.num_vars} variables.\n\t"
                f" {len(values)} variables are given"
            )

        if self.is_roundoff_on and math.abs(value) < self.round_off:
            value = 0.0

        return value

    def get_gradients(self) -> list["OrthogonalPolynomial"]:
        """Returns a list of gradients for the function"""
        grads: list[OrthogonalPolynomial] = []
        var2 = max(0, (self.order - 1) * self.num_vars + 1)

        var3: list[float] = [0 for _ in range(var2)]

        for var4 in range(self.num_vars):
            var5 = 0

            for var6 in range(self.num_terms):
                var7 = (var6 - 1) % self.num_vars
                var8 = (var6 - 1) / self.num_vars + 1
                if var6 == 0:
                    var3[var5] = float(0.0)
                elif var8 == 1:
                    if var7 == var4:
                        var10001 = var5 + 1
                        var3[var10001] += self.coefficients[var6]
                else:
                    var3[var5 + 1] = (
                        self.coefficients[var6] * float(var8)
                        if var7 == var4
                        else float(0.0)
                    )

            newOrth = OrthogonalPolynomial(
                self.order - 1, self.num_vars, self.handle_error
            )
            newOrth.set_coefficients(var3)
            grads.append(newOrth)

        return grads

    def get_coefficients(self) -> list[float]:
        """Returns the coefficients for the polynomial"""
        return self.coefficients

    def set_coefficients(
        self, coeffs: list[float], start: int | None = None
    ) -> None:
        """Sets the coefficients for the polynomial

        Parameters
        ----------
        coeffs : list[float]
            The coefficients for the polynomial
        start : int | None
            The coefficient index to start copying from
        """
        if start == None:
            if self.num_terms != 0 and len(coeffs) >= self.num_terms:
                for i in range(self.num_terms):
                    self.coefficients[i] = coeffs[i]
            else:
                self.handle_error(
                    f"ERROR: this polynomial has {self.num_terms} terms.\n\t"
                    f" {len(coeffs)} coefficients are given"
                )
        else:
            if (
                self.num_terms != 0
                and len(coeffs) - start + 1 >= self.num_terms
            ):
                for i in range(self.num_terms):
                    self.coefficients[i] = coeffs[start + i]
            else:
                self.handle_error(
                    f"ERROR: this polynomial has {self.num_terms} terms.\n\t"
                    f" {len(coeffs)} coefficients are given"
                )

    def get_func_str(self) -> str:
        """Generate and return a function string for the polynomial"""
        var1 = ""

        for var3 in range(self.num_terms):
            if self.coefficients[var3] != 0.0:
                var10000 = float(0)
                var2 = ""
                if self.coefficients[var3] < 0.0:
                    var10000 = self.coefficients[var3]
                    var2 = f" - {-var10000}"
                else:
                    var10000 = self.coefficients[var3]
                    var2 = f" + {var10000}"

                if var3 > 0:
                    var4 = (var3 - 1) % self.num_vars
                    var5 = (var3 - 1) / self.num_vars + 1

                    var2 = f"{var2}*x{var4 + 1}"
                    if var5 != 1:
                        var2 = f"{var2}^{var5}"

                var1 = f"{var1}{var2}"

        return var1

    def get_order(self) -> int:
        """Return the order of the polynomial"""
        return self.order

    def get_num_terms(self) -> int:
        """Return the number of terms in the polynomial"""
        return self.num_terms

    def get_num_vars(self) -> int:
        """Return the number of variables in the polynomial"""
        return self.num_vars

    def set_roundoff(
        self, round: bool | float, precision: float = None
    ) -> None:
        """Set the roundoff precision for the function evaluations"""
        if type(round) == bool and type(precision) == None:
            self.set_roundoff(round, float(0.00000001))
        elif type(round) == float:
            self.set_roundoff(True, round)
        else:
            self.is_roundoff_on = round
            self.round_off = precision
