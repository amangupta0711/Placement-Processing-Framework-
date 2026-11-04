"""Unit tests. Run from the project folder:  python -m unittest discover -s tests -v"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capp.alu import booth_multiply
from capp.cache import Cache, eat
from capp.control_unit import BASE_ROUTINE, FULL_ROUTINE, run_microroutine
from capp.cpu import assemble, program_text, run_cpu
from capp.pipeline import schedule_pipeline
from data.dummy_data import COMPANIES, STUDENTS
from models import software_eligible


class TestBooth(unittest.TestCase):
    def test_fixed_pairs(self):
        for a, b in [(12, 5), (-12, 5), (12, -5), (-12, -5), (0, 7), (127, -127)]:
            self.assertEqual(booth_multiply(a, b)[0], a * b)

    def test_random_pairs(self):
        rng = random.Random(3)
        for _ in range(1000):
            a, b = rng.randint(-127, 127), rng.randint(-127, 127)
            self.assertEqual(booth_multiply(a, b)[0], a * b)

    def test_report_samples(self):
        self.assertEqual(2 * 82 + 5 * 6 + (-10) * 0, 194)
        self.assertEqual(2 * 75 + 5 * 4 + (-10) * 2, 150)


class TestCPUandControl(unittest.TestCase):
    def test_cpu_matches_plain_rule_for_everyone(self):
        for c in COMPANIES:
            prog = assemble(program_text(c))
            for s in STUDENTS:
                _, mem, _, _ = run_cpu(prog, s)
                self.assertEqual(mem["status"] == 1, software_eligible(s, c))

    def test_score_formula(self):
        prog = assemble(program_text(COMPANIES[0]))
        self.assertEqual(run_cpu(prog, STUDENTS[0])[1]["score"], 194)
        self.assertEqual(run_cpu(prog, STUDENTS[1])[1]["score"], 150)

    def test_microroutine_matches_rule(self):
        for s in STUDENTS:
            for c in COMPANIES:
                self.assertEqual(run_microroutine(FULL_ROUTINE, s, c)[0], software_eligible(s, c))

    def test_routine_sizes(self):
        self.assertEqual((len(BASE_ROUTINE), len(FULL_ROUTINE)), (4, 5))


class TestPipeline(unittest.TestCase):
    def test_scheduled_has_fewer_stalls_than_naive(self):
        c, s = COMPANIES[0], STUDENTS[0]
        naive = run_cpu(assemble(program_text(c, False)), s)[2]
        sched = run_cpu(assemble(program_text(c, True)), s)[2]
        self.assertGreater(schedule_pipeline(naive)[3], schedule_pipeline(sched)[3])

    def test_cycles_equal_k_plus_n_minus_1_plus_stalls(self):
        trace = run_cpu(assemble(program_text(COMPANIES[0])), STUDENTS[0])[2]
        _, total, _, stalls = schedule_pipeline(trace)
        self.assertEqual(total, 5 + len(trace) - 1 + stalls)


class TestCache(unittest.TestCase):
    def test_hit_after_miss(self):
        c = Cache(16, 4)
        self.assertFalse(c.access(5)[0])
        self.assertTrue(c.access(5)[0])

    def test_lru_eviction(self):
        c = Cache(4, 4)             # one set, 4 ways
        for r in (0, 1, 2, 3, 4):   # 4 evicts record 0
            c.access(r)
        self.assertFalse(c.access(0)[0])

    def test_eat_formula(self):
        self.assertAlmostEqual(eat(1.0), 10)
        self.assertAlmostEqual(eat(0.0), 110)


if __name__ == "__main__":
    unittest.main()
