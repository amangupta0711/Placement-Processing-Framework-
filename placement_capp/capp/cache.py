"""Cache memory: direct-mapped / set-associative (LRU) and EAT."""
import random
from collections import OrderedDict

from models import NUM_STUDENTS, TC, TM


class Cache:
    def __init__(self, lines, ways):
        self.lines, self.ways = lines, ways
        self.sets = lines // ways
        self.data = [OrderedDict() for _ in range(self.sets)]   # per set: tag -> True, LRU order
        self.hits = self.misses = 0

    def access(self, record):
        idx, tag = record % self.sets, record // self.sets
        st = self.data[idx]
        if tag in st:
            st.move_to_end(tag)
            self.hits += 1
            return True, idx
        self.misses += 1
        if len(st) >= self.ways:
            st.popitem(last=False)          # evict least recently used
        st[tag] = True
        return False, idx

    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


def eat(h):
    """Effective access time = h*tc + (1-h)*(tc+tm)"""
    return h * TC + (1 - h) * (TC + TM)


def access_pattern(n=2000, hot=20, hot_share=0.8, seed=7):
    rng = random.Random(seed)
    hot_set = rng.sample(range(NUM_STUDENTS), hot)
    return [rng.choice(hot_set) if rng.random() < hot_share else rng.randrange(NUM_STUDENTS)
            for _ in range(n)]
