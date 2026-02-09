from components.inputfnc2 import InputFile
from components.optimize import Optimize as Opt
from components.optimize import EvolutionType
from multiprocessing import Queue
from enum import Enum


class METHOD(Enum):
    Single  = 0
    Multi   = 1
    NSGAII  = 2
    NSGAIII = 3

def run(queue: Queue, method: METHOD, file: str, settings: dict):
    file_str = file
    file: InputFile = InputFile(file, is_file=False)

    res = None
    ### --- SciPy ---
    match method:
        case METHOD.Single:
            res = Opt.single(file, grid_size=settings.get('gridsize', 5), tolerance=settings.get('tolerance', 1e-6))
        case METHOD.Multi:
            res = Opt.multi(
                input=file,
                min_weight=settings.get('min_weight', 0.01),
                increment=settings.get('increment', 0.01),
                grid_size=settings.get('gridsize', 5),
                tolerance=settings.get('tolerance', 1e-6),
                ftol=settings.get('ftol', 1e-6)
            )
        case METHOD.NSGAII:
            res = Opt.evolve(
                file,
                generations=settings.get('generations', 1000),
                population=settings.get('population', 200),
                crossover_rate=settings.get('crossover', 0.9),
                mutation_rate=settings.get('mutation', 0.01),
                partitions=settings.get('partition', 100),
                algorithm=EvolutionType.NSGAII,
            )
        case METHOD.NSGAIII:
            if len(file.objectives) <= 1:
                queue.put(["Error"])
                return

            res = Opt.evolve(
                file,
                generations=settings.get('generations', 1000),
                population=settings.get('population', 200),
                crossover_rate=settings.get('crossover', 0.9),
                mutation_rate=settings.get('mutation', 0.01),
                partitions=settings.get('partition', 100),
                algorithm=EvolutionType.NSGAIII,
            )
    
    if res:
        res.fnc = file_str
    queue.put([res])
