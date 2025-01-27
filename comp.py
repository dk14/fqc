from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod


# DSL

@dataclass
class Zero:
    pass

@dataclass
class Sum:
    a: Sum | Zero
    b: Mul


Const = int
VarName = str # reference to a binary variable

@dataclass
class Mul:
    a: Const
    b: VarName

VarState = dict[str, int]
VarNames  = list[str]

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