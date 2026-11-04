"""5-stage pipeline timing with automatic hazard detection."""



def schedule_pipeline(trace, forwarding=True):
    """In-order IF-ID-EX-MEM-WB. Hazards found automatically from register dependencies.
      * data hazard (RAW): with forwarding only LOAD->use needs 1 stall;
                           without forwarding: distance 1 -> 2 stalls, distance 2 -> 1 stall
      * control hazard   : 1 bubble after a taken branch / jump (as in the report)"""
    rows, hazards = [], []
    e_prev, x_prev = 1, 0
    for i, t in enumerate(trace):
        ins = t["ins"]
        ctrl = 1 if (i > 0 and trace[i - 1]["taken"]) else 0
        data, why = 0, ""
        for dist in (1, 2):
            j = i - dist
            if j < 0:
                continue
            p = trace[j]["ins"]
            if p["dest"] and p["dest"] in ins["srcs"]:
                need = (1 if (p["op"] == "LOAD" and dist == 1) else 0) if forwarding else 3 - dist
                if need > data:
                    data = need
                    why = f"{p['dest']} produced by #{j + 1:02d} {p['op']} (distance {dist})"
        if ctrl:
            hazards.append(f"#{i + 1:02d} {ins['text']}: CONTROL hazard - previous branch/jump taken, 1 bubble")
        if data:
            kind = "load-use" if forwarding else "RAW"
            hazards.append(f"#{i + 1:02d} {ins['text']}: DATA hazard ({kind}) - needs {why}, {data} stall(s)")
        s = ctrl + data
        e = 2 if i == 0 else x_prev
        x = e + 1 + s
        rows.append({"text": ins["text"], "if": (e_prev, e - 1), "id": e, "st": (e + 1, x - 1),
                     "ex": x, "mem": x + 1, "wb": x + 2, "stalls": s})
        e_prev, x_prev = e, x
    stalls = sum(r["stalls"] for r in rows)
    return rows, rows[-1]["wb"], hazards, stalls
