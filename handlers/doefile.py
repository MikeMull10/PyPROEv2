from pprint import pprint as pp
import numpy as np


class DOEFile:
    def __init__(self, file: str, is_str: bool = False) -> None:
        self.file_name = file
        self.is_str = is_str

        self.__read_data()

    def __read_data(self) -> None:
        _data = []
        lines = []

        if self.is_str:
            lines = self.file_name.split('\n')
        else:
            with open(self.file_name, "r+") as file:
                for line in file:
                    lines.append(line)
        
        for line in lines:
            line = line.strip()

            if line == "" or line[0] == "#":
                continue

            _data.append(line)

        _data[ 0 ] = [ int(_) for _ in _data[0].split() ]
        
        points, vars, levels, funcs = _data[ 0 ]

        var_data = []
        func_data = []

        for d in _data[1:]:
            #  check if the line is an actual point or describing a VARIABLE or FUNCTION
            if d[0] == 'X':
                continue
            elif d[0] == 'F':
                continue

            d = [ float(_) for _ in d.split() ][1:]
            
            while len(d) > vars + funcs:  # get rid of the index and theoretical X values (if they are there)
                d.pop(0)
            
            var_data.append( d[:vars] )
            func_data.append( d[vars:] )
        
        self.independent = np.array(var_data)
        self.dependent = np.array(func_data)
    
    def get_var_data(self) -> list:
        ret = []
        for ind in range( self.independent.shape[1] ):
            ret.append( [ np.min( self.independent[ :, ind ] ), np.max( self.independent[ :, ind ] ) ] )
        
        return ret
