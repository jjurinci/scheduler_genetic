import copy
from genetic_algorithm.optimizer import db_dml

def all_problematic_schedules_prof(self, timetable, check_professorId, check_dan, check_sat_start, check_sat_end):
    problematic_schedules = []
    for scheduled in timetable:
        schedule, dvorana, dan, sat_start = scheduled["schedule"], scheduled["time"]["classroom"], \
                                            scheduled["time"]["day"], scheduled["time"]["hour"]

        if dan != check_dan or schedule["professorId"] != check_professorId:
            continue
        sat_end = sat_start + schedule["duration"]
        if sat_start >= check_sat_end or sat_end <= check_sat_start:
            continue
        problematic_schedules.append(schedule["_id"])
    return problematic_schedules

def all_problematic_schedules_classroom(self, timetable, check_dvorana, check_dan, check_sat_start, check_sat_end):
    problematic_schedules = []
    for scheduled in timetable:
        schedule, dvorana, dan, sat_start = scheduled["schedule"], scheduled["time"]["classroom"], \
                                            scheduled["time"]["day"], scheduled["time"]["hour"]

        if dan != check_dan or schedule["classroomId"] != check_dvorana:
            continue
        sat_end = sat_start + schedule["duration"]
        if sat_start >= check_sat_end or sat_end <= check_sat_start:
            continue
        problematic_schedules.append(schedule["_id"])
    return problematic_schedules

def all_problematic_semesters(self, timetable, check_semesterId, check_dan, check_sat_start, check_sat_end):
    problematic_schedules = []
    for scheduled in timetable:
        schedule, dvorana, dan, sat_start = scheduled["schedule"], scheduled["time"]["classroom"], \
                                            scheduled["time"]["day"], scheduled["time"]["hour"]

        if dan != check_dan:
            continue
        sat_end = sat_start + schedule["duration"]
        if sat_start >= check_sat_end or sat_end <= check_sat_start:
            continue

        for semesterId in schedule["semesterIds"]:
            if semesterId == check_semesterId:
                problematic_schedules.append(schedule["_id"])

    return problematic_schedules

def format_get_problems(self, timetable, dvorane, nastavnici, studiji):
    schedule_problems = {}

    for scheduled in timetable:
        schedule, dvorana, dan, sat = scheduled["schedule"], scheduled["time"]["classroom"], \
                                      scheduled["time"]["day"], scheduled["time"]["hour"]
        time = scheduled["time"]

        s_id = schedule["_id"]
        schedule_problems[s_id] = False

        problems = {"professors": False, "classrooms_collision": False, "classrooms_capacity": False, \
                    "classrooms_computers": False,"semesters": False}

        if any(nastavnici[schedule["professorId"]].free[dan, sat:sat+schedule["duration"]] < 0):
            all_problematic_schedules = all_problematic_schedules_prof(self, timetable, schedule["professorId"], \
                                                                       dan, sat, sat + schedule["duration"])
            obj = {"problematicSchedules": all_problematic_schedules, "professorId": schedule["professorId"] , "time": time} #this {profId} is having {all_problematic_schedules} at the same {time}
            problems["professors"] = obj

        if any(dvorane[dvorana].free[dan, sat:sat+schedule["duration"]] < 0):
            all_problematic_classroom_collision = all_problematic_schedules_classroom(self, timetable, dvorana, \
                                                                                      dan, sat, sat + schedule["duration"])
            obj = {"problematicSchedules": all_problematic_classroom_collision, "classroomId": dvorana, "time": time}
            problems["classrooms_collision"] = obj

        if dvorane[dvorana].capacity < schedule["numStudents"]:
            problems["classrooms_capacity"] = True

        if not dvorane[dvorana].hasComputers and schedule["needsComputers"]:
            problems["classrooms_computers"] = True

        for semesterId in schedule["semesterIds"]:
            if any(studiji[semesterId].free[dan, sat:sat+schedule["duration"]] < 0):
                all_problematic_sems = all_problematic_semesters(self, timetable, semesterId, dan, sat, sat + schedule["duration"])
                obj = {"problematicSchedules": all_problematic_sems,
                       "semesterId": semesterId, "time": time}
                if not problems["semesters"]:
                    problems["semesters"] = [obj]
                else:
                    problems["semesters"].append(obj)

        if problems["professors"] or problems["classrooms_collision"] or problems["classrooms_capacity"] or \
           problems["classrooms_computers"] or problems["semesters"]:
           schedule_problems[s_id] = problems

    return schedule_problems


def format_collect_problems(self, rasp, time, dvorane, nastavnici, studiji):
    dvorana, dan, sat = time["classroom"], time["day"], time["hour"]
    rasp_id = self.rasp_id(rasp)
    rasps_sems = self.svi_semestri_raspa[rasp_id]
    for rasp_sem in rasps_sems:
        semestar = self.semester_id(rasp_sem)
        studiji[semestar].free[dan, sat:sat+rasp_sem.duration] -= 1

    dvorane[dvorana].free[dan, sat:sat+rasp.duration] -= 1
    nastavnici[rasp.professorId].free[dan, sat:sat+rasp.duration] -= 1

    return dvorane, nastavnici, studiji


def format_result(self, sample):
    how_many = 5 if 5 <= len(sample) else len(sample)

    timetables = []
    for i in range(how_many):
        dvorane, nastavnici, studiji = copy.deepcopy(self.dvorane), copy.deepcopy(self.nastavnici), \
                                       copy.deepcopy(self.studiji)
        timetable = []
        grade = { 'best': sample[i][0][0].item(), 'classrooms': sample[i][0][1].item(), 'professors': sample[i][0][2].item(),
                  'semesters': sample[i][0][3].item(),'capacity': sample[i][0][4], 'computers': sample[i][0][5] }

        vec_obradeno = {}
        for rasp in sample[i][1]:
            rasp_id = self.rasp_id(rasp)
            if rasp_id in vec_obradeno:
                continue
            vec_obradeno[rasp_id] = True

            rasps_sems = self.svi_semestri_raspa[rasp_id]
            semestri = list(map(lambda x: x.semesterId, rasps_sems))

            dvorana, dan, sat = sample[i][1][rasp]
            newrasp = {
                "_id": rasp.id,
                "name": rasp.name,
                "type": rasp.type,
                "group": rasp.group,
                "duration": rasp.duration,
                "mandatory": rasp.mandatory,
                "needsComputers": rasp.needsComputers,
                "numStudents": rasp.numStudents,
                "classroomName": self.classroom_name[dvorana],
                "professorFirstName": rasp.professorName.split(" ")[0],
                "professorLastName": " ".join(rasp.professorName.split(" ")[1:]),
                "startHHmm": "",
                "endHHmm": "",
                "professorId": rasp.professorId,
                "classroomId": dvorana,
                "subjectId": rasp.subjectId,
                "semesterIds": semestri,
                "timetableId": "",
                "userId": self.user_data[0],
                "solverId": self.user_data[1]
            }

            time = {"classroom": dvorana, "day": dan, "hour": sat}
            dvorane, nastavnici, studiji = format_collect_problems(self, rasp, time, dvorane, nastavnici, studiji)
            scheduled = {"schedule": newrasp, "time": time}
            timetable.append(scheduled)

        problems = format_get_problems(self, timetable, dvorane, nastavnici, studiji)
        timetable_obj = {"timetable": timetable, "grade": grade, "problems": problems}
        timetables.append(timetable_obj)

    return {"timetables": timetables, "solverId": self.user_data[1], "userId": self.user_data[0]}

def insert_final_results(self, results):
    done = {"solverId": self.user_data[1],"userId": self.user_data[0], "done": True}
    inserted_done = db_dml.insert_one('solver_results', False, done)
    inserted_results = db_dml.insert_one('solver_timetables', False, results)

def end_process(self, sample):
    results = format_result(self, sample)
    insert_final_results(self, results)

def front_end_requested_stoppage(self):
    query = {'$and': [{'solverId': self.user_data[1]}, {'userId': self.user_data[0]}]}
    frontend_requested_stoppage = db_dml.find_one('solver_stop', query)
    if frontend_requested_stoppage:
        return True
    return False
