from scipy.stats import qmc
from numpy import ndarray
from components.fnc_objects import Variable

def lhs(variables: list[Variable], samples: int) -> ndarray:
    sampler = qmc.LatinHypercube(len(variables))
    sample = sampler.random(n=samples)

    return qmc.scale(sample, l_bounds=[var.min for var in variables], u_bounds=[var.max for var in variables])
