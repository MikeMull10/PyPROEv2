from enum import Enum

class Opt(Enum):
    FAILED  = 0
    SUCCESS = 1

class Optimization:
    def __init__(self, status: Opt=Opt.SUCCESS, data: any=""):
        self.status = status
        self.error_message = ""
        self.data = None
        
        if not status:
            self.error_message = data
        else:
            self.data = data
    
    def __repr__(self):
        if not self.status:
            return f"FAILED: {self.error_message}"

        return str(self.data)

    def __getitem__(self, key):
        return self.data[key]
