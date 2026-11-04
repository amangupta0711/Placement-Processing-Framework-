"""Parallel processing: SIMD (data parallel) and MIMD (task parallel)."""
import threading

from data.dummy_data import STUDENTS
from models import OPS_PER_CHECK, software_eligible


def simd_eligibility(students, company, lanes=8):
    """One instruction stream, many data lanes: the same test is applied to 'lanes' students at once."""
    out, vsteps = [], 0
    for base in range(0, len(students), lanes):
        chunk = students[base:base + lanes]
        out.extend(software_eligible(s, company) for s in chunk)     # all lanes in one vector step
        vsteps += OPS_PER_CHECK
    return out, vsteps


def mimd_worker(company, barrier):
    """Each processor runs its OWN instruction stream (its own company rules)."""
    barrier.wait()                     # all processors start together, one thread each
    eligible, ops = 0, 0
    for s in STUDENTS:
        ops += OPS_PER_CHECK
        eligible += software_eligible(s, company)
    return company["name"], threading.current_thread().name, eligible, ops
