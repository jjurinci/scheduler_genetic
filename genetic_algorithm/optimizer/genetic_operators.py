import copy
import random

sys_random = random.SystemRandom()
def mutate(self, schedule):
    rasp0 = sys_random.choice(list(self.raspovi))

    # izbaci random rasp iz timetable-a
    schedule.pop(rasp0)
    avs = set(self.get_availables())

    # za sve ostale rasp-ove zauzmi available (dv,dan,sat)
    for rasp, (dvorana, dan, sat) in schedule.items():
        terms = {(dvorana, dan, sat+i) for i in range(rasp.duration)}
        avs -= terms

    nonavs = set()
    for (dvorana, dan, sat) in avs:
        if any((dvorana, dan, sat+i) not in avs for i in range(1, rasp0.duration)):
            nonavs.add((dvorana, dan, sat))
    avs -= nonavs

    slot = sys_random.choice(list(avs))
    rasp0_id = self.rasp_id(rasp0)
    rasps_sems = self.svi_semestri_raspa[rasp0_id]
    for rasp_sem in rasps_sems:
        schedule[rasp_sem] = slot

    # ubacivanje izbacenog random rasp-a u novo random vrijeme
    schedule[rasp0] = slot
    return schedule

# t1 = raspored1, t2 = raspored2 | raspored[rasp] = (dv,dan,sat)
def crossover(self, t1, t2):
    vec_obradeno = {}
    for rasp in t1:
        rasp_id = self.rasp_id(rasp)
        if rasp_id in vec_obradeno:
            continue
        vec_obradeno[rasp_id] = True

        hashable_rasp = rasp
        old_slot = t1[hashable_rasp]
        new_slot = sys_random.choice([t1[hashable_rasp], t2[hashable_rasp]])
        if old_slot == new_slot:
            continue

        rasps_sems = self.svi_semestri_raspa[rasp_id]
        for rasp_sem in rasps_sems:
            t1[rasp_sem] = new_slot

    return t1  # za svaki rasp u t1 stavlja random vrijeme od drugog ili svoje

def racunala_shuffle(self, schedule):
    obradeno = {}
    for rasp, (dvorana, dan, sat) in schedule.items():
        rasp_id = self.rasp_id(rasp)
        if rasp_id in obradeno:
            continue

        if (not self.dvorane[dvorana].hasComputers and rasp.needsComputers):
            avs = set(self.get_availables())
            for rasp_, (dvorana_, dan_, sat_) in schedule.items():
                terms = {(dvorana, dan, sat+i) for i in range(rasp_.duration)}
                avs -= terms

            remavs = avs.copy()
            nonavs = set()

            semester = self.semester_id(rasp)
            for (dvorana, dan, sat) in avs:
                if any((dvorana, dan, sat+i) not in avs for i in range(1, rasp.duration)) or \
                   any(self.dvorane[dvorana].free[dan, sat:sat+rasp.duration] != 1) or \
                   any(self.nastavnici[rasp.professorId].free[dan, sat:sat+rasp.duration] != 1) or \
                   any(self.studiji[semester].free[dan, sat:sat+rasp.duration] != 1) or \
                   self.dvorane[dvorana].capacity < rasp.numStudents or \
                   (not self.dvorane[dvorana].hasComputers and rasp.needsComputers):
                        nonavs.add((dvorana, dan, sat))

            avs -= nonavs
            if len(avs) == 0:
                continue
            try: 
                slot = sys_random.choice(list(avs))
            except:
                continue

            rasps_sems = self.svi_semestri_raspa[rasp_id]
            obradeno[rasp_id] = True
            for rasp_sem in rasps_sems:
                schedule[rasp_sem] = slot

    return schedule

def kapacitet_shuffle(self, schedule):
    obradeno = {}
    for rasp, (dvorana, dan, sat) in schedule.items():
        rasp_id = self.rasp_id(rasp)
        if rasp_id in obradeno:
            continue
        
        if self.dvorane[dvorana].capacity < rasp.numStudents:
            avs = set(self.get_availables())
            for rasp_, (dvorana_, dan_, sat_) in schedule.items():
                terms = {(dvorana, dan, sat+i) for i in range(rasp_.duration)}
                avs -= terms

            remavs = avs.copy()
            nonavs = set()

            semester = self.semester_id(rasp)
            for (dvorana, dan, sat) in avs:
                if any((dvorana, dan, sat+i) not in avs for i in range(1, rasp.duration)) or \
                   any(self.dvorane[dvorana].free[dan, sat:sat+rasp.duration] != 1) or \
                   any(self.nastavnici[rasp.professorId].free[dan, sat:sat+rasp.duration] != 1) or \
                   any(self.studiji[semester].free[dan, sat:sat+rasp.duration] != 1) or \
                   self.dvorane[dvorana].capacity < rasp.numStudents or \
                   (not self.dvorane[dvorana].hasComputers and rasp.needsComputers):
                        nonavs.add((dvorana, dan, sat))

            avs -= nonavs
            if len(avs) == 0:
                continue

            try:
                slot = sys_random.choice(list(avs))
            except: 
                continue

            rasps_sems = self.svi_semestri_raspa[rasp_id]
            obradeno[rasp_id] = True
            for rasp_sem in rasps_sems:
                schedule[rasp_sem] = slot

    return schedule

def nastavnik_shuffle(self, schedule):
    nastavnici = copy.deepcopy(self.nastavnici)
    vec_obradeno = {}
    for rasp, (dvorana, dan, sat) in schedule.items():
        rasp_id = self.rasp_id(rasp)
        if rasp_id in vec_obradeno:
            continue

        vec_obradeno[rasp_id] = True
        nastavnici[rasp.professorId].free[dan,
            sat:sat+rasp.duration] -= 1

    for ns in nastavnici:
        obradeno = {}
        for dan in range(5):
            for sat in range(16):
                if nastavnici[ns].free[dan, sat] < 0:
                    for rasp, (dvorana, rdan, rsat) in schedule.items():
                        rasp_id = self.rasp_id(rasp)
                        if rasp_id in obradeno:
                            continue

                        if rasp.professorId == ns and rdan == dan and rsat == sat:
                            avs = set(self.get_availables())
                            
                            for rasp_, (dvorana, dan, sat) in schedule.items():
                                terms = {(dvorana, dan, sat+i) for i in range(rasp_.duration)}
                                avs -= terms

                            nonavs = set()
                            semester = self.semester_id(rasp)
                            for (dvorana, dan, sat) in avs:
                                if any((dvorana, dan, sat+i) not in avs for i in range(1, rasp.duration)) or \
                                   any(self.dvorane[dvorana].free[dan, sat:sat+rasp.duration] != 1) or \
                                   any(self.nastavnici[rasp.professorId].free[dan, sat:sat+rasp.duration] != 1) or \
                                   any(self.studiji[semester].free[dan, sat:sat+rasp.duration] != 1) or \
                                   self.dvorane[dvorana].capacity < rasp.numStudents or \
                                   (not self.dvorane[dvorana].hasComputers and rasp.needsComputers):
                                        nonavs.add((dvorana, dan, sat))

                            avs -= nonavs
                            if len(avs) == 0:
                                continue
                            try: 
                                slot = sys_random.choice(list(avs))
                            except:
                                continue

                            rasps_sems = self.svi_semestri_raspa[rasp_id]
                            obradeno[rasp_id] = True
                            for rasp_sem in rasps_sems:
                                schedule[rasp_sem] = slot
    return schedule

def studij_shuffle(self, schedule):
    studiji = copy.deepcopy(self.studiji)
    for rasp, (dvorana, dan, sat) in schedule.items():
        semestar = self.semester_id(rasp)
        studiji[semestar].free[dan, sat:sat+rasp.duration] -= 1

    for st in studiji:
        obradeno = {}
        for dan in range(5):
            for sat in range(16):
                if studiji[st].free[dan, sat] < 0:
                    for rasp, (dvorana, rdan, rsat) in schedule.items():
                        rasp_id = self.rasp_id(rasp)
                        if rasp_id in obradeno:
                            continue

                        semestar = self.semester_id(rasp)
                        if semestar == st and rdan == dan and rsat == sat:
                            avs = set(self.get_availables())
                            
                            for rasp_, (dvorana, dan, sat) in schedule.items():
                                terms = {(dvorana, dan, sat+i) for i in range(rasp_.duration)}
                                avs -= terms

                            nonavs = set()
                            for (dvorana, dan, sat) in avs:
                                if any((dvorana, dan, sat+i) not in avs for i in range(1, rasp.duration)) or \
                                   any(self.dvorane[dvorana].free[dan, sat:sat+rasp.duration] != 1) or \
                                   any(self.nastavnici[rasp.professorId].free[dan, sat:sat+rasp.duration] != 1) or \
                                   any(self.studiji[semestar].free[dan, sat:sat+rasp.duration] != 1) or \
                                   self.dvorane[dvorana].capacity < rasp.numStudents or \
                                   (not self.dvorane[dvorana].hasComputers and rasp.needsComputers):
                                        nonavs.add((dvorana, dan, sat))

                            avs -= nonavs
                            if len(avs) == 0:
                                continue
                            try: 
                                slot = sys_random.choice(list(avs))
                            except:
                                continue
                            
                            rasps_sems = self.svi_semestri_raspa[rasp_id]
                            obradeno[rasp_id] = True
                            for rasp_sem in rasps_sems:
                                schedule[rasp_sem] = slot
    return schedule

def swapper(self, schedule):
    dvorane, nastavnici, studiji = copy.deepcopy(self.dvorane), copy.deepcopy(self.nastavnici), \
                                   copy.deepcopy(self.studiji)

    #brojanje collisiona
    vec_obradeno = {}
    for rasp, (dv, dan, sat) in schedule.items():
        rasp_id = (rasp.name, rasp.type, rasp.group)
        semestar = self.semester_id(rasp)

        studiji[semestar].free[dan, sat:sat+rasp.duration] -= 1

        if rasp_id in vec_obradeno:
            continue
        vec_obradeno[rasp_id] = True

        dvorane[dv].free[dan, sat:sat+rasp.duration] -= 1
        nastavnici[rasp.professorId].free[dan,sat:sat+rasp.duration] -= 1

    #pronalazak collision tocaka
    collision_raspovi = []
    for rasp_, (dv, dan, sat) in schedule.items():
        semestar = self.semester_id(rasp)
        for dan2 in range(5):
            for sat2 in range(16):
                if rasp_ in collision_raspovi:
                    break

                if nastavnici[rasp_.professorId].free[dan2, sat2] <= -1:
                    collision_raspovi.append(rasp_)
                if dvorane[dv].free[dan2, sat2] <= -1:
                    collision_raspovi.append(rasp_)
                if studiji[semestar].free[dan2, sat2] <= -1:
                    collision_raspovi.append(rasp_)
                if dvorane[dv].capacity < rasp_.numStudents:
                    collision_raspovi.append(rasp_)

    #random odaberi 1 i dohvati sve moguce avs po nastavniku
    if len(collision_raspovi) == 0:
        return self.grade(schedule), schedule
    collision_rasp = sys_random.choice(collision_raspovi)

    avs = set()
    nastavnici_ = copy.deepcopy(self.nastavnici)
    semester = self.semester_id(collision_rasp)
    for dan3 in range(5):
        for sat3 in range(15):
            if any(self.nastavnici[collision_rasp.professorId].free[dan3, sat3:sat3+collision_rasp.duration] != 1) or \
               any(self.studiji[semester].free[dan3, sat3:sat3+collision_rasp.duration] != 1):
                    break
            for dvr in self.dvorane:
                if collision_rasp.needsComputers and not self.dvorane[dvr].hasComputers or \
                   collision_rasp.numStudents > self.dvorane[dvr].capacity or \
                   any(self.dvorane[dvr].free[dan3, sat3:sat3+collision_rasp.duration] != 1):
                        continue
                avs.add((dvr, dan3, sat3))

    collision_slot = schedule[collision_rasp]
    collision_rasp_id = (collision_rasp.name, collision_rasp.type, collision_rasp.group)
    best_grade, best_schedule = (-50000,), schedule

    vec_obradeno = {}
    for rasp1, (dv, dan, sat) in schedule.items():
        slot = (dv, dan, sat)
        if slot not in avs:
            continue

        rasp1_id = self.rasp_id(rasp1)
        if rasp1_id in vec_obradeno:
            continue

        grade_schedule = copy.deepcopy(best_schedule)

        rasps_sems = self.svi_semestri_raspa[rasp1_id]
        vec_obradeno[rasp1_id] = True
        for rasp_sem in rasps_sems:
            grade_schedule[rasp_sem] = collision_slot

        collision_rasps_sems = self.svi_semestri_raspa[collision_rasp_id]
        vec_obradeno[collision_rasp_id] = True
        for rasp_sem in collision_rasps_sems:
            grade_schedule[rasp_sem] = slot

        the_grade = self.grade(grade_schedule)
        if the_grade[0] > best_grade[0]:
            best_grade = the_grade
            best_schedule = grade_schedule

    return best_grade, best_schedule