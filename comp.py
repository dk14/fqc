from dataclasses import dataclass
from abc import ABC, abstractmethod

# DSL

@dataclass
class Zero

@dataclass
class Sum:
    a: Sum | Zero
    b: Mul


type Const = int
type VarName = string # reference to a binary variable

@dataclass
class Mul:
    a: Const
    b: VarName

type VarState = Dict[string, int]
type VarNames  = list[string]

class Computer(ABC):

    def extract_vars(formula: Sum, acc: VarNames = []) -> VarNames:
        while True:
            match formula:
                case Sum(Zero(), Mul(_, name)):
                    return [name] + acc
                case Sum(next, Mul(_, name)):
                    formula = next
                    acc = [name] + acc

    @abstractmethod
    def maximize(self, formula: Sum) -> VarState:
        # extract vars
        # bruteforce evaluations
        # find minimum
        pass