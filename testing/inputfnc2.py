from testing.fnc_objects import Variable, Constant, Function, BasicFunction, Node
from scipy.optimize import NonlinearConstraint

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import re

import logging
from pprint import pprint as pp

SECTIONS = ["VARIABLE", "CONSTANT", "OBJECTIVE", "EQUALITY-CONSTRAINT", "INEQUALITY-CONSTRAINT", "FUNCTION", "GRADIENT"]

def clean_data(lines: list[str]):
    ret = []

    for line in lines:
        line = line.partition("#")[ 0 ].strip().replace("\t", " ")

        if len(line) > 0:
            ret.append(line)
    
    return ret

def split_functions(text: str):
    lines = text.splitlines()
    functions = []
    current = ""
    paren_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        current += " " + line
        paren_count += line.count('(') - line.count(')')

        # If we have balanced parentheses and a semicolon at the end, split
        if paren_count == 0 and ';' in line:
            parts = current.split(';')
            for p in parts[:-1]:
                if p.strip():
                    functions.append(p.strip())
            current = parts[-1].strip()  # Remaining partial expression

    # Any leftover (without semicolon) — treat as incomplete but add anyway
    if current.strip():
        functions.append(current.strip())

    return functions

class InputFile:
    def __init__(self, input_str: str, is_file: bool=True, check_nums: bool=True):
        self.file_str   = input_str
        self.is_file    = is_file
        self.check_nums = check_nums

        self.error:        bool = False
        self.error_message: str = ""

        self.variables: list[Variable] = []
        self.constants: list[Constant] = []
        self.objectives: list[Function] = []
        self.equality_constraints: list[Function] = []
        self.inequality_constraints: list[Function] = []
        self.functions: list[Function] = []
        self.gradients: list[Function] = []
        self.__read_data()

    def __expr__(self) -> str:
        if self.error:
            return self.error_message

        return f"VARIABLES -> {self.variables}\nCONSTANTS -> {self.constants}\nOBJECTIVES -> {self.objectives}\nEQUALITY-CONSTRAINTS -> {self.equality_constraints}\nINEQUALITY-CONSTRAINTS -> {self.inequality_constraints}\nFUNCTIONS -> {self.functions}\nGRADIENTS -> {self.gradients}"

    def __read_data(self):
        if self.is_file:
            try:
                with open(self.file_str, "r+") as file:
                    data = clean_data(file)
            except Exception as e:
                self.error = True
                self.error_message = str(e)
                return
        else:
            data = clean_data(self.file_str.split('\n'))

        flag = -1
        saved = {k: 0 for k in SECTIONS}
        dataset = [[] for _ in range(len(SECTIONS))]
        for line in data:
            for i, s in enumerate(SECTIONS):
                if f"*{s}" in line:
                    flag = i
                    if self.check_nums:
                        if ':' not in line:
                            self.error = True
                            self.error_message = f"Missing number of component for {s}."
                            return
                        _, number = line.split(':', 1)
                        saved[s.upper()] = int(number)
                    break
            else:
                if flag == -1: continue
                dataset[flag].append(line)
        
        self._variables, self._constants, self._objectives, self._equality_constraints, self._inequality_constraints, self._functions, self._gradients = dataset

        ### Checks
        if self.check_nums:
            if len(self._variables) != saved["VARIABLE"]:
                self.error = True
                self.error_message = f"Incorrect number of components for VARIABLE. Have {len(self._variables)} expected {saved["VARIABLE"]}."
                return
            elif len(self._functions) != saved["FUNCTION"]:
                self.error = True
                self.error_message = f"Incorrect number of components for FUNCTION. Have {len(self._functions)} expected {saved["FUNCTION"]}."
                return
            elif len(self._objectives) != saved["OBJECTIVE"]:
                self.error = True
                self.error_message = f"Incorrect number of components for OBJECTIVE. Have {len(self._objectives)} expected {saved["OBJECTIVE"]}."
                return

        ### VARIABLES
        for var in self._variables:
            try:
                d = [v.strip() for v in var.split(':')[ 1 ].split(',')]
                if len(d) < 3:
                    d.append(None)
                if len(d) < 4:
                    d.append(1e-6)

                d[0], d[1], d[3] = float(d[0]), float(d[1]), float(d[3])
                
                self.variables.append(Variable(var.split(':')[ 0 ], *d))
            except IndexError:
                self.error = True
                self.error_message = f"Malformed variable: '{var}'"
                return
            except ValueError:
                self.error = True
                self.error_message = f"Invalid variable value: '{var}'"
                return
        
        if len(self.variables) == 0:
            self.error = True
            self.error_message = "No variables."
            return
        
        self.variables = sorted(self.variables, key=lambda v: v.symbol)
        
        if self.check_nums and (len(self._constants)) != saved["CONSTANT"]:
            self.error = True
            self.error_message = f"Incorrect number of components for CONSTANT. Have {len(self._constants)} expected {saved["CONSTANT"]}"
            return
    
        ### CONSTANTS
        for con in self._constants:
            try:
                name, value = [c.strip() for c in con.replace(';', '').split('=', 1)]
                self.constants.append(Constant(name, value))
            except ValueError:
                self.error = True
                self.error_message = f"Malformed constant: '{con}'"
                return
            
        ### FUNCTIONS
        #TODO: Check for ';'
        funs: list[str] = split_functions("\n".join(self._functions))
        objs: list[str] = split_functions("\n".join(self._objectives))
        eqcs: list[str] = split_functions("\n".join(self._equality_constraints))
        inqs: list[str] = split_functions("\n".join(self._inequality_constraints))

        function_type_dict = {
            'fun': [f.split('=')[0].strip().lower() for f in funs],
            'obj': [f.split('=')[0].strip().lower() for f in objs],
            'eqc': [f.split('=')[0].strip().lower() for f in eqcs],
            'iqc': [f.split('=')[0].strip().lower() for f in inqs],
        }

        basic_funcs: list[BasicFunction] = []
        for function_type in [funs, objs, eqcs, inqs]:
            for fun in function_type:
                k, v = fun.split('=')
                basic_funcs.append(BasicFunction(k.strip(), v.strip()))

        for basic in basic_funcs:
            node = Node(basic.name, None, basic_funcs)
            if node.error_exists():
                self.error = True
                self.error_message = f"Circular function found in: {basic.name}"
                return

            basic.level = node.find_max()
        
        function_constants = {con.symbol: con.value for con in self.constants}
        for func in sorted(basic_funcs, key=lambda x: x.level):
            for function_type, array in zip(['fun', 'obj', 'eqc', 'iqc'], [self.functions, self.objectives, self.equality_constraints, self.inequality_constraints]):
                if func.name.lower() in function_type_dict[function_type]:
                    array.append(Function(func.name.lower(), func.text, [var.symbol for var in self.variables], function_constants))

        if len(self.functions) == 0:
            self.error = True
            self.error_message = "No functions."
            return

        elif len(self.objectives) == 0:
            self.error = True
            self.error_message = "No objectives."
            return
    
    def get_bounds(self):
        return [np.array([v.min, v.max]) for v in self.variables]
    
    def get_equality_constraints(self) -> list[NonlinearConstraint]:
        ret: list[NonlinearConstraint] = []
        
        for eq in self.equality_constraints:
            ret.append(NonlinearConstraint(
                eq,
                0,
                0,
                jac=eq.jacobian,
            ))

        return ret
    
    def get_inequality_constraints(self) -> list[NonlinearConstraint]:
        ret: list[NonlinearConstraint] = []

        for ineq in self.inequality_constraints:
            ret.append(NonlinearConstraint(
                ineq,
                -np.inf,
                0,
                jac=ineq.jacobian,
            ))

        return ret

    def get_nonlinear_constraints(self) -> list[NonlinearConstraint]:
        ret: list[NonlinearConstraint] = []
        
        ret += self.get_equality_constraints()
        ret += self.get_inequality_constraints()
        
        return ret
