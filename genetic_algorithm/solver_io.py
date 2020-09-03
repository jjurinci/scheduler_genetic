import json
import numpy as np
from genetic_algorithm import data_transformer as dt
from collections import defaultdict, namedtuple
from genetic_algorithm.optimizer.optimizer import Optimizer
from pymongo import MongoClient

def run(data):
    classrooms = data["data"]["classrooms"]
    professors = data["data"]["professors"]
    semesters = data["data"]["semesters"]
    rasps = frozenset(dt.transform(data))
    user_data = (data["data"]["userId"], data["data"]["solverId"])
    
    for i in range(len(classrooms)):
        classrooms[i]["capacity"] = int(classrooms[i]["capacity"])

    
    OPT = Optimizer(rasps, classrooms, professors, semesters, user_data)
    samples = OPT.generate_random_sample(10)
    if not samples:
        return
    after_iterate_samples = OPT.iterate(samples, 500)
