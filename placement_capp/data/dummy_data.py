"""Dummy student records and company criteria (no real data)."""
import random

from models import NUM_STUDENTS


def make_students(n=NUM_STUDENTS, seed=42):
    rng = random.Random(seed)
    students = []
    for i in range(n):
        students.append({
            "id": i,
            "name": f"Student-{i:03d}",
            "cgpa": rng.randint(60, 98),
            "skills": rng.randint(0, 10),
            "backlogs": rng.choices([0, 1, 2, 3, 4], weights=[60, 20, 10, 6, 4])[0],
        })
    # the two sample cases quoted in the Month-2 report
    students[0].update(cgpa=82, skills=6, backlogs=0)   # score 194
    students[1].update(cgpa=75, skills=4, backlogs=2)   # score 150
    return students


STUDENTS = make_students()


COMPANIES = [
    {"name": "TCS",     "min_cgpa": 65, "min_skills": 2, "max_backlogs": 2},
    {"name": "Infosys", "min_cgpa": 70, "min_skills": 3, "max_backlogs": 1},
    {"name": "Wipro",   "min_cgpa": 60, "min_skills": 1, "max_backlogs": 3},
    {"name": "Google",  "min_cgpa": 85, "min_skills": 7, "max_backlogs": 0},
]
