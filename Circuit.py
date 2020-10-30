import networkx as nx
import sympy as sym
import numpy as np


class Circuit():
    """ Electrical circuit modelling using an undirect weighted MultiGraph.

    Features:
    ------------
    - Holds and analyzes an electrical circuit given by it's branches, in aim to
     get the unknown value for each branch, that is, to solve the circuit.

    - Applies Kirchhoff Laws over the nodes and circuit loops,
    and resolves the linear resulting system, if possible.

    - Uses an internal graph representation of the circuit, shaping the
    nodes, branches and meshes of the circuit as the nodes, edges and
    cycles of the graph.

    Edge weights contain all branches components information, only supporting,
    for the moment:

    a) the resistance value 'R': ---[ *** KΩ]---

        The total resistance value inside the branch. Can be zero or positive,
        represents the resistance of all the physical components in that branch.

    b) the voltage value 'V': ---( *** V)---

        The total pottential difference given by the voltage sources inside
        the branch. Because the sources have two positions (direct or inverse),
        we consider a positive value when the source is direct in respect the
        ascending order '<' between edge connected nodes, and negative if not.

    c) the intensity value 'I':  ---\ *** mA\---

        The intensity value of the current that pass through the branch, measured
        in miliAmperes [mA]. As the voltage, a positive value means that its
        direction keeps the ascending order of the nodes, and a negative value
        means that goes in inverse direction.

    Normally, the intensity or 'I' representa branch's unknown, so we have to
    provide the resistance 'R' and voltage 'V' as input components.
    When the branch has a source generator, the intensity acts as an input component
    and the voltage value represents its potential difference. In this case, the
    unknown will be the voltage 'V' if a resistance value is given, or viceversa.

    If the circuit doesn't have a stable solution, the unknown value will take
    'NaN' (Not a Number) value, which represents an indetermination.

    Attributes:
    ------------
    nodes    : list of the circuit nodes.

    branches : dictionary of circuit branches, with component's values as dictionary keys.

    meshes   : list of the circuit meshes or loops, as the base cicles
               of the internal graph.

    Using these three attributes, the circuit can be solved by just extracting
    manually the necessary equations.

    Instead, this class only needs the branches dictionary passed as an initial
    parameter, and all computations are performed internally. Of course, stills
    needs the work of translating correctly all the circuit components.

    """

    # Variable units
    V_units = 'V'
    R_units = 'kO'
    I_units = 'mA'


    # Constructor
    def __init__(self, edgelist = []):
        """ Builds the circuit by passing a list of branches with their attributes.
            Empty circuit by default. """

        self._circuit = nx.MultiGraph()
        self._meshes = []

        # Add all branches
        for edge in edgelist:
            self.add_branch((edge[0], edge[1]), **(edge[2].copy()))


    # Branch adder
    def add_branch(self, edge, **edgedict):
        """ Adds a new branch to the circuit. Also sets its 'R' and 'V' values. """
        # Insertion preconditions + preprocessing
        self.__order_between_nodes(edge)
        self.__supported_dict_keys(edgedict)
        self.__supported_value_types(edgedict)

        # Insertion
        self._circuit.add_edge(edge[0], edge[1], **edgedict)

        # Updates
        self.__mesh_update()
        self.__kirchhoff_update()


    def __order_between_nodes(self, edge):
        """ Edge has to respect node's ascending order.
        Raises an error if edge[0] ≥ edge[1]. """
        if edge[0] >= edge[1]: raise AssertionError(
        "Branch does not satisfy the order '<' between nodes.")


    def __supported_dict_keys(self, edgedict):
        """ Edge dictionary must have two of the supported variables:
        'V', 'R', 'I', to determine the unknown variable. """
        if ('V' in edgedict and 'R' in edgedict and 'I' not in edgedict):
            edgedict['unknown'] = 'I' # Intensity as the unknown variable

        elif ('V' not in edgedict and 'R' in edgedict and 'I' in edgedict):
            edgedict['unknown'] = 'V' # Voltage as the unknown variable

        elif ('V' in edgedict and 'R' not in edgedict and 'I' in edgedict):
            edgedict['unknown'] = 'R' # Resistance as the unknown variable

        else: raise AttributeError("Branch dictionary must have one and only one" +
                    " undefined key variable (the unknown).")


    def __supported_value_types(self, edgedict):
        """ Edge dictionary values must be converted to symbolic expression. """
        if 'V' in edgedict: edgedict['V'] = sym.simplify(edgedict['V'])
        if 'R' in edgedict: edgedict['R'] = sym.simplify(edgedict['R'])
        if 'I' in edgedict: edgedict['I'] = sym.simplify(edgedict['I'])


    # Branch deleter
    def del_branch(self, edge):
        """ Removes the branch specified from the circuit. Has to give a key. """
        self._circuit.remove_edge(edge[0], edge[1], key = edge[2])

        # Updates
        self.__mesh_update()
        self.__kirchhoff_update()


    # Getter for nodes
    @property
    def nodes(self):
        """ Getter for the nodes list of the circuit. """
        return list(self._circuit.nodes)


    # Getter for branches
    @property
    def branches(self):
        """ Getter for the edges dictionary of the circuit. """
        return dict(self._circuit.edges)


    # Getter for meshes
    @property
    def meshes(self):
        """ Getter for the base cycles list of the circuit. """
        return self._meshes


    # Voltage difference
    def potential_diff(self, nodeA, nodeB):
        """ Returns the pottential difference between nodeA and nodeB, as the
        pottential of nodeA with respect nodeB: V_AB = (V_A - V_B). """

        diff = 0

        # For all edges in a biconnected path from B to A,
        nodes = nx.shortest_path(self._circuit, nodeB, nodeA)
        for branch in [(nodes[i], nodes[i+1], 0) for i in range(len(nodes) - 1)]:

            # intensity direction
            if branch in self.branches:
                diff += self._circuit.edges[branch]['V']
                diff -= self._circuit.edges[branch]['I'] * self._circuit.edges[branch]['R']

            # intensity inverse direction
            if (branch[1], branch[0], branch[2]) in self.branches:
                diff -= self._circuit.edges[branch]['V']
                diff += self._circuit.edges[branch]['I'] * self._circuit.edges[branch]['R']

        return diff


    # Str representation
    def __str__(self):
        """ Shows the circuit as a pictographic drawing, by calling the
        circuit_view or branches_view depending on its size and type. """

        # Full view representation
        if (len(self._circuit.nodes) <= 4):
            return self.circuit_view()

        # Short view representation
        else: return self.branches_view()


    # Circuit view (not sure if well labeled)
    def circuit_view(self):
        """ Full circuit view, prints nodes as column separators with
        homogeneous branches. Thinked for short circuits (4 or less nodes). """

        node_idx = {node:i for i, node in enumerate(self.nodes)} # Index remembering
        sep = "\t\t\t\t\t" # Separator between nodes

        # Str representation. Default branch as default lines, for branch separations
        circuit_pattern = sep.join([f"{node}" for node in self.nodes]) + "\n"

        # For each branch between nodes
        for j, branch in enumerate(self._circuit.edges):
            # get the branch nodes index.
            min_idx = min(node_idx[branch[0]], node_idx[branch[1]])
            max_idx = max(node_idx[branch[0]], node_idx[branch[1]])

            # Join and append branch components
            branch_components = []
            for component, value in self._circuit.edges[branch].items():
                # If V is not the unknown
                if component == 'V' and value:
                    branch_components.append("(" + str(value) + " " + self.V_units + ")")
                if component == 'R' and value:
                    branch_components.append("[" + str(value) + " " + self.R_units + "]")
                if component == 'I' and value:
                    branch_components.append("\\" + str(value) + " " + self.I_units + "\\")
            branch_components = "---".join(branch_components)
            branch_components = branch_components.center(40 * (max_idx - min_idx) - 1, "-")

            # Add two default separator lines
            branch_pattern = [""] + [sep for node in self.nodes][:-1] + [""]
            circuit_pattern += "|".join(branch_pattern) + "\n"
            circuit_pattern += "|".join(branch_pattern) + "\n"

            # Add the branch line
            circuit_pattern += "|".join(branch_pattern[:min_idx + 1])
            circuit_pattern += "+" + branch_components + "+"
            circuit_pattern += "|".join(branch_pattern[max_idx + 1:]) + "\n"

        return circuit_pattern


    # Branches view
    def branches_view(self):
        """ Simplified circuit view, as a row list of branches. Suitable for
        simbolic type circuits, or dense circuits (more than 4 nodes). """

        circuit_pattern = "" # Str representation of the branches

        # For each branch between nodes
        for j, branch in enumerate(self._circuit.edges):

            # Join and append branch components
            branch_components = []
            for component, value in self._circuit.edges[branch].items():
                # If V is not the unknown
                if component == 'V' and value:
                    branch_components.append("(" + str(value) + " " + self.V_units + ")")
                if component == 'R' and value:
                    branch_components.append("[" + str(value) + " " + self.R_units + "]")
                if component == 'I' and value:
                    branch_components.append("\\" + str(value) + " " + self.I_units + "\\")
            branch_components = "--------".join(branch_components)
            circuit_pattern += str(branch) + ": (" + str(branch[0]) + ")-------"
            circuit_pattern += branch_components + "-------(" + str(branch[1]) + ")\n\n"
        return circuit_pattern


    # Cycle base calculator
    def __mesh_update(self):
        """ Mesh update, every time that the circuit has changed.
        Gets all the graph base cycles, combined with the multiple edge cycles.
        """

        # Get all base cycles for the undirect multiple graph as:
        self._base_circuit = nx.Graph(self._circuit)
        self._meshes = []

        # the sum of all the base cycles for the undirect simple graph
        for cycle in nx.cycle_basis(self._base_circuit):
            self._meshes += [[(cycle[i-1], cycle[i], 0) for i in range(len(cycle))]]

        # with all the inner cycles for the undirect multiple graph
        for edge in self._base_circuit.edges:
            n = len(self._circuit.adj[edge[0]][edge[1]])
            self._meshes += [[(edge[0], edge[1], i), (edge[1], edge[0], i + 1)]
                             for i in range(n - 1)]


    # Kirchhoff solver
    def __kirchhoff_update(self):
        """ Applies Kirchhoff Laws for soving the circuit, by updating
        the unknowed values for each branch. """

        # Number of nodes and edges.
        N = len(self._circuit.nodes)
        E = len(self._circuit.edges)

        if not E: return # For empty circuits!!

        # Sympy matrixes for the lineal resulting system AX = B.
        A = sym.Matrix.zeros(E)
        B = sym.Matrix.zeros(E, 1)
        X = sym.symbols(f'x:{E}')

        # Apply Kirchhoff laws to get the linear system
        for i in range(E):
            for j, branch in enumerate(self._circuit.edges):

                # 1st Kirchhoff Law (charge conservation):
                # the sum of currents meeting at a node is zero.
                if i < (N - 1):
                    if (branch[1] == list(self._circuit.nodes)[i]): # intensity in

                        # Be sure of treating the correct unknown ('I', 'V' or 'R')
                        if (self._circuit.edges[branch]['unknown'] == 'I'): A[i, j] = 1
                        else: B[i] -= self._circuit.edges[branch]['I']

                    if (branch[0] == list(self._circuit.nodes)[i]): # intensity out

                        # Be sure of treating the correct unknown ('I', 'V' or 'R')
                        if (self._circuit.edges[branch]['unknown'] == 'I'): A[i, j] = -1
                        else: B[i] += self._circuit.edges[branch]['I']

                # 2nd Kirchhoff Law (energy conservation):
                # the directed sum of the voltages around any mesh is zero.
                else:
                    # direct branch
                    if branch in self.meshes[i - (N - 1)]:

                        # Be sure of treating the correct unknown ('I', 'V' or 'R')
                        if (self._circuit.edges[branch]['unknown'] == 'I'):
                            A[i, j] = - self._circuit.edges[branch]['R']
                            B[i] -= self._circuit.edges[branch]['V']

                        if (self._circuit.edges[branch]['unknown'] == 'V'):
                            A[i, j] = 1
                            B[i] += self._circuit.edges[branch]['R'] * self._circuit.edges[branch]['I']

                        if (self._circuit.edges[branch]['unknown'] == 'R'):
                            A[i, j] = - self._circuit.edges[branch]['I']
                            B[i] -= self._circuit.edges[branch]['V']

                    # inverse branch
                    if (branch[1], branch[0], branch[2]) in self.meshes[i - (N - 1)]:

                        # Be sure of treating the correct unknown ('I', 'V' or 'R')
                        if (self._circuit.edges[branch]['unknown'] == 'I'):
                            A[i, j] = self._circuit.edges[branch]['R']
                            B[i] += self._circuit.edges[branch]['V']

                        if (self._circuit.edges[branch]['unknown'] == 'V'):
                            A[i, j] = -1
                            B[i] -= self._circuit.edges[branch]['R'] * self._circuit.edges[branch]['I']

                        if (self._circuit.edges[branch]['unknown'] == 'R'):
                            A[i, j] = self._circuit.edges[branch]['I']
                            B[i] += self._circuit.edges[branch]['V']

        # Solves the linear system for symbolic coefficients
        # or numeric values and gets the solution
        solution_space = sym.linsolve((A, B), X)
        self.solved = bool(solution_space)
        for solution in solution_space: break

        # Adds the solutions back to branches
        for j, branch in enumerate(self._circuit.edges):
            variable = self._circuit.edges[branch]['unknown']
            if self.solved:  self._circuit.edges[branch][variable] = solution[j]
            else:  self._circuit.edges[branch][variable] = sym.S.NaN
