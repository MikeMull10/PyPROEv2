![Metamodeling Page](:/docs/imgs/metamodeling.png)
# Metamodeling

## Methods

1. Polynomial Regression
2. Radial Basis Function (RBF)

### Polynomial Regression
Creates a polynomial-based surrogate model that approximates the relationship between inputs and outputs using the following options:

- Linear Polynomial - Models the response as a linear combination of variables without curvature or interaction terms.

- Quadratic Polynomial with No Interaction - Includes squared terms to capture curvature while excluding cross-variable interaction effects.

- Quadratic Polynomial with Interaction - Includes squared terms and interaction terms to model both curvature and variable interactions.

Uses the following parameters:
- Variable Count - Determines the number of variables used by the metamodel.
- Function Count - Determines the number of response functions approximated by the metamodel.

---

### Radial Basis Function (RBF)
Creates a flexible, interpolation-based metamodel using radial basis functions to approximate complex, nonlinear responses.

Supported RBF types:
- Linear
- Cubic
- Thin Plate Spline
- Gaussian
- Multiquadratic
- Inversely Multiquadratic
- Compactly Supported (2,0)
- Compactly Supported (2,1)
- Compactly Supported (2,2)
- Compactly Supported (3,0)
- Compactly Supported (3,1)
- Compactly Supported (3,2)
- Compactly Supported (3,3)

Uses the following parameters:
- Variable Count - Determines the number of variables used by the metamodel.
- Function Count - Determines the number of response functions approximated by the metamodel.
- Polynomial Order - Determines the order of the polynomial tail added to the RBF model (0 for none, 1 for linear).
