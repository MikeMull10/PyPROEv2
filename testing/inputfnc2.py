import re
from pprint import pprint as pp

from testing.fnc_objects import Variable, Constant, Objective, Constraint, Function

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

import logging

SECTIONS = ["VARIABLE", "CONSTANT", "OBJECTIVE", "EQUALITY-CONSTRAINT", "INEQUALITY-CONSTRAINT", "FUNCTION", "GRADIENT"]

def clean_data(lines: list[str]):
    ret = []

    for line in lines:
        line = line.partition("#")[ 0 ].strip().replace("\t", " ")

        if len(line) > 0:
            ret.append(line)
    
    return ret

class InputFile:
    def __init__(self, input_str: str, is_file: bool=True, check_nums: bool=True):
        self.file_str   = input_str
        self.is_file    = is_file
        self.check_nums = check_nums

        self.error:        bool = False
        self.error_message: str = ""

        self.variables, self.constants, self.objectives, self.equality_constraints, self.inequality_constraints, self.functions, self.gradients = [[] for _ in range(len(SECTIONS))]
        self.__read_data()

    def __str__(self) -> str:
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
            data = clean_data(self.file_str)

        logging.debug(data)

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
        
        ### VARIABLES
        if self.check_nums and len(self._variables) != saved["VARIABLE"]:
            self.error = True
            self.error_message = f"Incorrect number of components for VARIABLE. Have {len(self._variables)} expected {saved["VARIABLE"]}."
            return

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
        
        ### CONSTANTS
        for con in self._constants:
            try:
                name, value = [c.strip() for c in con.replace(';', '').split('=', 1)]
                self.constants.append(Constant(name, value))
            except ValueError:
                self.error = True
                self.error_message = f"Malformed constant: '{con}'"
                return
        
        ### OBJECTIVE FUNCTION
        for obj in self._objectives:
            pass
