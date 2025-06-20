from time import time

import matplotlib.pyplot as plt

from algorithms.optimization import Optimization
from algorithms.slsqp import clean, create_function_from_string
from handlers.inputfnc import *

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.problems.functional import FunctionalProblem
from pymoo.optimize import minimize

def solve_evolve(
    n_objs: int,
    problem: FunctionalProblem,
    algorithm: str = "NSGAII",
    generations: int = 1000,
    population: int = 200,
    crossover: float = 0.9,
    mutation: float = 0.01,
    n_partitions: int = 100,
    verbose: bool = False,
    handle_error=None,
) -> Optimization:
    """Perform optimzation with an evolutionary algorithm: NSGAII, NSGAIII

    Parameters
    ---------
    algorithm : "NSGAII" | "NSGAIII" | "EpsMOEA"
        The type of algorithm to use in optimization
    generations: int
        The number of generations to evolve through
    population : int
        The starting population size for NSGAII or NSGAIII
    crossover : float
        The crossover rate of evolution
    mutation : float
        The mutation rate of evolution
    n_partitions : int
        The number of outer subsections NSGAIII distributes its solutions among
    eps : list[float]
        The epsilon value(s) used by EpsMOEA in its evaluations
    verbose : boolean
        Print all the solutions to the console
    """
    # SBX is simulated binary crossover - 90% probability of mutation
    # PM is polynomial mutation - 1% probability rate
    cross = SBX(crossover)
    poly_mut = PM(prob=mutation)
    algo = None

    if algorithm == "NSGAII":
        algo = NSGA2(pop_size=population, crossover=cross, mutation=poly_mut)
    elif algorithm == "NSGAIII":
        ref_dirs = get_reference_directions("uniform", n_objs, n_partitions=n_partitions)
        algo = NSGA3(pop_size=population, crossover=cross, mutation=poly_mut, ref_dirs=ref_dirs)

    t = time()

    results = {"crs": crossover, "mut": mutation}

    if algorithm == "NSGAII":
        results["pop"] = population

    elif algorithm == "NSGAIII":
        results["n_parts"] = n_partitions
    else:
        return Exception(
            "Invalid algorithm. Choose from NSGAII or NSGAIII."
        )

    # run the algorithm
    res = minimize(problem,
            algo,
            ('n_gen', generations),
            seed=42,
            verbose=verbose)

    time_taken = time() - t

    # log the solutions (optionally)
    if verbose:
        print("Objectives: ")
        [
            print(str(i))
            for i in res.F
        ]

    results["sol"] = res.F
    results["time"] = time_taken
    results["alg"] = algorithm

    return Optimization("evo", results, time_taken)


def handle_evolve(
    input_file: InputFile,
    num_iter: int = 1000,  # number of generations
    population: int = 200,  # population size
    crossover: float = 0.9,  # the crossover rate
    mutation: float = 0.01,  # the mutation rate
    n_partitions: int = 100,  # n_partitions used for NSGAIII
    algorithm: str = "NSGAII",  # which algorithm to use
    verbose: bool = False,  # whether or not to print all solutions
):
    """Gather the information necessary to call the optimization algorithm

    Parameters
    ----------
    problem : Problem
        Problem class with the number of objectives, variables, and constraints
    bounds : Real | list[Real]
        Bounds of the problem variable(s) in the form Real(min, max)
    definition : function
        A function that evaluates the values of objective and constraint functions
        and returns the answers as a tuple ([obj1, obj2], [cons1, cons2])
    """

    objectives = input_file.get_objective_functions()
    bounds = input_file.get_bounds()
    variables = input_file.variables
    cons = input_file.get_constraint_functions()

    # def func_definition(x):
    #     if cons:
    #         return (
    #             [
    #                 create_function_from_string(clean(f, len(variables)))(x)
    #                 for f in objectives
    #             ],
    #             [
    #                 create_constraint_from_string(f, input_file.functions, len(input_file.variables))(x)
    #                 for t, f in cons
    #             ],
    #         )
    #     else:
    #         return [
    #             create_function_from_string(clean(f, len(variables)))(x)
    #             for f in objectives
    #         ]
    

    problem = FunctionalProblem(
        n_var=len(variables.keys()),
        
        objs=[(create_function_from_string(clean(f, len(variables)))) for f in objectives],
        constr_eq=[( create_constraint_from_string(f, input_file.functions, len(input_file.variables))) for t, f in cons if t == "eq"],
        constr_ieq=[( create_constraint_from_string(f, input_file.functions, len(input_file.variables))) for t, f in cons if t == "ineq"],
        xl=[x[0] for x in bounds],
        xu=[x[1] for x in bounds],
    )

    return solve_evolve(
        len(objectives),
        problem,
        generations=num_iter,
        population=population,
        crossover=crossover,
        mutation=mutation,
        n_partitions=n_partitions,
        algorithm=algorithm,
        verbose=verbose,
    )
