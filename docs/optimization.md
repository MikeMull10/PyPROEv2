![Optimization Page](:/docs/imgs/optimization.png)
# Optimization

## Solvers

1. SLSQP
2. SLSQP + WSF
3. NSGAII
4. NSGAIII

### SLSQP
Sequential Least Squares Programming (SLSQP) is a gradient-based solver for constrained optimization problems.  
It iteratively adjusts variable values to minimize or maximize the objective function while respecting constraints.

### SLSQP + WSF
An extension of SLSQP that incorporates **Weighted Sum Formulation (WSF)** to handle multi-objective problems by combining multiple objectives into a single weighted function.

### NSGAII
The Non-dominated Sorting Genetic Algorithm II (NSGA-II) is a population-based evolutionary algorithm designed for multi-objective optimization.  
It uses selection, crossover, and mutation to explore the solution space and generate Pareto-optimal solutions.

### NSGAIII
NSGA-III is an evolutionary multi-objective optimization algorithm suitable for many-objective problems.  
It extends NSGA-II with reference directions to improve diversity and convergence for higher-dimensional objective spaces.

---

## Solver Parameters

**Grid Size**  
  Determines the number of equally spaced samples generated along each dimension in the grid. A higher grid size increases the number of guesses by creating a finer grid, while a lower grid size reduces the number of guesses by creating a coarser grid.

**Minimum Weight**  
  Defines the lower bound for weights in weighted formulations. Relevant for solvers using weighted sum approaches.

**Weight Increment**  
  Defines the adjustment interval for weights during iterative multi-objective optimization.

**Iterations**  
  Defines the number of cycles the algorithm will run.

**Population**  
  Defines the number of candidate solutions maintained in population-based algorithms like NSGA-II/III.

**Crossover Rate**  
  Defines the frequency of recombination between candidate solutions in genetic algorithms.

**Mutation Rate**  
  Controls the probability of random variation in candidate solutions to maintain diversity.

**Partitions**  
  Defines the number of segments or divisions in the solution space for grid-based sampling or weight exploration.
