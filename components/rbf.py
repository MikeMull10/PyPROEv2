import numpy as np
from scipy.spatial.distance import cdist
from enum import Enum

# -----------------------------
# RBF Types
# -----------------------------
class RBFType(Enum):
    LINEAR = 0
    CUBIC = 1
    THIN_PLATE_SPLINE = 2
    GAUSSIAN = 3
    MULTIQUADRIC = 4
    INVERSE_MULTIQUADRIC = 5

# -----------------------------
# Kernel evaluation
# -----------------------------
def rbf_kernel(r, kernel: RBFType, epsilon=1.0):
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
        return r**2 * np.log(1 + r)
    else:
        raise NotImplementedError(f"Kernel {kernel} not implemented")

# -----------------------------
# Fit RBF manually
# -----------------------------
def fit_rbf(X, y, kernel: RBFType, epsilon=1.0):
    D = cdist(X, X)
    A = rbf_kernel(D, kernel, epsilon)
    weights = np.linalg.solve(A, y)
    return weights

# -----------------------------
# Evaluate RBF
# -----------------------------
def eval_rbf(X_eval, X, weights, kernel: RBFType, epsilon=1.0):
    D = cdist(X_eval, X)
    K = rbf_kernel(D, kernel, epsilon)
    return K @ weights

# -----------------------------
# Create human-readable string
# -----------------------------
def rbf_term_str_explicit(w, c, kernel: RBFType, epsilon=1.0):
    # create explicit squared distance string
    dist_str = " + ".join([f"(x{i+1} - {v})**2" for i, v in enumerate(c)])
    dist_expr = f"sqrt({dist_str})"
    
    if kernel == RBFType.GAUSSIAN:
        return f"{w} * exp(-{epsilon}*({dist_str}))"
    elif kernel == RBFType.MULTIQUADRIC:
        return f"{w} * sqrt(1 + ({epsilon}*{dist_expr})**2)"
    elif kernel == RBFType.INVERSE_MULTIQUADRIC:
        return f"{w} / sqrt(1 + ({epsilon}*{dist_expr})**2)"
    elif kernel == RBFType.LINEAR:
        return f"{w} * {dist_expr}"
    elif kernel == RBFType.CUBIC:
        return f"{w} * ({dist_expr})**3"
    elif kernel == RBFType.THIN_PLATE_SPLINE:
        return f"{w} * ({dist_expr})**2 * log(1 + {dist_expr})"
    else:
        raise NotImplementedError(f"Kernel {kernel} not implemented")

def rbf_equation_str_explicit(weights, centers, kernel: RBFType, epsilon=1.0):
    terms = [rbf_term_str_explicit(w, c, kernel, epsilon) for w, c in zip(weights, centers)]
    return " + ".join(terms)

# -----------------------------
# Your 2D data
# -----------------------------
if __name__ == "__main__":
    X = np.array([
        [0.02, 0.001],
        [0.02, 0.0055],
        [0.02, 0.01],
        [0.11, 0.001],
        [0.11, 0.0055],
        [0.11, 0.01],
        [0.2, 0.001],
        [0.2, 0.0055],
        [0.2, 0.01]
    ])

    y = np.array([
        [2.867017456, 0.001871543, 408.0895977],
        [13.94914262, 0.001655596, 83.87612284],
        [22.05398043, 0.001439648, 53.0516477],
        [16.09940571, 6.31671e-05, 72.67349],
        [86.72727803, 6.18692e-05, 13.49056521],
        [154.377863, 6.05712e-05, 7.578806814],
        [29.33179397, 1.91473e-05, 39.88845692],
        [159.5054134, 1.89314e-05, 7.335174241],
        [286.7017456, 1.87154e-05, 4.080895977]
    ])

    # -----------------------------
    # Fit RBFs and print explicit equations
    # -----------------------------
    kernel = RBFType.GAUSSIAN
    epsilon = 2.0

    for i in range(y.shape[1]):
        weights = fit_rbf(X, y[:, i], kernel, epsilon)
        eq_str = rbf_equation_str_explicit(weights, X, kernel, epsilon)
        print(f"\nRBF Equation for f{i+1}:\n")
        print(eq_str)
