import re
from pprint import pprint as pp

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

SECTIONS = ["VARIABLE", "CONSTANT", "OBJECTIVE", "EQUALITY-CONSTRAINT", "INEQUALITY-CONSTRAINT", "FUNCTION", "GRADIENT"]

def clean_data(lines: list[str]):
    ret = []

    for line in lines:
        try:
            i = line.index("#")
        except:
            i = -1
        
        line = line[:i].strip().replace("\t", " ")

        if len(line) > 0:
            ret.append(line)
    
    return ret

class InputFile:
    def __init__(self, input_str: str, is_file: bool=True):
        self.file_str = input_str
        self.is_file  = is_file

        self.error:        bool = False
        self.error_message: str = ""

        self.__read_data()

    def __read_data(self):
        if self.is_file:
            try:
                with open(self.file_str, "r+") as file:
                    data = clean_data(file)
            except Exception as e:
                self.error = True
                self.error_message = e
                return
        else:
            data = clean_data(self.file_str)

        flag = -1
        dataset = [[] for i in range(len(SECTIONS))]
        for i, line in enumerate(data):
            for ii, s in enumerate(SECTIONS):
                if f"*{s}" in line:
                    flag = ii
                    break
            else:
                if flag == -1: continue
                dataset[flag].append(line)
        
        pp(dataset)
