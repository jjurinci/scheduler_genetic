import math
import copy
from random_object_id import generate
from collections import namedtuple

Rasp = namedtuple('Rasp', ['id', 'name', 'type', 'group', 'duration', 'mandatory', \
                           'needsComputers', 'semesterId', 'professorId','subjectId',\
                           'semesterName', 'professorName', 'numStudents'])

def transform(data):
    subjects = data["data"]["subjects"]
    weeks = int(data["data"]["weeks"])
    
    rasps = []

    for subject in subjects:
        _id = generate()
        subject_id = subject["_id"]
        name = subject["name"]
        duration = math.ceil( int(subject["theoryHr"]) / int(weeks) )
        mandatory = subject["mandatory"]
        num_students = subject["numStudents"]

        type_, group, needs_computers = None, None, None 

        if int(subject["theoryHr"]) > 0:
            type_ = "theory"
            group = 1 if ("theoryNumGroups" not in subject) else int(subject["theoryNumGroups"])
            needs_computers = subject["theoryNeedsComputers"]

            if "theoryNumGroups" in subject:
                for i in range(int(subject["theoryNumGroups"])):
                    group = i+1
                    
                    professor_id = subject["theoryGroupProfessors"][i]["_id"]
                    professor_name = subject["theoryGroupProfessors"][i]["firstName"] + " " + \
                                     subject["theoryGroupProfessors"][i]["lastName"] 

                    for semester in subject["semesters"]:
                        semester_id = semester["_id"]
                        semester_name = semester["name"] + " (" + semester["facultyName"] + ")"

                        rasp = Rasp(_id, name, type_, group, duration, mandatory, needs_computers, \
                                    semester_id, professor_id, subject_id, semester_name, professor_name, num_students)
                        rasps.append(rasp)
            
            else:
                professor_id = subject["theoryProfessors"][0]["_id"]
                professor_name = subject["theoryProfessors"][0]["firstName"] + " " + \
                                 subject["theoryProfessors"][0]["lastName"] 

                for semester in subject["semesters"]:
                    semester_id = semester["_id"]
                    semester_name = semester["name"] + " (" + semester["facultyName"] + ")"
                    rasp = Rasp(_id, name, type_, group, duration, mandatory, needs_computers, \
                                semester_id, professor_id, subject_id, semester_name, professor_name, num_students)
                    rasps.append(rasp)
            

        if int(subject["practiceHr"]) > 0:
            type_ = "practice"
            group = 1 if ("practiceNumGroups" not in subject) else int(subject["practiceNumGroups"])
            needs_computers = subject["practiceNeedsComputers"]
            
            if "practiceNumGroups" in subject:
                for i in range(int(subject["practiceNumGroups"])):
                    group = i+1
                    professor_id = subject["practiceGroupProfessors"][i]["_id"]
                    professor_name = subject["practiceGroupProfessors"][i]["firstName"] + " " + \
                                     subject["practiceGroupProfessors"][i]["lastName"] 
                    for semester in subject["semesters"]:
                        semester_id = semester["_id"]
                        semester_name = semester["name"] + " (" + semester["facultyName"] + ")"
                        rasp = Rasp(_id, name, type_, group, duration, mandatory, needs_computers, \
                                    semester_id, professor_id,subject_id, semester_name, professor_name, num_students)
                        rasps.append(rasp)
            
            
            else:
                professor_id = subject["practiceProfessors"][0]["_id"]
                professor_name = subject["practiceProfessors"][0]["firstName"] + " " + \
                                 subject["practiceProfessors"][0]["lastName"] 

                for semester in subject["semesters"]:
                    semester_id = semester["_id"]
                    semester_name = semester["name"] + " (" + semester["facultyName"] + ")"
                    rasp = Rasp(_id, name, type_, group, duration, mandatory, needs_computers, \
                                semester_id, professor_id, subject_id, semester_name, professor_name, num_students)
                    rasps.append(rasp)
            
        if int(subject["seminarHr"]) > 0:
            type_ = "seminar"
            group = 1 if ("seminarNumGroups" not in subject) else int(subject["seminarNumGroups"])
            needs_computers = subject["seminarNeedsComputers"]
            
            if "seminarNumGroups" in subject:
                for i in range(int(subject["seminarNumGroups"])):
                    group = i+1
                    professor_id = subject["seminarGroupProfessors"][i]["_id"]
                    professor_name = subject["seminarGroupProfessors"][i]["firstName"] + " " + \
                                     subject["seminarGroupProfessors"][i]["lastName"] 

                    for semester in subject["semesters"]:
                        semester_id = semester["_id"]
                        semester_name = semester["name"] + " (" + semester["facultyName"] + ")"
                        rasp = Rasp(_id, name, type_, group, duration, mandatory, needs_computers, \
                                    semester_id, professor_id, subject_id, semester_name, professor_name, num_students)
                        rasps.append(rasp)
            
            else:
                professor_id = subject["seminarProfessors"][0]["_id"]
                professor_name = subject["seminarProfessors"][0]["firstName"] + " " + \
                                 subject["seminarProfessors"][0]["lastName"] 
                for semester in subject["semesters"]:
                    semester_id = semester["_id"]
                    semester_name = semester["name"] + " (" + semester["facultyName"] + ")"
                    rasp = Rasp(_id, name, type_, group, duration, mandatory, needs_computers, \
                                semester_id, professor_id, semester_name, subject_id, professor_name, num_students)
                    rasps.append(rasp)
            
    return rasps
