## CIRCUIT SIMULATOR

Basic electrical circuit simulator. That's how I define a recently written Python Class which is capable of solving linear circuits (V, I, R variables), by using the well-knowned Kirchhoff Laws.

**Features:**

1. Initiallize circuits by passing its branches as atributtes. The circuit is modelled throught an **internal multigraph**: branch components as the corresponding edge atributtes.

2. **Automatic Kirchhoff update**, if possible, to determine the unknown variable for each branch: given a voltage source and a resistance, computes that branch intensity, or the potential difference of the generator if it's a current source. Also can determine the branch resistance if having a voltage AND a current source, but only if the Kirchhoff laws allow it: doesn't solve unstable circuits.

3. Circuit **str representation** using both `branch_view()` or `circuit_view()` methods. The first one as the standard, plots circuit branches in a ascending order, with their components. The second one is a more complete circuit view, layering the branches with column nodes, but only garantees a correct label for short (< 4 nodes) circuits.

4. Also have **useful methods** as `potential_difference()`, used for getting the potential difference between two circuit nodes.

5. And the better one... have **symbolic support**! Uses SimPy library for all computations, so can actually perform symbolic operations. That means, we can pass branch's values as knowned variables like 'V1' or 'R', so the targetted variable will get also a symbolic expression as result. That's so useful for college tasks, or general circuits where we don't know some of the branch's actual values.

**Limitations:**

The class is under-development-when-I-have-time, so I'm still thinking on how to improve it. For the moment, circuit branches only supports the three basic linear components: resistances, source generators and current generators, in DC.

**Examples:**
I've provided some circuits as examples, which you can acces at [./examples].

Of course, any comment, advise or support is highly appreciated.
