"""ALU: Booth signed multiplication (A, Q, Q-1, M registers)."""



def bstr(v, bits):
    return format(v & ((1 << bits) - 1), f"0{bits}b")


def to_signed(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


def booth_multiply(m, q, n=8):
    """M x Q using Booth's algorithm. Operands are n-bit signed (-127..127).
    Returns (product, steps); the 2n-bit product ends up in A:Q after n steps."""
    lim = (1 << (n - 1)) - 1
    if not (-lim <= m <= lim and -lim <= q <= lim):
        raise ValueError(f"operand outside {n}-bit signed range")
    mask = (1 << n) - 1
    M, A, Q, Qm1 = m & mask, 0, q & mask, 0
    steps = []
    for step in range(1, n + 1):
        pair = (Q & 1, Qm1)
        if pair == (1, 0):
            A = (A - M) & mask
            act = "A = A - M"
        elif pair == (0, 1):
            A = (A + M) & mask
            act = "A = A + M"
        else:
            act = "no operation"
        # arithmetic shift right of A:Q:Q-1 (sign bit of A is kept)
        Qm1 = Q & 1
        Q = ((Q >> 1) | ((A & 1) << (n - 1))) & mask
        A = ((A >> 1) | (A & (1 << (n - 1)))) & mask
        steps.append((step, f"{pair[0]}{pair[1]}", act, bstr(A, n), bstr(Q, n), Qm1))
    return to_signed((A << n) | Q, 2 * n), steps
