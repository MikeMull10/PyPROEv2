from decimal import Decimal, getcontext

import numpy as np
from platypus.core import FixedLengthArray

from pprint import pprint as pp

# set the output precision to 30 places
getcontext().prec = 30


class Optimization:
    def __init__(
        self, optimization_type: str, optimization_data, time_taken: float
    ):
        self.optimization_type = optimization_type  # single, multi (wsf), or evo (evolutionary algorithms)
        self.optimization_data = optimization_data
        self.write_success = True
        # for single:
        #   'fun': objective function value (minimum)
        #   'sol': solution to the minimization (the optimal x values)
        #   'con': the value(s) of the constraint function(s)
        #   'con-names': the actual constraints i.e. (['ineq', 'F2'])
        #   'jac': the value(s) of the gradient function(s)
        # for multi:
        #   'pf': points of the pareto front
        #   'sol': x value(s) for the pareto front
        # for evo:
        #   'crs': the crossover rate
        #   'mut': the mutation rate
        #   'pop': the starting population (NSGAII/EpsMOEA)
        #   'dvi': the inner divisions (NSGAIII)
        #   'dvo': the outer divisions (NSGAIII)
        #   'eps': the epsilon(s) (EpsMOEA)
        #   'alg': the algorithm type ("NSGAII", "NSGAIII", "EpsMOEA")
        self.time_taken = time_taken

    def generate_file(self, out: str = "", _print=False) -> str:
        """Generate a FNC file from optimization output

        Parameters
        ----------
        out : string
            The full filepath of the output file
        _print : boolean
            Log the output to the console
        """

        ret = f"#################################################################\n"
        ret += (
            f"##                                                            "
            f" ##\n"
        )
        ret += (
            f"##  GimOPT             Version 5.0             Copyright 2024 "
            f" ##\n"
        )
        ret += (
            f"##      Generic Interfaced Multiobjective Optimizer           "
            f" ##\n"
        )
        ret += (
            f"##                                                            "
            f" ##\n"
        )
        ret += (
            f"##      Michael Mulligan                                      "
            f" ##\n"
        )
        ret += (
            f"##      BS: Cybersecurity                                     "
            f" ##\n"
        )
        ret += (
            f"##      Liberty University                                    "
            f" ##\n"
        )
        ret += (
            f"##                                                            "
            f" ##\n"
        )
        ret += (
            f"##      E-mail: don't email me                                "
            f" ##\n"
        )
        ret += (
            f"##                                                            "
            f" ##\n"
        )
        ret += f"#################################################################\n\n"
        ret += f"OPTIMIZER:   { self.opt_type }\n"
        ret += (
            "INPUT FILE: "
            f" { self.input_file.file_name if self.input_file is not None else 'None' }\n"
        )
        ret += f"OUTPUT FILE: { 'NONE' if out == '' else out }\n\n"
        ret += (
            f"{ self.opt_type }:"
            f" { 'SINGLE' if self.opt_type == 'SLSQP' else 'MULTI' } OPTIMIZATION\n"
        )
        ret += f"=================================================================\n"
        ret += f"Variable ( { len( self.optimization.x ) } )\n"
        ret += f"-----------------------------------------------------------------\n"
        x_values = []
        for x in self.optimization.x:
            decimal_x = Decimal(x)
            x_values.append(f"{decimal_x:.10e}")
        ret += f"1\t\t" + "\t\t".join(x_values) + "\n\n"
        ret += (
            f"Objective ( { len( self.input_file.data[ 'OBJECTIVE' ] ) } ),"
            " EQ_Constraint ("
            f" { len( self.input_file.data[ 'EQUALITY-CONSTRAINT' ] ) } ),"
            " INEQ_Constraint ("
            f" { len( self.input_file.data[ 'INEQUALITY-CONSTRAINT' ] ) } )\n"
        )
        ret += f"-----------------------------------------------------------------\n"
        c_values = []
        for c in self.constraints:
            decimal_c = Decimal(c)
            c_values.append(f"{decimal_c:.10e}")
        ret += (
            f"1\t\t{self.optimization.fun:10e}\t\t"
            + "\t\t".join(c_values)
            + "\n\n"
        )
        ret += f"Optimization Statistics\n"
        ret += f"-----------------------------------------------------------------\n"
        ret += (
            "Number of initial points:        "
            f" { self.iteration_data[ 'initial' ] }\n"
        )
        ret += (
            "Number of iterations:            "
            f" { self.iteration_data[ 'iterations' ] }\n"
        )
        ret += (
            "Number of objective evaluations: "
            f" { self.iteration_data[ 'obj_calls' ] }\n"
        )
        ret += (
            "Number of constraint evaluations:"
            f" { self.iteration_data[ 'con_calls' ] }\n\n"
        )
        ret += f"Job completed successfully\n"
        ret += f"=========================================\n"

        hours, remainder = divmod(self.time_taken, 3600)
        minutes, seconds = divmod(remainder, 60)
        ret += (
            "TOTAL WALL TIME:"
            f" {int( hours ):02}h:{int( minutes ):02}m:{int( seconds ):02}s"
        )

        if out != "":
            try:
                with open(out, "w+") as file:
                    file.write(ret)
            except:
                self.write_success = False
                # print(f"Failed to output to { out }")

        if _print:
            print(ret)

        return ret

    def generate_summary_str(self) -> str:
        """Generates an abbreviated version of the optimization results"""

        ret = f"Optimization Statistics\n"
        ret += f"-----------------------------------------------------------------\n"
        ret += (
            "Number of initial points:        "
            f" { self.iteration_data[ 'initial' ] }\n"
        )
        ret += (
            "Number of iterations:            "
            f" { self.iteration_data[ 'iterations' ] }\n"
        )
        ret += (
            "Number of objective evaluations: "
            f" { self.iteration_data[ 'obj_calls' ] }\n"
        )
        ret += (
            "Number of constraint evaluations:"
            f" { self.iteration_data[ 'con_calls' ] }\n\n"
        )
        ret += f"Job completed successfully\n"
        ret += f"=========================================\n"

        hours, remainder = divmod(self.time_taken, 3600)
        minutes, seconds = divmod(remainder, 60)
        ret += (
            "TOTAL WALL TIME:"
            f" {int( hours ):02}h:{int( minutes ):02}m:{int( seconds ):02}s"
        )
        return ret

    def format_results(self) -> str:
        """Generates an abbreviated version of the optimization results"""
        results = self.optimization_data

        ret = (
            "Optimization Statistics for"
            f" {results['alg'] if self.optimization_type == 'evo' else self.optimization_type.capitalize() + '-objective'} Optimization\n"
        )
        ret += f"-----------------------------------------------------------------\n"

        if "fun" in results:
            ret += f"Obj Func Value:\n - O1: { results[ 'fun' ] }\n\n"

        if "con" in results:
            ret += "Con Func Values:\n"
            for i, ( c, cn ) in enumerate( zip( results[ 'con' ], results[ 'con-names' ] ) ):
                ret += f" - {'EC' if cn[ 0 ] == 'eq' else 'INEC'}{i + 1} ({ cn[ 1 ] }): {c}\n"

        if "pop" in results:
            ret += f"Starting Population:\t{ results[ 'pop' ] }\n"

        if "n_parts" in results:
            ret += f"Number of partitions:\t{ results[ 'n_parts' ] }\n"

        if "crs" in results:
            ret += f"Crossover Rate:\t{ results[ 'crs' ] }%\n"

        if "mut" in results:
            ret += f"Mutation Rate:\t\t{ results[ 'mut' ] }%\n"

        if "eps" in results:
            ret += f"Epsilon Values:\t{ results[ 'eps' ] }\n"

        if "pf" in results:
            ret += "\nPareto Front Values:\n"
            ret += f"-----------------------------------------------------------------\n"
            ret += "\t\t".join( [ f"F{i + 1}" for i in range( len( results[ "pf" ][ 0 ] ) ) ] ) + "\n"
            for points in results["pf"]:
                ret += "\t".join(str(i) for i in points)
                ret += "\n"

        ret += "\nSolution(s):\n"
        ret += f"-----------------------------------------------------------------\n"

        if type(results["sol"][0]) not in [FixedLengthArray, np.ndarray]:
            for i, r in enumerate( results[ 'sol' ] ):
                ret += f" - X{i + 1}: {r}\n"
        else:
            character = 'X' if results['alg'] == 'wsf' else 'F'
            ret += "\t\t".join( [ f"{character}{i + 1}" for i in range( len( results[ "sol" ][ 0 ] ) ) ] ) + "\n"
            for points in results["sol"]:
                ret += "\t".join(str(i) for i in points)
                ret += "\n"

        ret += f"-----------------------------------------------------------------\n"
        ret += f"Job completed successfully\n"
        ret += f"=========================================\n"

        hours, remainder = divmod(self.time_taken, 3600)
        minutes, seconds = divmod(remainder, 60)
        ret += (
            "TOTAL WALL TIME:"
            f" {int( hours ):02}h:{int( minutes ):02}m:{int( seconds ):02}s"
        )
        return ret
    
    def __str__(self):
        return self.format_results()
