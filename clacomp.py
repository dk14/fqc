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
        dict = [{vars[i]: v[i] for i in range(len(vars))} for v in combos]
        values = [(state, ClassicComputer.calculate(formula, state)) for state in dict]
        return max(values, key=lambda x: x[1])[0]
        
