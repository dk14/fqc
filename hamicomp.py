from dataclasses import dataclass

from comp import *
import itertools
from qiskit_optimization import QuadraticProgram

#formulate problem compatible with quadrantic program

LinearFormula = dict[str, int]

class HamiltonianComputer(Computer):
    def to_linear_formula(formula: Sum, acc: LinearFormula = {}) -> LinearFormula: 
         while True:
            match formula:
                case Sum(Zero(), Mul(x, name)):
                    return {name: x} | acc
                case Sum(next, Mul(x, name)):
                    formula = next
                    acc = {name: x} | acc

    def formulate_problem(formula: Sum) -> QuadraticProgram:
        qp = QuadraticProgram()
        vars = Computer.extract_vars(formula)
        for name in vars:
            qp.binary_var(name)
        qp.maximize(linear=HamiltonianComputer.to_linear_formula(formula))
        # print(qp.export_as_lp_string())
        return qp


# run optimization on qiskit's solver (classic and quantum)
# https://qiskit-community.github.io/qiskit-finance/tutorials/01_portfolio_optimization.html

from qiskit.circuit.library import TwoLocal
from qiskit.result import QuasiDistribution
from qiskit_aer.primitives import Sampler
from qiskit_algorithms import NumPyMinimumEigensolver, QAOA, SamplingVQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms.utils import algorithm_globals


class HamiltonianComputerClassicEigen(HamiltonianComputer):

    def maximize(self, formula: Sum) -> VarState:
        qp = HamiltonianComputer.formulate_problem(formula)
        exact_mes = NumPyMinimumEigensolver()
        exact_eigensolver = MinimumEigenOptimizer(exact_mes)
        result = exact_eigensolver.solve(qp)
        return result.variables_dict


class HamiltonianComputerQuantum(HamiltonianComputer):

    def maximize(self, formula: Sum) -> VarState:
        qp = HamiltonianComputer.formulate_problem(formula)

        algorithm_globals.random_seed = 1234
        cobyla = COBYLA()
        cobyla.set_options(maxiter=500)
        ry = TwoLocal(len(Computer.extract_vars(formula)), "ry", "cz", reps=3, entanglement="full")
        svqe_mes = SamplingVQE(sampler=Sampler(), ansatz=ry, optimizer=cobyla)
        svqe = MinimumEigenOptimizer(svqe_mes)
        result = svqe.solve(qp) 
        return result.variables_dict    
        


