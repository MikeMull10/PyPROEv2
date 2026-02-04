![Design of Experiments Page](:/docs/imgs/doe.png)
# Design of Experiments

## Methods

1. Factorial
2. Central Composite, Spherical
3. Central Composite, Face-Centered
4. Taguchi Orthogonal Array
5. Latin Hypercube

### Factorial
Creates a full combination matrix based on the following parameters:
- Variable Count - Determines the number of variables the design of experiments matrix will use.
- Function Count - Determines the number of functions the design of experiments matrix will use.
- Level Count - Determines the number of samples for each variable in the design of experiments matrix. (I.e. 2 → minimum and maximum, 3 → minimum, mid-point, and maximum, etc.)

### Central Composite, Spherical
Create a response surface design that evenly explores all directions around the center point for reliable optimization using the following parameters:
- Variable Count - Determines the number of variables the design of experiments matrix will use.
- Function Count - Determines the number of functions the design of experiments matrix will use.
- Center Points - Number of repeated runs at the center of the design space. Center points are used to estimate experimental error and detect curvature in the response. Increasing this value improves model reliability but increases the total number of runs.

### Central Composite, Face-Centered
Create a design that explores curvature while staying within the original factor ranges using the following parameters:
- Variable Count - Determines the number of variables the design of experiments matrix will use.
- Function Count - Determines the number of functions the design of experiments matrix will use.
- Center Points - Number of repeated runs at the center of the design space. Center points are used to estimate experimental error and detect curvature in the response. Increasing this value improves model reliability but increases the total number of runs.

### Taguchi Orthogonal Array
Creates a smaller matrix that efficiently screens factor effects using balanced fractional designs. Uses the following parameters:
- Variable Count - Determines the number of variables the design of experiments matrix will use.
- Function Count - Determines the number of functions the design of experiments matrix will use.
- Level Count - Defines how many discrete settings each factor can take (e.g., 2-level, 3-level).

### Latin Hypercube
Creates a matrix that spreads samples evenly across all variable ranges for broad, efficient exploration, using the following parameters:   
- Variable Count - Determines the number of variables the design of experiments matrix will use.
- Function Count - Determines the number of functions the design of experiments matrix will use.
- Data Points - Determines how many distinct samples are created across all variable ranges.