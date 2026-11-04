"""Menu demos for each CAPP concept (staged printouts)."""
import random
import threading
from concurrent.futures import ThreadPoolExecutor

from capp.alu import bstr, booth_multiply
from capp.cache import Cache, access_pattern, eat
from capp.control_unit import BASE_ROUTINE, FULL_ROUTINE, hardwired_signals, run_microroutine
from capp.cpu import assemble, program_text, run_cpu, status_text
from capp.parallel import mimd_worker, simd_eligibility
from capp.pipeline import schedule_pipeline
from data.dummy_data import COMPANIES, STUDENTS
from models import (CACHE_LINES, CACHE_WAYS, NUM_STUDENTS, OPS_PER_CHECK, STAGES, TC, TM,
                    software_eligible)
from services.console import ask_int, banner, pause, pick_company, pick_student, section


def view_data():
    banner("DUMMY STUDENT RECORDS & COMPANY CRITERIA", "No real student data is used")
    print(f"{'ID':>3}  {'Name':<13}{'CGPA':>5}{'x10':>5}{'Skills':>8}{'Backlogs':>10}")
    for s in STUDENTS[:15]:
        print(f"{s['id']:>3}  {s['name']:<13}{s['cgpa'] / 10:>5.1f}{s['cgpa']:>5}{s['skills']:>8}{s['backlogs']:>10}")
    print(f"... {len(STUDENTS) - 15} more records (ids 15-{len(STUDENTS) - 1})")
    section("Company criteria")
    print(f"{'Company':<10}{'Min CGPA(x10)':>14}{'Min skills':>12}{'Max backlogs':>14}{'Eligible':>10}")
    for c in COMPANIES:
        cnt = sum(software_eligible(s, c) for s in STUDENTS)
        print(f"{c['name']:<10}{c['min_cgpa']:>14}{c['min_skills']:>12}{c['max_backlogs']:>14}{cnt:>10}")
    section("Eligibility score")
    print("Score = 2 x CGPA + 5 x skills + (-10) x backlogs   (CGPA kept as integer, e.g. 8.2 -> 82)")
    pause()


def booth_table(m, q, label):
    prod, steps = booth_multiply(m, q)
    print(f"\n{label}:  M (multiplicand) = {m} [{bstr(m, 8)}]   Q (multiplier) = {q} [{bstr(q, 8)}]")
    print(f"{'Step':>4} {'Q0Q-1':>6}  {'Operation':<13}{'A':>10}{'Q':>10}{'Q-1':>5}")
    print(f"{'init':>4} {'':>6}  {'':<13}{bstr(0, 8):>10}{bstr(q, 8):>10}{0:>5}")
    for st, pr, act, a, qq, qm in steps:
        print(f"{st:>4} {pr:>6}  {act:<13}{a:>10}{qq:>10}{qm:>5}")
    last = steps[-1]
    ok = "OK" if prod == m * q else "MISMATCH"
    print(f"Result A:Q = {last[3]} {last[4]} = {prod}    normal {m} x {q} = {m * q}  -> {ok}")
    return prod


def booth_self_test():
    fixed = [(12, 5), (-12, 5), (12, -5), (-12, -5), (0, 7), (127, -127)]
    rng = random.Random(1)
    rand = [(rng.randint(-127, 127), rng.randint(-127, 127)) for _ in range(1000)]
    ok_fixed = sum(booth_multiply(a, b)[0] == a * b for a, b in fixed)
    ok_rand = sum(booth_multiply(a, b)[0] == a * b for a, b in rand)
    print(f"Self-test: {ok_fixed}/{len(fixed)} fixed pairs (neg x pos, neg x neg ...) and "
          f"{ok_rand}/{len(rand)} random pairs match normal multiplication.")


def demo_booth():
    banner("ALU - BOOTH SIGNED MULTIPLICATION", "Score = 2 x CGPA + 5 x skills + (-10) x backlogs")
    s = pick_student(1)
    print(f"\n{s['name']}: CGPA {s['cgpa'] / 10:.1f} (stored as {s['cgpa']}), "
          f"skills {s['skills']}, backlogs {s['backlogs']}")
    print("Why Booth? The backlog weight is NEGATIVE; Booth handles signed numbers directly.")
    p1 = booth_table(s["cgpa"], 2, "Multiply 1: CGPA x 2")
    p2 = booth_table(s["skills"], 5, "Multiply 2: skills x 5")
    p3 = booth_table(s["backlogs"], -10, "Multiply 3: backlogs x (-10)")
    section("Eligibility score (ADD in the ALU)")
    print(f"Score = {p1} + {p2} + ({p3}) = {p1 + p2 + p3}")
    section("Verification")
    booth_self_test()
    pause()


def print_microroutine(rows):
    print(f"{'uPC':>3}  {'Micro-instruction':<19}{'Control signals':<34}Result")
    for addr, m, out in rows:
        print(f"{addr:>3}  {m['name']:<19}{', '.join(m['signals']):<34}{out}")


def demo_control_unit():
    banner("CONTROL UNIT - HARDWIRED vs MICRO-PROGRAMMED")
    section("A. Hardwired: fixed gates on opcode + timing step (LOAD / COMPARE / STORE)")
    print("ADDR_OUT=(LOAD+STORE).T1  MEM_READ=LOAD.T2  REG_WRITE=LOAD.T3  REG_OUT=COMPARE.T1+STORE.T2")
    print("ALU_SUB=COMPARE.T2  FLAG_WRITE=COMPARE.T3  MEM_WRITE=STORE.T3")
    print(f"\n{'Opcode':<9}{'T1':<22}{'T2':<22}{'T3'}")
    for op in ("LOAD", "COMPARE", "STORE"):
        print(f"{op:<9}" + "".join(f"{'+'.join(hardwired_signals(op, t)) or '-':<22}" for t in (1, 2, 3)))

    s = pick_student(0)
    c = pick_company(1)
    section(f"B. Micro-programmed: CHECK_ELIGIBILITY stored in control memory ({s['name']} vs {c['name']})")
    ok, rows = run_microroutine(BASE_ROUTINE, s, c)
    print_microroutine(rows)

    section("C. Company changes its rule: 'minimum skills' must also be checked")
    print("Micro-programmed -> insert ONE row into control memory (no hardware change):")
    ok2, rows2 = run_microroutine(FULL_ROUTINE, s, c)
    print_microroutine(rows2)
    print("Hardwired        -> new timing state + new gates + decoder change = circuit redesign.")

    section("D. Comparison")
    n1, n2 = len(BASE_ROUTINE), len(FULL_ROUTINE)
    print(f"{'':<34}{'Hardwired':<18}{'Micro-programmed'}")
    print(f"{'Cycles, 4-step routine':<34}{n1 * 1:<18}{n1 * 2}   (1 control-memory read + 1 execute per step)")
    print(f"{'Cycles after skills rule added':<34}{n2 * 1:<18}{n2 * 2}")
    print(f"{'Cost of changing a rule':<34}{'redesign circuit':<18}{'edit control memory'}")
    print("Choice for this project: MICRO-PROGRAMMED, because company rules change often.")
    pause()


def demo_instruction_cycle():
    banner("INSTRUCTION CYCLE - MINI CPU: FETCH -> DECODE -> EXECUTE",
           "Instruction set: LOAD STORE CMP MUL ADD BLT BGT JMP HALT")
    s = pick_student(0)
    c = pick_company(1)
    prog = assemble(program_text(c, scheduled=True))
    regs, mem, trace, booth_ops = run_cpu(prog, s)
    print(f"\n{s['name']} (CGPA {s['cgpa']}, skills {s['skills']}, backlogs {s['backlogs']}) "
          f"applies to {c['name']}  [min CGPA {c['min_cgpa']}, min skills {c['min_skills']}, "
          f"max backlogs {c['max_backlogs']}]")
    for t in trace:
        ins = t["ins"]
        nxt = t["pc"] + 1
        print(f"\nPC={t['pc']:02d}  {ins['text']}")
        print(f"  FETCH  : MAR <- PC({t['pc']}); MBR <- M[MAR]; IR <- MBR; PC <- {nxt}")
        print(f"  DECODE : opcode = {ins['op']}, operands = {', '.join(ins['args']) or '-'}")
        print(f"  EXECUTE: {t['note']}")
    section("Result")
    print(f"Instructions executed : {len(trace)}   (each = 3 phases -> {len(trace) * 3} phase-steps)")
    print(f"Booth multiplications : {booth_ops}")
    print(f"Score stored in memory: {mem['score']}")
    print(f"Application status    : {status_text(mem)}   "
          f"(plain-Python check agrees: {software_eligible(s, c) == (mem['status'] == 1)})")
    pause()


def print_pipeline_grid(rows, total):
    print(" " * 24 + "".join(f"{c:>3}" for c in range(1, total + 1)))
    for i, r in enumerate(rows):
        cells = {}
        for c in range(r["if"][0], r["if"][1] + 1):
            cells[c] = "IF"
        cells[r["id"]] = "ID"
        for c in range(r["st"][0], r["st"][1] + 1):
            cells[c] = "ST"
        cells[r["ex"]], cells[r["mem"]], cells[r["wb"]] = "EX", "ME", "WB"
        label = f"{i + 1:02d} {r['text']}"[:23]
        print(f"{label:<24}" + "".join(f"{cells.get(c, ''):>3}" for c in range(1, total + 1)))


def demo_pipeline():
    banner("5-STAGE PIPELINE + AUTOMATIC HAZARD DETECTION",
           "IF  ID  EX  ME (memory)  WB      ST = stall bubble")
    s = pick_student(0)
    c = pick_company(1)
    results = []
    for title, scheduled, fwd in (("NAIVE order (each LOAD used immediately), forwarding ON", False, True),
                                  ("SCHEDULED order (LOADs grouped first), forwarding ON", True, True),
                                  ("SCHEDULED order, forwarding OFF", True, False)):
        prog = assemble(program_text(c, scheduled))
        _, mem, trace, _ = run_cpu(prog, s)
        rows, total, hazards, stalls = schedule_pipeline(trace, fwd)
        n = len(trace)
        results.append((title, n, stalls, total, n * STAGES))
        section(title)
        if fwd or not scheduled:
            print_pipeline_grid(rows, total)
        print("Hazards detected:" if hazards else "Hazards detected: none")
        for h in hazards:
            print("  - " + h)
    section("Summary (one application through the pipeline)")
    print(f"{'Mode':<58}{'n':>3}{'Stalls':>7}{'Piped':>6}{'Unpiped':>8}{'Speedup':>8}")
    for title, n, stalls, total, unp in results:
        print(f"{title[:57]:<58}{n:>3}{stalls:>7}{total:>6}{unp:>8}{unp / total:>8.2f}")
    section("Pipeline formula: time = k + (n - 1) cycles   (k = 5 stages, unpipelined = n x k)")
    print(f"{'n':>6}{'Unpipelined':>13}{'Pipelined':>11}{'Speedup':>9}")
    for n in (10, 100, 200):
        print(f"{n:>6}{n * STAGES:>13}{STAGES + n - 1:>11}{n * STAGES / (STAGES + n - 1):>9.2f}")
    print("Speedup approaches k = 5 as n grows. Each stall adds exactly 1 cycle.")
    pause()


def demo_cache():
    banner("CACHE MEMORY - DIRECT-MAPPED vs 4-WAY SET ASSOCIATIVE",
           f"tc = {TC} ns, tm = {TM} ns, EAT = h*tc + (1-h)*(tc+tm)")
    pattern = access_pattern()
    print(f"Workload: {len(pattern)} record accesses, 80% to 20 shortlisted students, "
          f"20% to any of {NUM_STUDENTS} records.")
    section(f"Staged view: first 10 accesses ({CACHE_LINES} lines)")
    dm, sa = Cache(CACHE_LINES, 1), Cache(CACHE_LINES, CACHE_WAYS)
    print(f"{'Access':>6}{'Record':>8}   {'Direct (rec mod ' + str(CACHE_LINES) + ')':<24}{'4-way (set = rec mod ' + str(sa.sets) + ')'}")
    for i, rec in enumerate(pattern[:10], 1):
        h1, i1 = dm.access(rec)
        h2, i2 = sa.access(rec)
        print(f"{i:>6}{rec:>8}   line {i1:<3}{'HIT ' if h1 else 'MISS':<15}set {i2:<3}{'HIT' if h2 else 'MISS'}")
    section("Hit ratio and EAT for different cache sizes (whole workload)")
    print(f"{'Lines':>6} | {'Direct hit%':>12}{'EAT ns':>9} | {'4-way hit%':>11}{'EAT ns':>9}")
    for lines in (8, 16, 32, 64):
        d, a = Cache(lines, 1), Cache(lines, CACHE_WAYS)
        for rec in pattern:
            d.access(rec)
            a.access(rec)
        mark = "  <- report configuration" if lines == CACHE_LINES else ""
        print(f"{lines:>6} | {d.hit_ratio() * 100:>11.1f}%{eat(d.hit_ratio()):>9.1f} | "
              f"{a.hit_ratio() * 100:>10.1f}%{eat(a.hit_ratio()):>9.1f}{mark}")
    print(f"\nWithout cache every access costs {TM} ns.")
    print("Observation: the working set (20 hot records) is larger than 16 lines, so a small cache")
    print("thrashes; a larger cache fixes this, and 4-way (LRU) avoids conflict misses of direct-mapped.")
    pause()


def demo_parallel():
    banner("PARALLEL PROCESSING - FLYNN: SISD vs SIMD vs MIMD")
    n = len(STUDENTS)
    print(f"{'Class':<7}{'Instruction streams':<22}{'Data streams':<14}Placement use")
    print(f"{'SISD':<7}{'1':<22}{'1':<14}one student checked at a time")
    print(f"{'SIMD':<7}{'1':<22}{'many':<14}same eligibility test on many student records")
    print(f"{'MIMD':<7}{'many':<22}{'many':<14}each company runs its own rules separately")

    section("SIMD: same test, 8 lanes (vector of 8 students per step)")
    c = COMPANIES[1]
    chunk = STUDENTS[:8]
    print(f"Company {c['name']}: CGPA>={c['min_cgpa']}, skills>={c['min_skills']}, backlogs<={c['max_backlogs']}")
    print("Lane      : " + " ".join(f"{s['id']:>4}" for s in chunk))
    print("CGPA      : " + " ".join(f"{s['cgpa']:>4}" for s in chunk))
    print("Skills    : " + " ".join(f"{s['skills']:>4}" for s in chunk))
    print("Backlogs  : " + " ".join(f"{s['backlogs']:>4}" for s in chunk))
    print("Eligible? : " + " ".join(f"{'yes' if software_eligible(s, c) else 'no':>4}" for s in chunk))
    print(f"\n{'Lanes':>6}{'SISD ops':>10}{'SIMD steps':>12}{'Speedup':>9}")
    for lanes in (1, 4, 8, 16):
        res, steps = simd_eligibility(STUDENTS, c, lanes)
        print(f"{lanes:>6}{n * OPS_PER_CHECK:>10}{steps:>12}{n * OPS_PER_CHECK / steps:>9.2f}")

    section(f"MIMD: {len(COMPANIES)} processors (threads), one per company, each with its own criteria")
    with ThreadPoolExecutor(max_workers=len(COMPANIES), thread_name_prefix="CPU") as ex:
        barrier = threading.Barrier(len(COMPANIES))
        results = list(ex.map(lambda c: mimd_worker(c, barrier), COMPANIES))
    print(f"{'Company':<10}{'Processor':<9}{'Eligible':>9}{'Ops':>7}")
    for name, thr, el, ops in results:
        print(f"{name:<10}{thr:<9}{el:>9}{ops:>7}")
    seq = sum(r[3] for r in results)
    par = max(r[3] for r in results)
    print(f"\nSequential ops = {seq}, MIMD parallel time = {par} ops  -> ideal speedup = {seq / par:.1f}x "
          f"(= number of processors)")
    best = (n * OPS_PER_CHECK * len(COMPANIES)) / (n / 8 * OPS_PER_CHECK)
    print(f"MIMD x SIMD(8 lanes) combined ideal speedup = {best:.0f}x")
    print("Note: threads model the MIMD organisation; Python's GIL means no real wall-clock gain.")
    pause()
