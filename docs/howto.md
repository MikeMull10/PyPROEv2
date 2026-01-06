# How to use PyPROE X

---

## Starting with Equations

If you already have the equations (objective & constraint functions), then you can jump straight to formulating. You can minimize the **Design of Experiment** and **Metamodeling** tabs by clicking on their headers.

We will use the following example to demonstrate:

---

### Example Setup

![Example Image](:/docs/imgs/ex1.png)

First, insert the two variables into formulation:

![Variables](:/docs/imgs/vars.png)

Next, add the three equations:

![Functions](:/docs/imgs/funcs.png)

Then, add the objective function:

![Objective](:/docs/imgs/obj.png)

Add the equality and inequality constraints:

![Equality Constraint](:/docs/imgs/eq.png)

![Inequality Constraint](:/docs/imgs/ineq.png)

Make sure to **flip the sign** for the inequality constraint because we need to see if X1 is greater than 1.

---

### Finding the Solution for the Example

Now that we have our problem formulated, we can run optimization. Make sure that **SLSQP** is the selected solver. Since this is a single-objective problem, we will use SLSQP to solve it. For problems with more than one objective function, another solver should be used.

![Solver](:/docs/imgs/opt-head.png)

We will keep the gridsize at 5. This will provide 25 starting points to find the lowest point. When ready, press **Start**.

This should provided the following result:
```
Optimization Statistics for SINGLE
————————————————————————————————————————————————————————————————

Objective Function: 
 - O1 (F1): 0.4999999999999998

Solution(s):
————————————————————————————————————————————————————————————————
 - X1: 1.5000000000000002
 - X2: 1.5
————————————————————————————————————————————————————————————————
Job completed successfully
=================================
TOTAL TIME ELAPSED: 00h:00m:00s
```

This tells us that the smallest possible value is `~0.5` at the point `(1.5, 1.5)`. To see this visually, copy the formulation using the copy button.

![Copy](:/docs/imgs/copy.png)

Once copied, use the navigation bar on the left to access the Plotting page, press the paste button to paste the formulation data. It should look like this:

![Paste](:/docs/imgs/paste.png)

Press the **Plot** button at the button and choose Contours. This allows us to visualize our equations.

To find ths solution visually, we see that the solution must be on the diagonal line because it is an equality-constraint where the value must equal 3, and the solution must be to the right of the vertical line as it is an inequality-constraint where the value must be greater than 1. The rings show the value of the objective function. The smallest possible value is the one closest to the center of the rings, to the right of the vertical line, and touching the diagonal line.

![Sol](:/docs/imgs/sol.png)

## Starting without the Equations

To be added later.