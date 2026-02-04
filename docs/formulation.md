![Formulation Page](:/docs/imgs/formulation.png)

---

# Formulation
## Variables

The variables used in your equations.
- The Minimum and Maximum must be numbers (can use scientific notation). I.e. cannot be `π`, `1 + 1`, etc.
- Variable name can be anything, but variables are typically `X1`, `X2`, `X3`...

## Constants

Static versions of variables. These can include values like `π` or expressions like `1 + 1`, `sin(x1)`, etc.
- Variable name can be anything, but constants are typically `C1`, `C2`, `C3`...

## Functions

The equations used in your problem.
- Equation name can be anything, but functions are typically `F1`, `F2`, `F3`..., but can also use `Gx` or `Hx` for constraint functions.
- The equation part can include the following symbols and expressions:
  - Sin / Cos / Tan
  - Cot / Sec / Csc
  - Asin / Acos / Atan
  - Sinh / Cosh / Tanh
  - Asinh / Acosh / Atanh
  - exp
  - log
  - ln
  - sqrt
  - abs
  - sum
  - indexed sum (formatted as `iSum(<expression>, <index>, <start>, <end>)` i.e. `iSum(x[i], i, 1, 4)`, which is equivalent to `x1 + x2 + x3 + x4`)
  - pi
  - E
  - sign
  - min
  - max
  - Variables
  - Constants
  - Other Functions
- The equation must use explicit multiplication (i.e. `2 * X1` instead of `2X1`)

## Objectives

The objective function(s) (the solution(s) to your problem).
- Objective name can by anything, but objectives are typically `O1`, `O2`, `O3`...
- Objective function is typically one of the functions, but can also include expressions. I.e. `F1 * 3 + 2` is valid, but atypical.

## Equality Constraints

The constraint functions that have a set value. For a solution to be valid, the constraint function must EQUAL that value.
- Constraint name can by anything, but equaltity constraints are typically `EQ1`, `EQ2`, `EQ3`...
- Constraint function is typically one of the functions, but can also include expressions. I.e. `F1 * 3 + 2` is valid, but atypical.
- Constraint value is often `0`, but could be different based on the equation. I.e. for `F1 = 3`, you can use `F1` as the function and `3` as the value, or you could have `F1 - 3` as the function and `0` as the value.

## Inequality Constraints

The constraint functions that have a set threshold. For a solution to be valid, the constraint function must be LESS THAN OR EQUAL TO that threshold.
- Constraint name can by anything, but inequaltity constraints are typically `INEQ1`, `INEQ2`, `INEQ3`...
- Constraint function is typically one of the functions, but can also include expressions. I.e. `F1 * 3 + 2` is valid, but atypical.
- Constraint threshold is often `0`, but could be different based on the equation. I.e. for `F1 <= 3`, you can use `F1` as the function and `3` as the threshold, or you could have `F1 - 3` as the function and `0` as the threshold.