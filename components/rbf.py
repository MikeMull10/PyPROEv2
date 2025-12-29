import numpy as np
from scipy.spatial.distance import cdist
from enum import Enum
import re

class RBFType(Enum):
    LINEAR = 0
    CUBIC = 1
    THIN_PLATE_SPLINE = 2
    GAUSSIAN = 3
    MULTIQUADRIC = 4
    INVERSE_MULTIQUADRIC = 5
    CS_2_0 = 6
    CS_2_1 = 7
    CS_2_2 = 8
    CS_3_0 = 9
    CS_3_1 = 10
    CS_3_2 = 11
    CS_3_3 = 12

def wendland_kernel(r, kernel: RBFType, epsilon):
    """Compactly supported Wendland kernels."""
    rho = epsilon * r
    t = np.maximum(0.0, 1.0 - rho)

    if kernel in (RBFType.CS_2_0, RBFType.CS_3_0):
        return t**2

    elif kernel in (RBFType.CS_2_1, RBFType.CS_3_1):
        return t**4 * (4*rho + 1)

    elif kernel in (RBFType.CS_2_2, RBFType.CS_3_2):
        return t**6 * (35*rho**2 + 18*rho + 3)

    elif kernel == RBFType.CS_3_3:
        return t**8 * (32*rho**3 + 25*rho**2 + 8*rho + 1)

    else:
        raise NotImplementedError(kernel)

def rbf_kernel(r, kernel: RBFType, epsilon=1.0):
    """Compute RBF kernel values for distance matrix r."""
    if kernel == RBFType.GAUSSIAN:
        return np.exp(-(epsilon*r)**2)

    elif kernel == RBFType.MULTIQUADRIC:
        return np.sqrt(1 + (epsilon*r)**2)

    elif kernel == RBFType.INVERSE_MULTIQUADRIC:
        return 1 / np.sqrt(1 + (epsilon*r)**2)

    elif kernel == RBFType.LINEAR:
        return r

    elif kernel == RBFType.CUBIC:
        return r**3

    elif kernel == RBFType.THIN_PLATE_SPLINE:
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.where(r > 1e-10, r**2 * np.log(r), 0)
        return result

    elif kernel.name.startswith("CS_"):
        return wendland_kernel(r, kernel, epsilon)

    else:
        raise NotImplementedError(kernel)

def needs_polynomial(kernel: RBFType):
    """Check if kernel requires polynomial augmentation."""
    # Conditionally positive definite kernels need polynomial terms
    return 1 if kernel in (RBFType.THIN_PLATE_SPLINE, RBFType.LINEAR, RBFType.CUBIC) else None

def build_polynomial_matrix(X, degree=1):
    """Build polynomial basis matrix for given points."""
    X = np.asarray(X)
    n, d = X.shape
    
    if degree == 0:
        # Just constant term
        return np.ones((n, 1))
    elif degree == 1:
        # Constant + linear terms: [1, x1, x2, ..., xd]
        return np.column_stack([np.ones(n), X])
    else:
        raise NotImplementedError(f"Polynomial degree {degree} not implemented")

def fit_rbf(X: np.ndarray, y: np.ndarray, kernel: RBFType, epsilon: float=1.0, smooth: float=0.0, poly_order: int | None=None):
    """
    Fit RBF interpolation to data.
    
    Parameters:
    -----------
    X : array-like, shape (n, d)
        Input points
    y : array-like, shape (n,)
        Target values
    kernel : RBFType
        RBF kernel type
    epsilon : float
        Shape parameter for the kernel
    smooth : float
        Smoothing/regularization parameter (0 = exact interpolation)
    poly_order : int or None
        Whether to include polynomial terms. If None, automatically determined.
    
    Returns:
    --------
    weights : dict
        Dictionary containing 'rbf_weights' and optionally 'poly_weights'
    """
    X = np.asarray(X)
    y = np.asarray(y)
    n = len(X)
    
    if poly_order is None:
        poly_order = needs_polynomial(kernel)  # must return int or None

    # Build kernel matrix
    D = cdist(X, X)
    K = rbf_kernel(D, kernel, epsilon)

    # ---- NO polynomial terms ----
    if poly_order is None:
        if smooth > 0:
            K += np.eye(n) * smooth
        rbf_weights = np.linalg.solve(K, y)
        return {
            'rbf_weights': rbf_weights,
            'poly_weights': None,
            'centers': X
        }

    # ---- WITH polynomial terms ----
    P = build_polynomial_matrix(X, degree=poly_order)
    m = P.shape[1]

    A = np.zeros((n + m, n + m))
    A[:n, :n] = K
    if smooth > 0:
        A[:n, :n] += np.eye(n) * smooth
    A[:n, n:] = P
    A[n:, :n] = P.T

    b = np.zeros(n + m)
    b[:n] = y

    solution = np.linalg.solve(A, b)

    return {
        'rbf_weights': solution[:n],
        'poly_weights': solution[n:],
        'centers': X
    }

def eval_rbf(X_eval, weights_dict, kernel: RBFType, epsilon=1.0):
    """
    Evaluate RBF interpolant at new points.
    
    Parameters:
    -----------
    X_eval : array-like, shape (m, d)
        Evaluation points
    weights_dict : dict
        Dictionary from fit_rbf containing weights and centers
    kernel : RBFType
        RBF kernel type
    epsilon : float
        Shape parameter
    
    Returns:
    --------
    y_eval : array, shape (m,)
        Interpolated values
    """
    X_eval = np.asarray(X_eval)
    X = weights_dict['centers']
    rbf_weights = weights_dict['rbf_weights']
    poly_weights = weights_dict.get('poly_weights')
    
    # Evaluate RBF terms
    D = cdist(X_eval, X)
    K = rbf_kernel(D, kernel, epsilon)
    y_eval = K @ rbf_weights
    
    # Add polynomial terms if present
    if poly_weights is not None:
        P = build_polynomial_matrix(X_eval, degree=1)
        y_eval += P @ poly_weights
    
    return y_eval

def rbf_term_str(w, center, kernel: RBFType, epsilon=1.0):
    """Generate string representation of single RBF term."""
    dist_sq = " + ".join(
        [f"(x{i+1} - {v:.15g})**2" for i, v in enumerate(center)]
    )
    r = f"sqrt({dist_sq})"
    eps_str = f"{epsilon:.15g}"
    rho = f"{eps_str}*{r}"
    t = f"max(0, 1 - {rho})"

    if kernel == RBFType.GAUSSIAN:
        core = f"exp(-({eps_str})**2 * ({dist_sq}))"

    elif kernel == RBFType.MULTIQUADRIC:
        core = f"sqrt(1 + ({eps_str}*{r})**2)"

    elif kernel == RBFType.INVERSE_MULTIQUADRIC:
        core = f"1/sqrt(1 + ({eps_str}*{r})**2)"

    elif kernel == RBFType.LINEAR:
        core = r

    elif kernel == RBFType.CUBIC:
        core = f"({r})**3"

    elif kernel == RBFType.THIN_PLATE_SPLINE:
        core = f"({r})**2 * log({r}) if {r} > 0 else 0"

    elif kernel in (RBFType.CS_2_0, RBFType.CS_3_0):
        core = f"({t})**2"

    elif kernel in (RBFType.CS_2_1, RBFType.CS_3_1):
        core = f"({t})**4 * (4*{rho} + 1)"

    elif kernel in (RBFType.CS_2_2, RBFType.CS_3_2):
        core = f"({t})**6 * (35*{rho}**2 + 18*{rho} + 3)"

    elif kernel == RBFType.CS_3_3:
        core = f"({t})**8 * (32*{rho}**3 + 25*{rho}**2 + 8*{rho} + 1)"

    else:
        raise NotImplementedError(kernel)

    return f"{w:.15g} * ({core})"

def rbf_equation_str(weights_dict, kernel: RBFType, epsilon=1.0):
    """Generate full equation string for RBF interpolant."""
    rbf_weights = weights_dict['rbf_weights']
    centers = weights_dict['centers']
    poly_weights = weights_dict.get('poly_weights')
    
    terms = [
        rbf_term_str(w, c, kernel, epsilon)
        for w, c in zip(rbf_weights, centers)
    ]
    
    # Add polynomial terms if present
    if poly_weights is not None:
        n_dim = centers.shape[1]
        terms.append(f"{poly_weights[0]:.15g}")  # constant

        # Add linear terms only if they exist
        for i in range(1, len(poly_weights)):
            terms.append(f"{poly_weights[i]:.15g} * x{i}")
    
    return f"\n{' ' * 3} + ".join(terms)

def generate_rbf(X: np.array, y: np.array, rbf_type: RBFType, epsilon: float, poly_order: int=0, smooth: float=0.0, variable_names=None):
    weights = fit_rbf(X, y, rbf_type, epsilon=epsilon, smooth=smooth, poly_order=poly_order)
    equation = rbf_equation_str(weights, rbf_type, epsilon)
    
    # Replace variable names if custom names provided
    if variable_names is not None:
        for i, var_name in enumerate(variable_names):
            equation = re.sub(rf'\bx{i+1}\b', var_name, equation)
    
    return equation
