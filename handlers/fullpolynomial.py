import math


class FullPolynomial:
    """A class representing a polynomial and is associated operations"""

    def __init__(
        self,
        poly_orders: int | list[list[int]],
        num_vars: int | None = None,
        handle_error=None,
    ) -> None:
        """
        Parameters
        ----------
        poly_order : int | list[list[int]]
            The order of the polynomial function
        num_vars: int | None
            The number of variables in the polynomial function
        """
        self.EPSILON = float(0.00000001)
        self.num_terms: int = 0
        self.num_vars: int = 0
        self.term_orders: list[list[int]] = []
        self.coefficients: list[float] = []
        self.round_off: float = None
        self.handle_error = handle_error

        # initialize the polynomial with the provided number of variables
        if num_vars != None:
            self.is_roundoff_on: bool = False
            self.order = poly_orders
            self.num_vars = num_vars

            if self.order > 0 and self.num_vars > 0:
                var4 = [None for _ in range(self.num_vars)]
                var3 = self.get_var_orders([], var4, self.order, 0)

                self.num_terms = len(var3)
                self.coefficients = [float(0) for _ in range(self.num_terms)]
                self.term_orders = [[] for _ in range(self.num_terms)]

                for i in range(0, self.num_terms):
                    self.term_orders[i] = var3[i]
                    self.coefficients[i] = 0.0

            else:
                self.order = 0
                self.num_terms = 1
                self.coefficients = [float(1)]
                self.term_orders = [[0]]
        else:
            # initialize the polynomial if no variable count is given
            self.num_terms = len(poly_orders)
            self.num_vars = len(poly_orders[0])
            self.term_orders = [
                [0 for _ in range(self.num_vars)] for _ in range(self.num_terms)
            ]
            self.coefficients = [float(0) for _ in range(self.num_terms)]
            self.order = 0

            for i in range(self.num_terms):
                var3 = 0

                for j in range(self.num_vars):
                    self.term_orders[i][j] = poly_orders[i][j]
                    var3 += self.term_orders[i][j]

                if var3 > self.order:
                    self.order = var3

    def get_func_value(self, vars: list[float]) -> float:
        """Get a function value with the provided variable values

        Parameters
        ----------
        vars : list[float]
            The variable values to evalute the function with
        """
        total = 0.0
        if len(vars) < self.num_vars:
            self.handle_error(
                "ERROR: this polynomial has"
                f" {self.num_vars} variables.\n\t{len(vars)} variables are"
                " given."
            )
        else:
            for i in range(0, self.num_terms):
                total += self.coefficients[i] * self.get_func_value_at(vars, i)

        if self.is_roundoff_on and abs(total) < self.round_off:
            total = 0.0

        return total

    def get_func_value_at(self, vars: list[float], term_index: int) -> float:
        """Get a function value with the provided variable values

        Parameters
        ----------
        vars : list[float]
            The variable values to evalute the function with
        """
        total = 0.0
        if self.num_terms != 0 and len(vars) >= self.num_vars:
            if self.num_terms != 1 and term_index < self.num_terms:
                total = 1.0

                for i in range(0, self.num_vars):
                    total *= math.pow(
                        vars[i], float(self.term_orders[term_index][i])
                    )
            else:
                total = 0.0
        else:
            self.handle_error(
                "ERROR: this polynomial has"
                f" {self.num_vars} variables.\n\t{len(vars)} variables are"
                " given."
            )

        if self.is_roundoff_on and math.abs(total) < self.round_off:
            total = 0.0

        return total

    def get_gradients(self) -> list["FullPolynomial"]:
        """Calculate the gradients for the polynomial"""

        grads: list[FullPolynomial] = [0 for _ in range(self.num_vars)]
        var2: list[list[int]] = [
            [0 for _ in range(self.num_vars)] for _ in range(self.num_terms)
        ]
        coeffs: list[float] = [0 for _ in range(self.num_terms)]
        var7 = 0

        for var4 in range(0, self.num_vars):
            for var5 in range(0, self.num_terms):
                coeffs[var5] = self.coefficients[var5]

                for var6 in range(0, self.num_vars):
                    var2[var5][var6] = self.term_orders[var5][var6]
                    if var6 == var4:
                        if var2[var5][var6] == 0:
                            coeffs[var5] = 0.0

                            if var7 >= self.num_vars:
                                continue
                            else:
                                var2[var5][var7] = 0
                                var7 += 1

                    if var7 >= self.num_vars:
                        continue
                    else:
                        coeffs[var5] *= float(var2[var5][var6])
            if var7 >= self.num_vars:
                poly = FullPolynomial(var2, handle_error=self.handle_error)
                poly.set_coefficients(coeffs)
                grads[var4] = poly

        return grads

    def get_coefficients(self) -> list[float]:
        """Returns the coefficients for the polynomial"""
        return self.coefficients

    def set_coefficients(self, coeffs: list[float], start: int = None) -> None:
        """Set the coefficients for the polynomial

        Parameters
        ----------
        coeffs : list[float]
            The coefficients for the polynomial
        points: int | None
            The number of points in the polynomial
        """
        if start != None and (
            self.num_terms != 0 and len(coeffs) - start + 1 >= self.num_terms
        ):
            for i in range(self.num_terms):
                self.coefficients[i] = coeffs[start + i]
        elif (
            start == None
            and self.num_terms != 0
            and len(coeffs) >= self.num_terms
        ):
            for pt in range(self.num_terms):
                self.coefficients[pt] = coeffs[pt]
        else:
            self.handle_error(
                "ERROR: this polynomial has"
                f" {self.num_terms} terms.\n\t{len(coeffs)} coefficients are"
                " given. "
            )

    def get_func_str(self) -> str:
        """Generate the function string for the polynomial"""
        funcstr = ""
        termstr = ""

        for i in range(self.num_terms):
            if (float(self.coefficients[i]) == 0.0):
                continue
            else:
                if (self.coefficients[i] < 0):
                    termstr = f" - {- self.coefficients[i]}"
                else:
                    termstr = f" + {self.coefficients[i]}"
                
                if self.num_terms > 1:
                    for j in range(self.num_vars):
                        if self.term_orders[i][j] == 1:
                            termstr += f"*x{j + 1}"
                        elif self.term_orders[i][j] > 1:
                            termstr += f"*x{j + 1}^{self.term_orders[i][j]}"
                
                funcstr += termstr
        return funcstr

    def get_order(self) -> int:
        """Returns the order of the polynomial"""
        return self.order

    def get_num_terms(self) -> int:
        """Returns the number of terms in the polynomial"""
        return self.num_terms

    def get_num_vars(self) -> int:
        """Returns the number of variables in the polynomial"""
        return self.num_vars

    def set_roundoff(
        self, roundoff: bool | float, precision: float | None = None
    ) -> None:

        if type(roundoff) == bool and precision == None:
            self.set_roundoff(roundoff, float(0.00000001))
        elif type(roundoff) == float:
            self.set_roundoff(True, roundoff)
        else:
            self.is_roundoff_on = roundoff
            self.round_off = precision

    def get_var_orders(
        self, terms: list[list[int]], var_orders: list[int], order: int, i_var: int
    ) -> list[list[int]]:
        """Returns the order of variables

        Parameters
        ----------
        These parameters exist, but I'm not fully sure what each one does.
        """
        for i in range(order + 1):
            var_orders[i_var] = i
            if (i_var == (self.num_vars - 1)): # last variable
                var_order_copy = [var_orders[j] for j in range(self.num_vars)]
                terms.append(var_order_copy)
            else:
                self.get_var_orders(terms, var_orders, order - i, i_var + 1)
    
        return terms