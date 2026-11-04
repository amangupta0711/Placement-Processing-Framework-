"""Integration: cache + control unit + ALU + CPU + pipeline in one flow."""
from capp.cache import Cache, eat
from capp.control_unit import FULL_ROUTINE, run_microroutine
from capp.cpu import assemble, program_text, run_cpu
from capp.pipeline import schedule_pipeline
from data.dummy_data import COMPANIES, STUDENTS
from models import CACHE_LINES, CACHE_WAYS, STAGES, TC, TM, software_eligible
from services.console import banner, pause, pick_company, pick_student, section
from services.demos import print_microroutine


SESSION_CACHE = Cache(CACHE_LINES, CACHE_WAYS)


PROGRAM_CACHE = {}


def get_program(company, scheduled=True):
    key = (company["name"], scheduled)
    if key not in PROGRAM_CACHE:
        PROGRAM_CACHE[key] = assemble(program_text(company, scheduled))
    return PROGRAM_CACHE[key]


def process_application(student, company, cache):
    hit, idx = cache.access(student["id"])
    regs, mem, trace, booth_ops = run_cpu(get_program(company), student)
    rows, total, hazards, stalls = schedule_pipeline(trace, forwarding=True)
    return {"hit": hit, "idx": idx, "latency": TC if hit else TC + TM,
            "status": mem["status"] == 1, "score": mem["score"], "n": len(trace),
            "booth": booth_ops, "cycles": total, "stalls": stalls, "unpiped": len(trace) * STAGES}


def demo_integrated_single():
    banner("INTEGRATED FLOW - ONE APPLICATION, ALL CAPP PARTS TOGETHER")
    s = pick_student(0)
    c = pick_company(1)
    print(f"\n{s['name']} -> {c['name']}")
    r = process_application(s, c, SESSION_CACHE)

    section("Stage 1  CACHE / MEMORY : read student record")
    print(f"Record {s['id']} -> set {r['idx']} of {SESSION_CACHE.sets} ({CACHE_WAYS}-way): "
          f"{'HIT' if r['hit'] else 'MISS (fetched from main memory)'}  -> {r['latency']} ns")
    print("Run this option again with the same student to see the HIT.")

    section("Stage 2  CONTROL UNIT (micro-programmed) : CHECK_ELIGIBILITY routine")
    ok, rows = run_microroutine(FULL_ROUTINE, s, c)
    print_microroutine(rows)
    print(f"Control cycles = {len(FULL_ROUTINE)} steps x 2 = {len(FULL_ROUTINE) * 2}")

    section("Stage 3  ALU : Booth multiplications for the score")
    print(f"3 Booth multiplications (8 shift/add steps each) -> score = {r['score']}")

    section("Stage 4  INSTRUCTION CYCLE : mini-CPU program")
    print(f"{r['n']} instructions fetched, decoded and executed -> status: "
          f"{'ELIGIBLE' if r['status'] else 'REJECTED'}")
    print(f"Cross-check with plain Python rule: {software_eligible(s, c) == r['status']}")

    section("Stage 5  PIPELINE : timing of those instructions")
    print(f"Stalls found: {r['stalls']}   Pipelined = {r['cycles']} cycles   "
          f"Unpipelined = {r['unpiped']} cycles   Speedup = {r['unpiped'] / r['cycles']:.2f}")

    section("Stage 6  PARALLEL : where this scales")
    print("Same test on many students -> SIMD lanes;  each company's rules -> MIMD processors")
    print("(see option 9 for the whole batch).")
    pause()


def demo_integrated_batch():
    banner("INTEGRATED BATCH - ALL STUDENTS x ALL COMPANIES")
    cache = Cache(CACHE_LINES, CACHE_WAYS)
    results = {c["name"]: [] for c in COMPANIES}
    mism = 0
    tot = {"n": 0, "booth": 0, "cycles": 0, "stalls": 0, "unpiped": 0, "latency": 0}
    for s in STUDENTS:
        for c in COMPANIES:
            r = process_application(s, c, cache)
            if r["status"] != software_eligible(s, c):
                mism += 1
            results[c["name"]].append((s, r))
            for k in tot:
                tot[k] += r[k] if k != "cycles" else r["cycles"]
    apps = len(STUDENTS) * len(COMPANIES)
    stream = tot["n"] + STAGES - 1 + tot["stalls"]          # one continuous instruction stream

    section("Shortlist per company (top 5 by Booth score)")
    for c in COMPANIES:
        elig = [(s, r) for s, r in results[c["name"]] if r["status"]]
        elig.sort(key=lambda x: -x[1]["score"])
        print(f"\n{c['name']}: {len(elig)} eligible of {len(STUDENTS)}")
        for s, r in elig[:5]:
            print(f"   {s['name']}  score {r['score']:>4}  (CGPA {s['cgpa']}, skills {s['skills']}, "
                  f"backlogs {s['backlogs']})")

    section("Performance summary")
    print(f"Applications processed           : {apps}")
    print(f"Cross-check vs plain Python rule : {apps - mism}/{apps} identical")
    print(f"Booth multiplications            : {tot['booth']}")
    print(f"Instructions executed            : {tot['n']}")
    print(f"Pipeline  unpipelined cycles     : {tot['unpiped']}")
    print(f"          pipelined (stream)     : {stream}   speedup {tot['unpiped'] / stream:.2f} "
          f"(stalls: {tot['stalls']})")
    h = cache.hit_ratio()
    print(f"Cache ({CACHE_LINES} lines, {CACHE_WAYS}-way): hit ratio {h * 100:.1f}%   "
          f"EAT {eat(h):.1f} ns   (no cache: {TM} ns)")
    print(f"Parallel (ideal)                 : SIMD 8 lanes x MIMD {len(COMPANIES)} processors = "
          f"{8 * len(COMPANIES)}x on the eligibility checks")
    pause()
