from __future__ import annotations
from handlers.function import Function


class Variable:
    def __init__(self, _symbol, _min: float, _max: float, _type, _increment: float=1e-6):
        self.symbol = _symbol
        self.min, self.max = float(_min), float(_max)
        self.type      = _type
        self.increment = float(_increment)
    
    def __repr__(self):
        return f"{self.symbol}: ({self.min}, {self.max}), {self.type}, {self.increment}"

class Constant:
    def __init__(self, _symbol: str, _value: float):
        self.symbol = _symbol
        self.value  = _value
    
    def __repr__(self):
        return f"{self.symbol}: {self.value}"

class Objective:
    def __init__(self, _symbol: str, _value: str):
        self.symbol = _symbol
        self.value  = _value

class Constraint:
    def __init__(self, _symbol: str, _function: Function):
        self.symbol   = _symbol
        self.function = _function

#TODO: Handle F1 vs F11 etc
class Node:
    def __init__(self, value: str, parent: Node, functions: list[Function]):
        self.value: str = value
        self.parent: Node = parent
        self.children: list[Node] = []

        self.error = False

        self.level = 0
        curr: Node = self
        while (curr := curr.parent):
            self.level += 1
            if self.value == curr.value:
                self.error = True
                return

        for f in functions:
            if f.name == self.value:
                this_func = f.text
        
        children = []
        for f in functions:
            if f.name in this_func:
                children.append(f.name)
        
        for c in children:
            self.children.append(Node(c, self, functions))
    
    def find_max(self):
        if len(self.children) == 0:
            return self.level

        return max(child_max.find_max() for child_max in self.children)

    def error_exists(self):
        if len(self.children) == 0:
            return self.error
        
        return True in [child.error_exists() for child in self.children]

    def __repr__(self):
        indent = '  ' * self.level
        result = f"{indent}{self.value}\n"
        for child in self.children:
            result += repr(child)
        return result
