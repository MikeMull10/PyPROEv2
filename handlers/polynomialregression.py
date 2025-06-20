from handlers.gradmanager import GradientManager
from handlers.inputfnc import clean, create_function_from_string
from handlers.doefile import DOEFile
from scipy.stats import f
import numpy as np
import itertools

# Generate linear regression
def linear_regression(X, y):
    return np.linalg.inv(X.T @ X) @ X.T @ y

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
def polynomial_regression(X, y):
    # Generate polynomial features (linear, quadratic, and interaction terms)
    X_expanded = generate_polynomial_features(X)
    
    # Solve for the coefficients using the normal equation
    B = np.linalg.inv(X_expanded.T @ X_expanded) @ X_expanded.T @ y
    return B

# Define a prediction function based on the coefficients
def predict_polynomial(X, B):
    X_expanded = generate_polynomial_features(X)
    return X_expanded @ B

# Generate polynomial and interaction terms labels for any number of variables
def generate_term_labels(n_features):
    # List to hold the labels for each term
    labels = ["1"]  # Intercept term (constant)
    
    # Linear terms
    labels.extend([f"x{i+1}" for i in range(n_features)])
    
    # Quadratic terms (x_i^2)
    labels.extend([f"x{i+1}^2" for i in range(n_features)])
    
    # Interaction terms (x_i * x_j for i != j)
    for i, j in itertools.combinations(range(n_features), 2):
        labels.append(f"x{i+1}*x{j+1}")
    
    return labels

# Function to convert coefficients to an equation string
def coefficients_to_equation(B, n_features):
    # Generate labels for the terms
    term_labels = generate_term_labels(n_features)
    
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
def generate_polynomial_features_no_interaction(X):
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
def polynomial_regression_no_interaction(X, y):
    # Generate polynomial features (linear and quadratic terms, no interaction)
    X_expanded = generate_polynomial_features_no_interaction(X)
    
    # Solve for the coefficients using the normal equation
    B = np.linalg.inv(X_expanded.T @ X_expanded) @ X_expanded.T @ y
    return B

# Function to generate term labels for quadratic regression without interaction
def generate_term_labels_no_interaction(n_features):
    labels = ["1"]  # Intercept term
    labels.extend([f"x{i+1}" for i in range(n_features)])  # Linear terms
    labels.extend([f"x{i+1}^2" for i in range(n_features)])  # Quadratic terms
    return labels

# Convert coefficients to a polynomial equation string (no interaction)
def coefficients_to_equation_no_interaction(B, n_features):
    # Generate labels for the terms
    term_labels = generate_term_labels_no_interaction(n_features)
    
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

class PolynomialRegression:
    def __init__(self, doe_file: DOEFile) -> None:
        self.doe_file = doe_file

        self.data: list = []

    def get_func_str(self) -> str:
        ret = ""
        for i, d in enumerate(self.data):
            ret += f"F{ i + 1 } = { d };\n"
        
        return ret

    def get_func_grads(self) -> str:
        ret = ""

        size = self.doe_file.independent.shape[1]

        # get functions
        funcs = {}
        for i, d in enumerate(self.data):
           funcs[ f"F{ i + 1 }" ] = f"{ d }"
        
        vars = {}
        for i in range(size):
            vars[ f"X{ i + 1 }" ] = ""
        
        gm = GradientManager(vars, funcs)

        grads = gm.generate(no_simplify=True)

        for g in grads:
            ret += f"{ g } = { grads[ g ] };\n"

        return ret

    def get_func_value(self, vals):
        funcs = self.data

        f = [ create_function_from_string( clean( func, self.doe_file.independent.shape[ 1 ] ) ) for func in funcs ]

        return [ _function( vals ) for _function in f ]
    
    def get_stats(self, _type: int, _func: int):
        y = self.doe_file.dependent[:, _func]

        match _type:
            case 0:
                X = np.column_stack([np.ones(self.doe_file.independent.shape[0])] + [self.doe_file.independent[:, i] for i in range(self.doe_file.independent.shape[1])])
                B = linear_regression(X, y)
            case 1:
                X = self.doe_file.independent
                B = polynomial_regression_no_interaction(X, y)
                X = generate_polynomial_features_no_interaction(X)
            case 2:
                X = self.doe_file.independent
                B = polynomial_regression(X, y)
                X = generate_polynomial_features(X)
            case _:
                return
    
        y_pred = X @ B

        _info = self.calculate_statistics(X, y, y_pred)

        info = []
        info.append( f"{ _info['F-statistic'] }" )
        info.append( f"{ _info['p-value'] }" )
        info.append( f"{ _info['R2'] }" )
        info.append( f"{ _info['R2_adj'] }" )
        info.append( f"{ _info['RMSE'] }" )
        info.append( f"{ _info['PRESS'] }" )
        info.append( f"{ _info['R2_press'] }" )

        return info

    def calculate_statistics(self, X, y, y_pred):
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

    def linear(self):
        ind = self.doe_file.independent

        ret = []
        for i in range( self.doe_file.dependent.shape[1] ):
            dep = self.doe_file.dependent[:, i]

            ret.append(self.__do_linear(ind, dep))
        
        return ret
    
    def __do_linear(self, ind, dep):
        X = np.column_stack([np.ones(ind.shape[0])] + [ind[:, i] for i in range(ind.shape[1])])
        y = dep

        B = linear_regression(X, y)

        # Generate the equation string
        equation_terms = [f"{B[0]}"]
        for i in range(1, len(B)):
            equation_terms.append(f"{B[i]} * x{i}")
        equation = " + ".join(equation_terms)

        return equation

    def quad_interaction(self):
        ind = self.doe_file.independent

        ret = []
        for i in range( self.doe_file.dependent.shape[1] ):
            dep = self.doe_file.dependent[:, i]

            ret.append( self.__do_quad_int(ind, dep) )
        
        return ret

    def __do_quad_int(self, ind, dep):
        B = polynomial_regression(ind, dep)

        equation = coefficients_to_equation(B, ind.shape[1])

        return equation

    def quad_no_int(self, ret_B: bool = False):
        ind = self.doe_file.independent

        ret = []
        for i in range( self.doe_file.dependent.shape[1] ):
            dep = self.doe_file.dependent[:, i]

            ret.append( self.__do_quad_no_int(ind, dep) )
        
        return ret

    def __do_quad_no_int(self, ind, dep):
        B = polynomial_regression_no_interaction(ind, dep)

        equation = coefficients_to_equation_no_interaction(B, ind.shape[1])

        return equation
