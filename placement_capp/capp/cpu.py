"""Mini CPU: assembler + executor (instruction cycle). MUL uses Booth."""
from capp.alu import booth_multiply


def program_text(company, scheduled=True):
    """One application = one short program. 'scheduled' groups the LOADs first so
    that no LOAD result is used by the very next instruction (avoids stalls)."""
    c = company
    if scheduled:
        head = """
            LOAD R1, cgpa
            LOAD R2, skills
            LOAD R3, backlogs
            MUL R4, R1, #2
            MUL R5, R2, #5
            MUL R6, R3, #-10
        """
    else:
        head = """
            LOAD R1, cgpa
            MUL R4, R1, #2
            LOAD R2, skills
            MUL R5, R2, #5
            LOAD R3, backlogs
            MUL R6, R3, #-10
        """
    tail = f"""
            ADD R4, R4, R5
            ADD R4, R4, R6
            STORE score, R4
            CMP R1, #{c['min_cgpa']}
            BLT REJ
            CMP R2, #{c['min_skills']}
            BLT REJ
            CMP R3, #{c['max_backlogs']}
            BGT REJ
            STORE status, #1
            JMP END
        REJ:
            STORE status, #0
        END:
            HALT
    """
    return head + tail


def is_reg(x):
    return len(x) > 1 and x[0] == "R" and x[1:].isdigit()


def assemble(src):
    labels, prog = {}, []
    for line in src.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(":"):
            labels[line[:-1]] = len(prog)
            continue
        op, _, rest = line.partition(" ")
        args = [a.strip() for a in rest.split(",")] if rest else []
        prog.append({"op": op, "args": args, "text": line, "dest": None, "srcs": []})
    for ins in prog:
        op, a = ins["op"], ins["args"]
        if op in ("BLT", "BGT", "JMP"):
            ins["target"] = labels[a[0]]
        if op == "LOAD":
            ins["dest"] = a[0]
        elif op == "MUL":
            ins["dest"], ins["srcs"] = a[0], [a[1]]
        elif op == "ADD":
            ins["dest"], ins["srcs"] = a[0], [a[1], a[2]]
        elif op == "CMP":
            ins["srcs"] = [x for x in a if is_reg(x)]
        elif op == "STORE":
            ins["srcs"] = [x for x in a[1:] if is_reg(x)]
    return prog


def run_cpu(prog, student):
    """Execute the program. MUL goes through the Booth multiplier. Returns the dynamic trace."""
    mem = {"cgpa": student["cgpa"], "skills": student["skills"],
           "backlogs": student["backlogs"], "status": None, "score": None}
    regs = {f"R{i}": 0 for i in range(8)}
    flags = {"N": False, "Z": False}
    trace, pc, booth_ops = [], 0, 0
    while True:
        ins = prog[pc]
        op, a = ins["op"], ins["args"]
        taken, note, npc = False, "", pc + 1
        if op == "LOAD":
            regs[a[0]] = mem[a[1]]
            note = f"{a[0]} <- M[{a[1]}] = {regs[a[0]]}"
        elif op == "MUL":
            imm = int(a[2][1:])
            regs[a[0]], _ = booth_multiply(regs[a[1]], imm)
            booth_ops += 1
            note = f"{a[0]} <- Booth({regs[a[1]]} x {imm}) = {regs[a[0]]}"
        elif op == "ADD":
            regs[a[0]] = regs[a[1]] + regs[a[2]]
            note = f"{a[0]} <- {a[1]} + {a[2]} = {regs[a[0]]}"
        elif op == "CMP":
            val = regs[a[0]]
            rhs = int(a[1][1:]) if a[1].startswith("#") else regs[a[1]]
            flags["N"], flags["Z"] = val < rhs, val == rhs
            note = f"compare {val} with {rhs}: N={int(flags['N'])} Z={int(flags['Z'])}"
        elif op in ("BLT", "BGT", "JMP"):
            taken = (flags["N"] if op == "BLT" else
                     (not flags["N"] and not flags["Z"]) if op == "BGT" else True)
            if taken:
                npc = ins["target"]
            note = f"{'TAKEN' if taken else 'not taken'} -> PC = {npc}"
        elif op == "STORE":
            val = int(a[1][1:]) if a[1].startswith("#") else regs[a[1]]
            mem[a[0]] = val
            note = f"M[{a[0]}] <- {val}"
        elif op == "HALT":
            note = "stop"
        trace.append({"pc": pc, "ins": ins, "taken": taken, "note": note})
        if op == "HALT":
            break
        pc = npc
    return regs, mem, trace, booth_ops


def status_text(mem):
    return "ELIGIBLE" if mem["status"] == 1 else "REJECTED"
