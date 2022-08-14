import math
from commands_collection import CommandsCollection, REAL, INT, STRING
from formatting import *

commands = CommandsCollection()


@commands.command(
    "Calculates the root(s) of a quadratic equation using a, b, and c " +
    "where ax{^2} + bx + c = 0, a != 0.",
    {
        "a": REAL,
        "b": REAL,
        "c": REAL
    }
)
def quadratic_roots(a, b, c):
    r = math.sqrt(abs(b**2 - 4 * a * c))
    return f"x = {solution_set([(-b + r) / (2 * a), (-b - r) / (2 * a)])}"


@commands.command(
    "Calculates the general term tn of an arithmetic sequence.",
    {
        "n": INT,
        "t{_1}": REAL,
        "common difference": REAL
    }
)
def arithmetic_general_term(n, t1, d):
    tn = t1 + (n - 1) * d
    return f"t{subscript(n)} = {tn}"


@commands.command(
    "Calculates the sum Sn of an arithmetic sequence.",
    {
        "n": INT,
        "t{_1}": REAL,
        "common difference": REAL
    }
)
def arithmetic_sum(n, t1, d):
    sn = (n/2) * (2 * t1 + (n - 1) * d)
    return f"S{subscript(n)} = {sn}"


@commands.command(
    "Calculates the general term tn of a geometric sequence.",
    {
        "n": INT,
        "t{_1}": REAL,
        "common ratio": REAL
    }
)
def geometric_general_term(n, t1, r):
    tn = t1 * (r**(n-1))
    return f"t{subscript(n)} = {tn}"


@commands.command(
    "Calculates the sum Sn of a geometric sequence.",
    {
        "n": INT,
        "t{_1}": REAL,
        "common ratio": REAL
    }
)
def geometric_sum(n, t1, r):
    sn = (t1 * (r**n - 1)) / (r - 1)
    return f"S{subscript(n)} = {sn}"


@commands.command(
    "Calculates the sum S∞ of an infinite geometric sequence, " +
    "where (-1 < common ratio < 1).",
    {
        "t{_1}": REAL,
        "common ratio": REAL
    }
)
def infinite_geometric_sum(t1, r):
    if not -1 < r < 1:
        return error("Common ratio must be greater than -1 and less than 1.")

    s_inf = t1 / (1 - r)
    return f"S∞ = {s_inf}"


@commands.command(
    "Simplifies a square root.",
    {
        "radicand": INT,
    }
)
def simplify_square_root(r):
    def simpl_sqrt(num):
        for i in range(2, num):
            div, mod = divmod(num, i*i)
            if mod == 0:
                sq1, sq2 = simpl_sqrt(div)
                return (i * sq1, sq2)
            if div == 0:
                break
        return (1, num)

    coef, rad = simpl_sqrt(r)
    return f"{m('sqrt')}{radical(r)} = {coef}{m('sqrt')}{radical(rad)}"
