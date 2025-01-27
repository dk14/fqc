from dataclasses import dataclass

from comp import *
import itertools

class ClassicComputer(Computer):

    def calculate(formula: Sum, varstate: VarState, acc: int = 0) -> int: 
         while True:
            match formula:
                case Sum(Zero(), Mul(x, name)):
                    return x * varstate[name] + acc
                case Sum(next, Mul(x, name)):
                    formula = next
                    acc = x * varstate[name] + acc

    def maximize(self, formula: Sum) -> VarState:
        vars = Computer.extract_vars(formula)
        combos = list(itertools.product([0, 1], repeat = len(vars)))
        dict = list(map(lambda v: {vars[i]: v[i] for i in range(len(vars))}, combos))
        values = list(map(lambda state: (state, ClassicComputer.calculate(formula, state)), dict))
        return max(values, key=lambda x: x[1])[0]
        
