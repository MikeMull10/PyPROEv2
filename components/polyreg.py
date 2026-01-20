from scipy.stats import f
import numpy as np
import itertools

from enum import Enum

# Generate linear regression
def linear_regression(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]

# Generate polynomial and interaction terms for any number of variables
def generate_polynomial_features(X):
    n_samples, n_features = X.shape
    
    # Start with an intercept (column of ones)
    features = [np.ones(n_samples)]  # Intercept term
    
    # Add linear terms
    features.extend([X[:, i] for i in range(n_features)])
    
    # Add quadratic terms (x_i^2)
    features.extend([X[:, i]**2 for i in range(n_features)])
    
    # Add interaction terms (x_i * x_j for i != j)
    for i, j in itertools.combinations(range(n_features), 2):
        features.append(X[:, i] * X[:, j])
    
    # Stack features column-wise to form the expanded feature matrix
    return np.column_stack(features)

# Perform polynomial regression
def polynomial_regression(X, y) -> np.ndarray:
    # Generate polynomial features (linear, quadratic, and interaction terms)
    X_expanded = generate_polynomial_features(X)
    
    # Solve for the coefficients using the normal equation
    B = np.linalg.inv(X_expanded.T @ X_expanded) @ X_expanded.T @ y
    return B

# Define a prediction function based on the coefficients
def predict_polynomial(X, B) -> np.ndarray:
    X_expanded = generate_polynomial_features(X)
    return X_expanded @ B

# Generate polynomial and interaction terms labels for any number of variables
def generate_term_labels(n_features, with_interaction: bool=True, variable_names: list[str] | None = None) -> list[str]:
    # List to hold the labels for each term
    labels = ["1"]  # Intercept term (constant)

    names = [(variable_names[i] if variable_names else f"X{i + 1}") for i in range(n_features)]
    
    # Linear terms
    labels.extend(names)
    
    # Quadratic terms (x_i^2)
    labels.extend([f"{name}^2" for name in names])
    
    # Interaction terms (x_i * x_j for i != j)
    if with_interaction:
        for i, j in itertools.combinations(range(n_features), 2):
            labels.append(f"{names[i]} * {names[j]}")
    
    return labels

# Function to convert coefficients to an equation string
def coefficients_to_equation(B, n_features, variable_names: list[str] | None = None) -> str:
    # Generate labels for the terms
    term_labels = generate_term_labels(n_features, variable_names)
    
    # Create a list of terms like 'B0 * 1', 'B1 * x1', etc.
    equation_terms = []
    for i, b in enumerate(B):
        # Add the coefficient and the respective term
        if b != 0:  # Skip terms where the coefficient is zero
            if term_labels[i] == "1":
                equation_terms.append(f"{b}")
            else:
                equation_terms.append(f"{b} * {term_labels[i]}")
    
    # Join all the terms together with ' + ' in between
    equation = " + ".join(equation_terms)
    return equation

# Generate polynomial (linear and quadratic) terms for any number of variables without interaction
def generate_polynomial_features_no_interaction(X) -> np.ndarray:
    n_samples, n_features = X.shape
    
    # Start with an intercept (column of ones)
    features = [np.ones(n_samples)]  # Intercept term
    
    # Add linear terms
    features.extend([X[:, i] for i in range(n_features)])
    
    # Add quadratic terms (x_i^2)
    features.extend([X[:, i]**2 for i in range(n_features)])
    
    # Stack features column-wise to form the expanded feature matrix
    return np.column_stack(features)

# Perform polynomial regression without interaction terms
def polynomial_regression_no_interaction(X, y) -> np.ndarray:
    # Generate polynomial features (linear and quadratic terms, no interaction)
    X_expanded = generate_polynomial_features_no_interaction(X)
    
    # Solve for the coefficients using the normal equation
    B = np.linalg.inv(X_expanded.T @ X_expanded) @ X_expanded.T @ y
    return B

# Convert coefficients to a polynomial equation string (no interaction)
def coefficients_to_equation_no_interaction(B, n_features, variable_names: list[str] | None = None) -> str:
    # Generate labels for the terms
    term_labels = generate_term_labels(n_features, with_interaction=False, variable_names=variable_names)
    
    # Create a list of terms like 'B0 * 1', 'B1 * x1', etc.
    equation_terms = []
    for i, b in enumerate(B):
        # Add the coefficient and the respective term
        if b != 0:  # Skip terms where the coefficient is zero
            if term_labels[i] == "1":
                equation_terms.append(f"{b}")
            else:
                equation_terms.append(f"{b} * {term_labels[i]}")
    
    # Join all the terms together with ' + ' in between
    equation = " + ".join(equation_terms)
    return equation

def do_linear_regression(independent: np.ndarray, dependent: np.ndarray, variable_names: list[str] | None = None) -> list[str]:
    results: list[str] = []

    X = np.column_stack((
        np.ones(independent.shape[0]),
        independent
    ))

    for dep_idx in range(dependent.shape[1]):
        y = dependent[:, dep_idx]
        B = linear_regression(X, y)

        terms = [f"{B[0]}"]
        for coef_idx in range(1, len(B)):
            name = (
                variable_names[coef_idx - 1]
                if variable_names
                else f"X{coef_idx}"
            )
            terms.append(f"{B[coef_idx]} * {name}")

        results.append(" + ".join(terms))

    return results

def do_quad_int(independent: np.ndarray, dependent: np.ndarray, variable_names: list[str] | None = None) -> list[str]:
    ret: list[str] = []

    for i in range(dependent.shape[1]):
        B = polynomial_regression(independent, dependent[:, i])
        ret.append(coefficients_to_equation(B, independent.shape[1], variable_names))
    
    return ret

def do_quad_no_int(independent: np.ndarray, dependent: np.ndarray, variable_names: list[str] | None = None) -> list[str]:
    ret: list[str] = []

    for i in range(dependent.shape[1]):
        B = polynomial_regression_no_interaction(independent, dependent[:, i])
        ret.append(coefficients_to_equation_no_interaction(B, independent.shape[1], variable_names))
    
    return ret

def calculate_statistics(X, y, y_pred) -> dict:
        # Number of data points and predictors
        n = len(y)
        p = X.shape[1] - 1  # Excluding the intercept

        # Residuals
        residuals = y - y_pred
        
        # Total sum of squares
        y_mean = np.mean(y)
        SS_tot = np.sum((y - y_mean) ** 2)
        
        # Residual sum of squares
        SS_res = np.sum(residuals ** 2)
        
        # R-squared
        R2 = 1 - (SS_res / SS_tot)
        
        # Adjusted R-squared
        R2_adj = 1 - ((SS_res / (n - p - 1)) / (SS_tot / (n - 1)))
        
        # RMSE
        RMSE = np.sqrt(SS_res / (n - p - 1))
        
        # F-statistic
        F_stat = ((SS_tot - SS_res) / p) / (SS_res / (n - p - 1))
        
        # p-value for F-statistic
        p_value = f.sf(F_stat, p, n - p - 1)
        
        # PRESS (Leave-one-out cross-validation)
        H = X @ np.linalg.inv(X.T @ X) @ X.T  # Hat matrix
        PRESS = np.sum((residuals / (1 - np.diag(H))) ** 2)
        
        # R2press
        R2_press = 1 - (PRESS / SS_tot)
        
        return {
            'F-statistic': F_stat,
            'p-value': p_value,
            'R2': R2,
            'R2_adj': R2_adj,
            'RMSE': RMSE,
            'PRESS': PRESS,
            'R2_press': R2_press
        }


class PolyTypes(Enum):
    LINEAR = 0
    QUAD_NO_INT = 1
    QUAD_INT = 2

poly_lookup: dict[PolyTypes, callable] = {
    PolyTypes.LINEAR: do_linear_regression,
    PolyTypes.QUAD_NO_INT: do_quad_no_int,
    PolyTypes.QUAD_INT: do_quad_int
}

def get_Ypred(independent, dependent, poly_type):
    match poly_type:
        case PolyTypes.LINEAR:
            X = np.column_stack([
                np.ones(independent.shape[0]),
                *[independent[:, i] for i in range(independent.shape[1])]
            ])
            B = linear_regression(X, dependent)

        case PolyTypes.QUAD_NO_INT:
            X = generate_polynomial_features_no_interaction(independent)
            B = polynomial_regression_no_interaction(independent, dependent)

        case PolyTypes.QUAD_INT:
            X = generate_polynomial_features(independent)
            B = polynomial_regression(independent, dependent)

        case _:
            return None, None

    return X, X @ B