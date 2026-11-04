"""Shared constants and the plain-Python reference rule."""

STAGES = 5                  # IF, ID, EX, MEM, WB
CACHE_LINES = 16            # as in the Month-2 report
CACHE_WAYS = 4
TC, TM = 10, 100            # cache / main-memory access time (ns)
NUM_STUDENTS = 200
OPS_PER_CHECK = 4           # CMP cgpa, CMP skills, CMP backlogs, SET flag


def software_eligible(s, c):
    """Plain-Python reference rule, used only to cross-check the 'hardware' path."""
    return (s["cgpa"] >= c["min_cgpa"] and s["skills"] >= c["min_skills"]
            and s["backlogs"] <= c["max_backlogs"])
