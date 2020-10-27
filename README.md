## KIRCHHOFF CALCULATOR

Basic electrical circuit calculator. That's how I define a recently written Python Class which is capable of solving linear circuits (V, I, R variables), by using the well-knowned Kirchhoff Laws.

**Features:**

1. Initiallize circuits by passing its branches as atributtes. The circuit is modelled throught an **internal multigraph**: branch components as the corresponding edge atributtes.

2. **Automatic Kirchhoff update**, if possible, to determine the unknown variable for each branch: given a generator and a resistance, computes that branch intensity (if voltage source) or the potential difference of the generator (if current source). Also can determine the branch resistance if having a voltage AND a current source, but only if the Kirchhoff laws allow it: doesn't solve unstable circuits. 

3. Circuit **str representation** using both `branch_view()` or `circuit_view()` methods. The first one as the standard, plots circuit branches in a ascending order, with their components. The second one is a more complete circuit view, layering the branches with column nodes, but only is garanteed to work for short (< 4 nodes) circuits. 

4. **Useful methods** as `potential_difference()`, for getting the potential difference between two circuit nodes, and `thevenin()`, which applies a thevenin transformation onto a branch's complement subcircuit, and returns the resulting thevenin voltage Vth and thevenin resistance Rth.

5. And the better one... have **symbolic support**! Uses SimPy library for all computations, so can actually perform symbolic operations. That means, we can pass branch's values as knowed variables like 'V1' or 'R', so the targetted variable will get also a symbolic expression as result. That's so useful for college tasks, or general circuits where we don't know some of the branch's actual values.
