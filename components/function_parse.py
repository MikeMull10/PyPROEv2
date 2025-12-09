import re

def parse_function_offset(expr: str):
    expr = expr.strip().replace(" ", "")

    # Reject implicit multiplication: any number followed directly by a function name
    if re.search(r"\d[A-Za-z_]", expr):
        raise ValueError("Implicit multiplication is not allowed")

    # Try patterns in both orders ------------------------------------

    # Case 1: function first → f ± 3
    pattern_func_first = re.compile(
        r"""
        (?P<funcsign>[+\-]?)?
        (?P<func>[A-Za-z_][A-Za-z0-9_]*)
        (?P<op>[+\-])
        (?P<value>[+\-]?\d+(\.\d+)?)
        """,
        re.VERBOSE
    )

    # Case 2: number first → 3 ± f
    pattern_num_first = re.compile(
        r"""
        (?P<value>[+\-]?\d+(\.\d+)?)
        (?P<op>[+\-])
        (?P<funcsign>[+\-]?)?
        (?P<func>[A-Za-z_][A-Za-z0-9_]*)
        """,
        re.VERBOSE
    )

    # ---------------------------------------------------------------

    m = pattern_func_first.fullmatch(expr)
    if not m:
        m = pattern_num_first.fullmatch(expr)

    if not m:
        return None, None, None
        # raise ValueError("Invalid expression format")

    func = m.group("func")
    func_sign = m.group("funcsign") or "+"
    op = m.group("op")
    value = float(m.group("value"))

    # Normalize: treat "3 + -f" properly
    if func_sign == "-":
        func = "-" + func

    return func, op, value
