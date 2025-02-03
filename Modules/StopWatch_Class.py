import time

class StopWatch():
    def __init__(self):
        self.reset()

    def reset(self)-> float:
        self.start_time = time.time()

    def getTime(self) -> float:
        if self.start_time:
            return time.time() -self.start_time
        
