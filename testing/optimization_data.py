from enum import Enum
from testing.inputfnc2 import InputFile
import numpy as np

class Opt(Enum):
    FAILED  = 0
    SUCCESS = 1

class Optimization:
    def __init__(self, status: Opt=Opt.SUCCESS, data: any=None, fnc: InputFile=None):
        self.status = status
        self.error_message = ""
        self.data: dict = None
        self.fnc: InputFile = fnc
        
        if not status:
            self.error_message = data
        else:
            self.data = data
    
    def __repr__(self):
        if not self.status:
            return f"FAILED: {self.error_message}"

        return self.format_results()
    
    def __getitem__(self, key):
        return self.data.get(key, None)
    
    def format_results(self) -> str:
        if isinstance(self.fnc, str):
            self.fnc = InputFile(self.fnc, is_file=False)

        if self.status == Opt.FAILED:
            return "FAILED"

        results = self.data.get('data', None)
        if not results or not self.fnc: return ""

        run_type = self.data.get('type', None)

        ret = f"Optimization Statistics for {run_type.upper()}\n"
        ret += f"{'—' * 64}\n\n"

        if run_type == 'single':
            ret += f"Objective Function: \n"
            ret += f" - {self.fnc.objectives[0].name.upper()} ({self.fnc.objectives[0].text.upper()}): {results.fun}\n\n"
            ret += f"Solution(s):\n"
            ret += f"{'—' * 64}\n"
            for i, var in enumerate(self.fnc.variables):
                ret += f" - {var.symbol}: {results.x[i]}\n"
        
        elif run_type == 'multi':
            ret += f"Objective Functions ({', '.join(obj.name for obj in self.fnc.objectives)}):\n"

            points = np.array(results['points'])
            precision = max(len(str(x)) for x in points.flat) + 1
            for i, point in enumerate(points):
                ret += '\t'.join([f"{p:<{precision}}" for p in point]) + '\n'
        else:
            ret += f"Objective Functions ({', '.join(obj.name for obj in self.fnc.objectives)}):\n"


        ret += f"{'—' * 64}\n"
        ret += f"Job completed successfully\n"
        ret += f"=================================\n"

        hours, remainder = divmod(self.data['time'], 3600)
        minutes, seconds = divmod(remainder, 60)
        ret += (
            "TOTAL TIME ELAPSED:"
            f" {int( hours ):02}h:{int( minutes ):02}m:{int( seconds ):02}s"
        )
    
        return ret
