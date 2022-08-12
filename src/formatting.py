MATH_REPLACE = {
    "_0": "₀",
    "_1": "₁",
    "_2": "₂",
    "_3": "₃",
    "_4": "₄",
    "_5": "₅",
    "_6": "₆",
    "_7": "₇",
    "_8": "₈",
    "_9": "₉",
    "^0": "⁰",
    "^1": "¹",
    "^2": "²",
    "^3": "³",
    "^4": "⁴",
    "^5": "⁵",
    "^6": "⁶",
    "^7": "⁷",
    "^8": "⁸",
    "^9": "⁹"
}


def m(s: str):
    r = s
    for k, v in MATH_REPLACE.items():
        r = r.replace("{" + k + "}", v)
    return r


def subscript(n):
    return "".join(MATH_REPLACE[f"_{i}"] for i in str(int(n)))


def superscript(n):
    return "".join(MATH_REPLACE[f"^{i}"] for i in str(int(n)))


def solution_set(solutions: list):
    return "{" + ", ".join(set([str(e) for e in solutions])) + "}"


def error(s):
    return f"⚠️ {s}"
