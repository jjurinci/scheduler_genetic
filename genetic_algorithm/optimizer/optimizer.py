import math
import random
import copy
import itertools
import numpy as np
import genetic_algorithm.optimizer.db_dml as db_dml
import genetic_algorithm.optimizer.optimizer_stop as optimizer_stop
import genetic_algorithm.optimizer.genetic_operators as genetic_operators
from collections import defaultdict, namedtuple
from tqdm import tqdm
from multiprocessing import Pool
from itertools import product

sys_random = random.SystemRandom()
Dvorana = namedtuple('Dvorana', ['capacity', 'hasComputers', 'free'])
Nastavnik = namedtuple('Nastavnik', ['free'])
Studij = namedtuple('Studij', ['numStudents', 'free'])

class Optimizer:
    def __init__(self, raspovi, dvorane, nastavnici, studiji, user_data):
        self.user_data = user_data
        self.raspovi = raspovi
        self.dvorane = dict()
        self.nastavnici = dict()
        self.studiji = dict()
        self.svi_semestri_raspa = dict()
        self.classroom_name = dict()

        for dv in dvorane:
            id_dvorane, kapacitet, racunalna = dv["_id"], dv["capacity"], dv["hasComputers"]
            self.classroom_name[id_dvorane] = dv["name"]
            if id_dvorane not in self.dvorane:
                self.dvorane[id_dvorane] = Dvorana(kapacitet, racunalna, np.zeros(shape=(5, 16), dtype=np.int))
            for dan, sat in dv["free"]:
                self.dvorane[id_dvorane].free[dan-1, sat-1] = 1

        for nastavnik in nastavnici:
            id_nastavnika = nastavnik["_id"]
            if id_nastavnika not in self.nastavnici:
                self.nastavnici[id_nastavnika] = Nastavnik(np.zeros(shape=(5, 16), dtype=np.int))
            for dan, sat in nastavnik["free"]:
                self.nastavnici[id_nastavnika].free[dan-1, sat-1] = 1

        for studij in studiji:
            semestar = studij["_id"]
            self.studiji[semestar] = Studij(studij["numStudents"], np.ones(shape=(5, 16), dtype=np.int))
        
        #svi semestri rasp_id-a
        for rasp in self.raspovi:
            rasp_id = self.rasp_id(rasp)
            self.svi_semestri_raspa[rasp_id] = [rasp]
            for rasp2 in self.raspovi:
                if rasp == rasp2:
                    continue
                rasp2_id = self.rasp_id(rasp2)
                if rasp_id == rasp2_id:
                    self.svi_semestri_raspa[rasp_id].append(rasp2)
    
    def rasp_id(self, rasp):
        return (rasp.name, rasp.type, rasp.group)
    
    def semester_id(self, semester):
        return semester.semesterId

    def get_availables(self):
        availables = []
        for dvorana in self.dvorane:
            for dan in range(5):
                for sat in range(16):
                    if self.dvorane[dvorana].free[dan][sat] == 1:
                        availables.append((dvorana, dan, sat))
        return availables

    def grade(self, raspored):
        ocjena, warnings = 0, []
        dvorane, nastavnici, studiji = copy.deepcopy(self.dvorane), copy.deepcopy(self.nastavnici), \
                                       copy.deepcopy(self.studiji)

        vec_obradeno = {}
        for rasp, (dvorana, dan, sat) in raspored.items():
            rasp_id = self.rasp_id(rasp)
            semestar = self.semester_id(rasp)
            studiji[semestar].free[dan, sat:sat+rasp.duration] -= 1

            if rasp_id not in vec_obradeno:
                dvorane[dvorana].free[dan,sat:sat+rasp.duration] -= 1
                nastavnici[rasp.professorId].free[dan,sat:sat+rasp.duration] -= 1
            vec_obradeno[rasp_id] = True

        vec_obradeno = {}
        dvorana_ocjena, nastavnik_ocjena, studij_ocjena, kapacitet_ocjena, rac_ocjena = 0, 0, 0, 0, 0
        for rasp, (dvorana, dan, sat) in raspored.items():
            rasp_id = self.rasp_id(rasp)
            semestar = self.semester_id(rasp)
            dvorana_cnt = sum(dvorane[dvorana].free[dan, sat:sat+rasp.duration] < 0)
            nastavnik_cnt = sum(nastavnici[rasp.professorId].free[dan, sat:sat+rasp.duration] < 0)
            studiji_cnt = sum(studiji[semestar].free[dan, sat:sat+rasp.duration] < 0)

            # kolizije studija
            skor_studija = studiji_cnt * rasp.numStudents
            studij_ocjena -= skor_studija
            ocjena -= skor_studija

            # ignoriraj isti rasp (ista dvorana, isti nastavnik, isti dan,sat ali drugi semestar)
            if rasp_id in vec_obradeno:
                continue
            vec_obradeno[rasp_id] = True

            # kolizije dvorane
            skor_dvorane = dvorana_cnt * rasp.numStudents
            dvorana_ocjena -= skor_dvorane
            ocjena -= skor_dvorane

            # kolizije nastavnika
            skor_nastavnika = nastavnik_cnt * rasp.numStudents
            nastavnik_ocjena -= skor_nastavnika
            ocjena -= skor_nastavnika

            # nedostatan kapacitet
            if dvorane[dvorana].capacity < rasp.numStudents:
                kapacitet_ocjena -= rasp.numStudents
                ocjena -= rasp.numStudents

            # racunalni rasp u neracunalnoj dvorani
            if rasp.needsComputers and not dvorane[dvorana].hasComputers:
                rac_ocjena -= rasp.numStudents
                ocjena -= rasp.numStudents
        
        return (ocjena, dvorana_ocjena, nastavnik_ocjena, studij_ocjena, kapacitet_ocjena, rac_ocjena)

    def generate_random_sample(self, N):
        best = -50000
        samples = []
        availables = self.get_availables()

        for _ in range(10*N):
            avs = availables.copy()
            raspored = {}
            vec_obradeni = {}
            for rasp in self.raspovi:
                if self.rasp_id(rasp) in vec_obradeni:
                    continue

                okay = False
                stuck_i, stuck_max = 0, 1000
                while not okay:
                    stuck_i+=1
                    if stuck_i == stuck_max: return []
                    slot = sys_random.choice(avs)
                    if (slot[2] + rasp.duration) <= 16:
                        cnt = 0
                        for j in range(slot[2], slot[2]+rasp.duration):
                            if (slot[0], slot[1], j) in avs:
                                cnt += 1
                            else:
                                break
                        if cnt == rasp.duration:
                            okay = True
                            stuck_i = 0

                rasp1_id = self.rasp_id(rasp)
                vec_obradeni[rasp1_id] = True
                rasps_sems = self.svi_semestri_raspa[rasp1_id]
                for rasp_sem in rasps_sems:
                    raspored[rasp_sem] = slot

                for j in range(slot[2], slot[2]+rasp.duration):
                    avs.remove((slot[0], slot[1], j))

            samples.append((self.grade(raspored), raspored))
            best = max(samples[len(samples)-1][0][0], best)

        samples.sort(key=lambda x: x[0], reverse=True)
        return samples[:N]
    
    def racunala_shuffle_and_grade(self, x):
        x1 = genetic_operators.racunala_shuffle(self, x)
        return self.grade(x1), x1

    def kapacitet_shuffle_and_grade(self, x):
        x1 = genetic_operators.kapacitet_shuffle(self, x)
        return self.grade(x1), x1

    def nastavnik_shuffle_and_grade(self, x):
        x1 = genetic_operators.nastavnik_shuffle(self, x)
        return self.grade(x1), x1

    def studiji_shuffle_and_grade(self, x):
        x1 = genetic_operators.studij_shuffle(self, x)
        return self.grade(x1), x1

    def cross_and_grade(self, x):
        x1 = genetic_operators.crossover(self, x[0], x[1])
        return self.grade(x1), x1

    def mutate_and_grade(self, x):
        x1 = genetic_operators.mutate(self, x)
        return self.grade(x1), x1
    
    def swap_and_grade(self,x):
        return genetic_operators.swapper(self, x)
    
    def iterate(self, sample, generations=100, starting_generation=1, population_cap=512):
        BEST = (sample[0][0], sample[0][1].copy())
        
        zero_grade_reached_cnt = 0
        for generation in range(starting_generation, starting_generation+generations):
            if BEST[0][0] == 0: zero_grade_reached_cnt+=1
            if BEST[0][0] == 0 and zero_grade_reached_cnt == 5:
                optimizer_stop.end_process(self, sample)
                return
            
            if optimizer_stop.front_end_requested_stoppage(self):
                optimizer_stop.end_process(self, sample)
                return
            
            with Pool(7) as p:
                the_samples = [s[1] for s in sample]

                mutations = p.map(self.mutate_and_grade, the_samples[:10])
                nastavnik_shuffle = p.map(self.nastavnik_shuffle_and_grade, the_samples[:10])
                studiji_shuffle = p.map(self.studiji_shuffle_and_grade, the_samples[:50])
                kapacitet_shuffle = p.map(self.kapacitet_shuffle_and_grade, the_samples[:10])
                racunala_shuffle = p.map(self.racunala_shuffle_and_grade, the_samples[:10])
                
                if optimizer_stop.front_end_requested_stoppage(self):    
                    optimizer_stop.end_process(self, sample)
                    return
                
                if BEST[0][0] > -800:
                    swapper = p.map(self.swap_and_grade, the_samples[:10])

            sample += mutations+nastavnik_shuffle+studiji_shuffle+kapacitet_shuffle+racunala_shuffle
            if BEST[0][0] > - 800:
                sample += swapper
                swa = map(lambda x: x[0][0], swapper)
                swa_b = max(swa)
                
            mut = map(lambda x: x[0][0], mutations)
            nas = map(lambda x: x[0][0], nastavnik_shuffle)
            stu = map(lambda x: x[0][0], studiji_shuffle)
            kap = map(lambda x: x[0][0], kapacitet_shuffle)
            rac = map(lambda x: x[0][0], racunala_shuffle)
             
            mut_b, nas_b, stu_b, kap_b, rac_b = max(mut), max(nas), max(stu), max(kap), max(rac)
            #print("mut: ", mut_b, "nas:", nas_b, "stu:", stu_b, "kap: ", kap_b, "rac: ", rac_b)

            sample = [x for i, x in enumerate(sample) if i == sample.index(x)]
            sample.sort(key=lambda x: x[0][0], reverse=True)
            sample = sample[0:population_cap]
            if sample[0][0][0] > BEST[0][0]:
                BEST = (sample[0][0], sample[0][1].copy())
                #print(f"{generation}, {BEST[0][0]}, | dvorana: {BEST[0][1]}, nastavnik: {BEST[0][2]}, studij: {BEST[0][3]}, kapacitet: {BEST[0][4]}, rac: {BEST[0][5]}")

                grade = {
                    'generation': generation,
                    'best': BEST[0][0].item(), #numpy int to int
                    'classrooms': BEST[0][1].item(),
                    'professors': BEST[0][2].item(),
                    'semesters': BEST[0][3].item(),
                    'capacity': BEST[0][4],
                    'computers': BEST[0][5],
                    'solverId': self.user_data[1],
                    'userId': self.user_data[0]
                }
                result = db_dml.insert_one('solver_results', False, grade)
                
        optimizer_stop.end_process(self, sample)
