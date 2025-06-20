import math


class Statistics:
    def __init__(
        self,
        var1: list[list[float]],
        var2: list[float],
        var3,
        var4: list[float],
    ):
        """Initialize RBF statistics

        Parameters
        ----------
        var1 : list[list[float]]
            The array form of a variable matrix
        var2 : list[float]
            A column vector of a function matrix
        var3 : FullPolynomial | OrthogonalPolynomial | PR | RadialBasisFunction,
            The function these statistics are about
        var4 : list[float]
            The hii matrix
        """
        self.FValue = -1.0
        self.PValue = -1.0
        self.R2 = -1.0
        self.R2adj = -1.0
        self.RMSE = -1.0
        self.PRESS = -1.0
        self.R2press = -1.0

        var5 = len(var1)
        var6 = len(var1[0])
        var7 = var3.get_num_terms() - 1

        if var5 == len(var2) and var6 == var3.get_num_vars():
            var8 = float(0.0)
            var10 = float(0.0)
            var12 = float(0.0)
            var14 = float(0.0)
            var16 = float(0.0)
            self.PRESS = float(0.0)

            for var18 in range(var5):
                var12 += var2[var18]
                var16 += var2[var18] * var2[var18]
                var8 = var3.get_func_value(var1[var18])
                var10 = (var2[var18] - var8) * (var2[var18] - var8)
                self.PRESS += self.zero_division_nan(
                    var10, ((1.0 - var4[var18]) * (1.0 - var4[var18]))
                )
                var14 += var10
            var16 -= self.zero_division_nan(var12 * var12, float(var5))
            self.FValue = self.zero_division_nan(
                self.zero_division_nan((var16 - var14), float(var7)),
                self.zero_division_nan(var14, float(var5 - var7 - 1)),
            )
            self.R2 = 1.0 - self.zero_division_nan(var14, var16)
            self.R2adj = 1.0 - float(
                self.zero_division_nan(
                   ((var5 - 1) * (1.0 - self.R2)), float(var5 - var7 - 1)
                )
            )
            self.RMSE = math.sqrt(
                self.zero_division_nan(var14, float(var5 - var7 - 1))
            )
            self.calc_prob(self.FValue, var7, var5 - var7 - 1)
            self.R2press = 1.0 - self.zero_division_nan(self.PRESS, var16)

    def calc_prob(self, var1: float, var3: int, var4: int) -> None:
        """Calculates the probability"""
        var5 = self.zero_division_nan(
            float(var4), (float(var4) + float(var3) * var1)
        )
        self.PValue = self.beta(var4, var3, var5)

    def beta(self, var1: int, var2: int, var3: float) -> float:
        """Calculates the beta value"""
        print(var3)
        var13 = math.sqrt(1.0 - var3)
        var11 = math.sqrt(var3)
        var6 = 2 * (var2 / 2) - var2 + 2
        var7 = 2 * (var1 / 2) - var1 + 2
        var9 = None
        var15 = None
        if var6 > 1:
            if var7 > 1:
                var9 = var3
                var15 = var3 * (1.0 - var3)
            else:
                var9 = var11
                var15 = (1.0 - var3) * var11 / 2.0
        elif var7 > 1:
            var9 = 1.0 - var13
            var15 = var13 * var3 / 2.0
        else:
            var9 = 1.0 - 0.6366197724 * math.atan(
                self.zero_division_nan(var13, var11)
            )
            var15 = 0.3183098862 * var13 * var11

        var8 = var7

        for var5 in range(int(var7), var1 + 1, 2):
            var8 = var5
            if var5 >= var1:
                break

            var9 -= self.zero_division_nan(2.0 * var15, float(var5))
            var15 = (
                self.zero_division_nan(var15 * var3 * float(var6 + var5), float(var5))
            )

        for var5 in range(int(var6), var2, 2):
            var9 += self.zero_division_nan(2.0 * var15, float(var5))
            var15 = (
                self.zero_division_nan(var15 * (1.0 - var3) * float(var5 + var8), float(var5))
            )

        var10000 = self.zero_division_nan(var15, (var3 * (1.0 - var3)))
        return var9

    def get_stats(self) -> str:
        """Return a string of statistics"""
        var3 = ""
        var3 = f"{var3}        F       = {self.get_fvalue()}\n"
        var1 = self.get_pvalue()
        opt1 = "        Pr>F    < 0.0001\n"
        var3 = (
            f"{var3}{(opt1 if var1 < float(0.0001) else '        Pr>F    = ')}{var1}\n"
        )
        var3 = (
            f"{var3}        R2      = {self.get_r2()}            \n       "
            f" R2adj   = {self.get_r2adj()}            \n        RMSE    ="
            f" {self.get_rsme()}            \n        PRESS   ="
            f" {self.get_press()}            \n        R2press ="
            f" {self.get_r2press()}\n"
        )
        return var3

    def get_fvalue(self) -> float:
        """Returns the f-value"""
        return self.FValue

    def get_pvalue(self) -> float:
        """Returns the p-value"""
        return self.PValue

    def get_r2(self) -> float:
        """Returns the R2 value"""
        return self.R2

    def get_r2adj(self) -> float:
        """Returns the R2 adj value"""
        return self.R2adj

    def get_rsme(self) -> float:
        """Returns the root mean squared error"""
        return self.RMSE

    def get_press(self) -> float:
        """Returns the PRESS value"""
        return self.PRESS

    def get_r2press(self) -> float:
        """Returns the R2 press value"""
        return self.R2press

    def zero_division_nan(self, num1: float, num2: float) -> float:
        """Try to divide num1 by num2, if num2 is 0, return positive or negative infinity"""
        try:
            return num1 / num2
        except:
            return float("inf") if num1 > 0 else float("-inf")
