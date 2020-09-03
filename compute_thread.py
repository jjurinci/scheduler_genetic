from threading import Thread
from genetic_algorithm import solver_io

class Compute(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        solver_io.run(self.data)