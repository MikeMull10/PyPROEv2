# Getting Started

Welcome to **PyPROE X** 
This guide will walk you through the basics of using the application, from defining a problem to visualizing results.

---

## 1. What is PyPROE?

PyPROE is a modeling and optimization tool designed to help you:

- Define **variables** and **functions**
- Build **designs of experiments (DOE)**
- Create **metamodels** (e.g., RBF, regression)
- Visualize results with **plots and surfaces**
- Perform **optimization and analysis**

You do *not* need to write code to use PyPROE — everything is done through the interface.

---

## 2. Main Interface Overview

When you launch PyPROE, you will see:

- **Navigation Bar (left)**  
  - Used to switch between pages such as *Main*, *Plotting*, and *Settings*.

- **Main Page**  
  - Where you define variables, functions, and designs.

- **Plotting Page**  
  - Used to visualize functions, surfaces, contours, and results.

---

## 3. Defining Variables

Variables represent the inputs to your problem.

1. Open the **Design** dialog
2. Add one or more variables
3. For each variable, specify:
   - **Minimum value**
   - **Maximum value**
   - **Symbol** (e.g., `x1`, `x2`)

Example:

| Variable | Min | Max |
|--------|-----|-----|
| x₁     | 0   | 10  |
| x₂     | -5  | 5   |

---

## 4. Defining Functions

Functions describe relationships between variables.

1. Add a function in the **Functions** section
2. Provide:
   - A **name** (e.g., `f1`)
   - A **mathematical expression**

Example:

```text
F1 = X1 ^ 2 + 2 * X2;
