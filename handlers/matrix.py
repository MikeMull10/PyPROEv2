from __future__ import annotations
from handlers.errorhandler import ErrorHandler


class Matrix:
    """A class representing a matrix"""

    def __init__(
        self,
        var1: int | list[list[float]] | list[float] | "Matrix",
        var2: int | None = None,
        var3: float | None = None,
        handle_error: ErrorHandler=None,
    ) -> None:
        """
        Can be initialized with:
        - row/col dimensions
        - row/col dimensions with an initializer value
        - a 2D array
        - a 1D array
        - a Matrix object.
        """
        self.handle_error = handle_error
        if var2 != None:
            self.num_row = var1
            self.num_col = var2
            self.initialize(var3 if var3 != None else 0.0)

        else:
            try:
                self.num_row = var1.size_rows()
                self.num_col = var1.size_cols()
                self.a = var1.get_array()
            except:
                try:
                    self.num_row = len(var1)
                    self.num_col = len(var1[0])
                    self.a = var1
                except:
                    self.num_row = len(var1)
                    self.num_col = 1
                    self.a = [[i] for i in var1]

    def initialize(self, initVar: float) -> None:
        """Initialize the matrix with the given number

        Parameters
        ----------
        initVar : float
            The value to initialize all matrix values to
        """
        self.a = [
            [float(initVar) for _ in range(self.num_col)]
            for _ in range(self.num_row)
        ]

    def set_to_identity(self) -> None:
        """Set the all matrix values to 0, and set the diagonal values to 1.0"""
        self.initialize(0.0)

        for i in range(self.num_row):
            self.a[i][i] = 1.0

    def set_submatrix(
        self, matrix: "Matrix", row_start: int, col_start: int
    ) -> None:
        """Set a submatrix of A to the given matrix

        Parameters
        ----------
        matrix : Matrix
            The matrix to set as a submatrix of A
        row_start : int
            The starting row where the matrix should be copied in
        col_start : init
            The starting column where the matrix should be copied in
        """
        var4 = matrix.get_array()

        for var5 in range(matrix.size_rows()):
            for var6 in range(matrix.size_cols()):
                self.a[row_start + var5][col_start + var6] = var4[var5][var6]

    def copy(self, matrix: list[list[float]] | list[float] | "Matrix") -> None:
        """Copy the given matrix to matrix A"""

        if type(matrix) == "Matrix":
            self.copy(matrix.get_array())
        elif type(matrix[0]) == list:
            for var2 in range(self.num_row):
                for var3 in range(self.num_col):
                    self.a[var2][var3] = matrix[var2][var3]
        elif type(matrix[0]) == float:
            for var2 in range(self.num_row):
                self.a[var2][0] = matrix[var2]
        else:
            self.handle_error.gen_error(
                "Invalid paramater type passed to Matrix.copy. Expected"
                " list[list[float]], list[float], or Matrix.\t Received:"
                " {type(matrix)}"
            )

    def get_array(self) -> list[list[float]]:
        """Return matrix A as a nested array of values"""
        return self.a

    def set_array(self, vals: list[list[float]]) -> None:
        """Set matrix A to a nested array of values"""
        self.a = vals

    def get_row_vector(self, index: int) -> list[float]:
        """Returns the row vector of matrix A at the given index"""
        return self.a[index]

    def get_col_vector(self, index: int) -> list[float]:
        """Returns the column vector of matrix A at the given index"""
        return [i[index] for i in self.a]

    def plus(self, matrix: "Matrix") -> "Matrix":
        """Returns the sum of the given matrix added to the current matrix"""
        var2: Matrix = Matrix(
            self.num_row, self.num_col, handle_error=self.handle_error
        )
        var3: list[list[float]] = var2.get_array()
        var4: list[list[float]] = matrix.get_array()

        for var5 in range(self.num_row):
            for var6 in range(self.num_col):
                var3[var5][var6] = self.a[var5][var6] + var4[var5][var6]

        var2.set_array(var3)
        return var2

    def minus(self, matrix: "Matrix") -> "Matrix":
        """Returns the difference of the given matrix subtracted from the current matrix"""
        var2: Matrix = Matrix(
            self.num_row, self.num_col, handle_error=self.handle_error
        )
        var3: list[list[float]] = var2.get_array()
        var4: list[list[float]] = matrix.get_array()

        for var5 in range(self.num_row):
            for var6 in range(self.num_col):
                var3[var5][var6] = self.a[var5][var6] - var4[var5][var6]

        var2.set_array(var3)
        return var2

    def times(self, matrix: "Matrix") -> "Matrix":
        """Multiplies the given matrix with the current matrix"""
        var2: Matrix = Matrix(
            self.size_rows(), matrix.size_cols(), handle_error=self.handle_error
        )
        var3: list[list[float]] = var2.get_array()
        var4: list[list[float]] = matrix.get_array()

        for var5 in range(self.size_rows()):
            for var6 in range(matrix.size_cols()):
                var3[var5][var6] = 0.0

                for var7 in range(matrix.size_rows()):
                    var3[var5][var6] += self.a[var5][var7] * var4[var7][var6]

        var2.set_array(var3)
        return var2

    def transpose(self) -> "Matrix":
        """Return a transposed version of the current matrix"""
        var1 = Matrix(
            self.num_col, self.num_row, handle_error=self.handle_error
        )
        var2 = var1.get_array()

        for var3 in range(self.num_col):
            for var4 in range(self.num_row):
                var2[var3][var4] = self.a[var4][var3]

        var1.set_array(var2)
        return var1

    def inverse(self) -> "Matrix":
        """Invert and return the given matrix"""
        var1: LDLTSolver = LDLTSolver(
            Matrix(self.a, handle_error=self.handle_error), self.handle_error
        )
        var2 = Matrix(
            self.num_row, self.num_col, handle_error=self.handle_error
        )
        var2.set_to_identity()
        return var1.solve(var2)

    def get(self, row: int, col: int) -> float:
        """Return the value in matrix A at the given row and column"""
        return self.a[row][col]

    def set(self, row: int, col: int, value: float) -> None:
        """Set a value in matrix A at given row and column"""
        self.a[row][col] = value

    def size_rows(self) -> int:
        """Returns the number of rows in the matrix"""
        return self.num_row

    def size_cols(self) -> int:
        """Returns the number of columns in the matrix"""
        return self.num_col

    def print(self) -> None:
        """Print the current matrix to the console"""
        self.handle_error.gen_error(
            f"Matrix A[{self.num_row}][{self.num_col}]                         "
            " \n--------------------------------------------------\n          "
            f"                {self.get_matrix_string()}"
        )

    def get_matrix_string(self) -> str:
        """Returns a string representative of the current matrix values"""
        var1 = ""

        for var2 in range(self.num_row):
            for var3 in range(self.num_col):
                var1 = f"{var1}\t{self.a[var2][var3]}"
            var1 = f"{var1}\n"

        return var1
    
    def __str__(self):
        return self.a


class LDLTSolver:
    """LDL^T (Cholesky) matrix decomposition class"""

    def __init__(self, matrix: Matrix, handle_error: ErrorHandler=None):
        self.A = None
        self.LDLT = None
        self.handle_error = handle_error

        if matrix.size_rows() != matrix.size_cols():
            self.handle_error.gen_error("LDLT solver requires a square matrix.")
        else:
            self.A = Matrix(matrix, handle_error=self.handle_error)
            self.LDLT = self.A.get_array()
            self.decompose()

    def decompose(self) -> None:
        """Decompose the matrix"""
        if self.A != None:
            var1 = self.A.size_rows()

            for var2 in range(var1):
                var10000 = []

                for var3 in range(var2):
                    var10000 = self.LDLT[var2]
                    var10000[var2] -= (
                        self.LDLT[var2][var3]
                        * self.LDLT[var2][var3]
                        * self.LDLT[var3][var3]
                    )

                for var3 in range(var2 + 1, var1):
                    for var4 in range(var2):
                        var10000 = self.LDLT[var3]
                        var10000[var2] -= (
                            self.LDLT[var3][var4]
                            * self.LDLT[var2][var4]
                            * self.LDLT[var4][var4]
                        )

                    var10000 = self.LDLT[var3]
                    var10000[var2] = self.zero_division_nan(
                        var10000[var2], self.LDLT[var2][var2]
                    )

    def solve(self, matrix: Matrix) -> Matrix:
        """Solve and return the given matrix"""
        if self.A == None:
            return None
        else:
            var2 = self.A.size_rows()
            var3 = Matrix(matrix, handle_error=self.handle_error)
            var4: list[list[float]] = var3.get_array()

            for var5 in range(var3.size_cols()):
                for var6 in range(var2):
                    for var7 in range(var6):
                        var4[var6][var5] -= (
                            self.LDLT[var6][var7] * var4[var7][var5]
                        )

                for var6 in range(var2 - 1, -1, -1):
                    for var7 in range(var6 + 1, var2):
                        var4[var6][var5] -= (
                            self.LDLT[var6][var6]
                            * self.LDLT[var7][var6]
                            * var4[var7][var5]
                        )

                    # in Java, 0 division by floats is acceptable, but not for Python
                    try:
                        var4[var6][var5] /= self.LDLT[var6][var6]
                    except:
                        pass

            # var3.set_array(var4)
            return var3

    def zero_division_nan(self, var1: float, var2: float) -> float:
        """Divide the first number by the second, and if the second is a 0, return NAN
        (For context, the original Java this was translated from did this automatically.)
        """
        try:
            return var1 / var2
        except:
            return float("nan")
    
    def __str__(self):
        return self.A
