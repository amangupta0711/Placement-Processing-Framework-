"""Control unit: hardwired signals and micro-programmed control memory."""



def hardwired_signals(op, t):
    """Hardwired CU = decoder + AND/OR gates on (opcode, timing step). No memory lookup."""
    LOAD, CMP, STORE = op == "LOAD", op == "COMPARE", op == "STORE"
    T1, T2, T3 = t == 1, t == 2, t == 3
    sig = {
        "ADDR_OUT": (LOAD or STORE) and T1,
        "MEM_READ": LOAD and T2,
        "REG_WRITE": LOAD and T3,
        "REG_OUT": (CMP and T1) or (STORE and T2),
        "ALU_SUB": CMP and T2,
        "FLAG_WRITE": CMP and T3,
        "MEM_WRITE": STORE and T3,
    }
    return [k for k, v in sig.items() if v]


def micro(name, signals, desc, test=None):
    return {"name": name, "signals": signals, "desc": desc, "test": test}


BASE_ROUTINE = [
    micro("LOAD_CGPA", ["ADDR_OUT", "MEM_READ", "REG_WRITE"], "load CGPA"),
    micro("CMP_CGPA_MIN", ["REG_OUT", "ALU_SUB", "FLAG_WRITE"], "compare with company minimum",
          lambda s, c: s["cgpa"] >= c["min_cgpa"]),
    micro("CMP_BACKLOG_LIMIT", ["REG_OUT", "ALU_SUB", "FLAG_WRITE"], "compare backlogs with limit",
          lambda s, c: s["backlogs"] <= c["max_backlogs"]),
    micro("SET_ELIGIBLE", ["REG_OUT", "MEM_WRITE"], "set eligible flag"),
]


SKILL_MI = micro("CMP_SKILLS_MIN", ["REG_OUT", "ALU_SUB", "FLAG_WRITE"], "compare skills with minimum",
                 lambda s, c: s["skills"] >= c["min_skills"])


FULL_ROUTINE = BASE_ROUTINE[:2] + [SKILL_MI] + BASE_ROUTINE[2:]


def run_microroutine(routine, s, c):
    ok, rows = True, []
    for addr, m in enumerate(routine):
        if m["test"]:
            res = m["test"](s, c)
            ok = ok and res
            out = "PASS" if res else "FAIL"
        elif m["name"] == "SET_ELIGIBLE":
            out = "eligible = 1" if ok else "eligible = 0"
        else:
            out = "done"
        rows.append((addr, m, out))
    return ok, rows
