import math
from commands_collection import CommandsCollection, Real, Int, CommandError
from formatting import *
from utils import iof

commands = CommandsCollection()


@commands.command(
    "Calculates the root(s) of a quadratic equation using a, b, and c " +
    "where ax{^2} + bx + c = 0, a != 0.",
    {
        "a": Real(),
        "b": Real(),
        "c": Real()
    }
)
def quadratic_roots(a, b, c):
    d = b**2 - 4 * a * c
    if d < 0:
        return f"x = no solution"

    r = math.sqrt(d)
    return f"x = {solution_set([(-b + r) / (2 * a), (-b - r) / (2 * a)])}"


@commands.command(
    "Outputs the Vertex, Line of Symmetry, and Y-Intercept of a quadratic function " +
    "using a, b, and c where y = ax{^2} + bx + c, a != 0.",
    {
        "a": Real(),
        "b": Real(),
        "c": Real()
    }
)
def quadratic_info(a, b, c):
    symmetry_x = -b / (2 * a)
    vertex_x, vertex_y = symmetry_x, (4 * a * c - b ** 2) / (4 * a)
    y_int = c

    return (
        f"Line of Symmetry: x = {iof(symmetry_x)}<br>" +
        f"Vertex: ({iof(vertex_x)}, {iof(vertex_y)})<br>" +
        f"Y-Intercept: {y_int}"
    )


@commands.command(
    "Calculates the general term tn of an arithmetic sequence.",
    {
        "n": Int(),
        "t{_1}": Real(),
        "common difference": Real()
    }
)
def arithmetic_general_term(n, t1, d):
    tn = t1 + (n - 1) * d
    return f"t{subscript(n)} = {tn}"


@commands.command(
    "Calculates the sum Sn of an arithmetic sequence.",
    {
        "n": Int(),
        "t{_1}": Real(),
        "common difference": Real()
    }
)
def arithmetic_sum(n, t1, d):
    sn = (n/2) * (2 * t1 + (n - 1) * d)
    return f"S{subscript(n)} = {sn}"


@commands.command(
    "Calculates the general term tn of a geometric sequence.",
    {
        "n": Int(),
        "t{_1}": Real(),
        "common ratio": Real()
    }
)
def geometric_general_term(n, t1, r):
    tn = t1 * (r**(n-1))
    return f"t{subscript(n)} = {tn}"


@commands.command(
    "Calculates the sum Sn of a geometric sequence.",
    {
        "n": Int(),
        "t{_1}": Real(),
        "common ratio": Real()
    }
)
def geometric_sum(n, t1, r):
    sn = (t1 * (r**n - 1)) / (r - 1)
    return f"S{subscript(n)} = {sn}"


@commands.command(
    "Calculates the sum S∞ of an infinite geometric sequence, " +
    "where (-1 < common ratio < 1).",
    {
        "t{_1}": Real(),
        "common ratio": Real()
    }
)
def infinite_geometric_sum(t1, r):
    if not -1 < r < 1:
        return CommandError("Common ratio must be greater than -1 and less than 1.")

    s_inf = t1 / (1 - r)
    return f"S∞ = {s_inf}"


@commands.command(
    "Simplifies a square root.",
    {
        "radicand": Int(),
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
    return f"{m('sqrt')}{radical(r)} = {coef}" + \
        (f" {m('sqrt')}{radical(rad)}" if rad != 1 else "")


@commands.command(
    "Checks if an integer is prime.",
    {
        "n": Int()
    }
)
def is_prime(n):
    if n & 1 == 0:
        return f"{n} is not prime. (example: 2 {m('mul')} {n // 2})"

    d = 3
    while d * d <= n:
        if n % d == 0:
            return f"{n} is not prime. (example: {d} {m('mul')} {n // d})"
        d = d + 2
    
    return f"{n} is prime."


@commands.arg_list_command(
    "Calculates the Greatest Common Divisor of a list of integers.",
    "integers...",
    Int()
)
def gcd(*integers):
    r = math.gcd(*integers)
    result = f"GCD of {', '.join([str(i) for i in integers])} = {int(r)} ("
    examples = []
    for i in integers:
        examples.append(f"{i} {m('div')} {i // r}")
    return result + ", ".join(examples) + ")"


@commands.arg_list_command(
    "Calculates the Least Common Multiple of a list of integers.",
    "integers...",
    Int()
)
def lcm(*integers):
    r = math.lcm(*integers)
    result = f"LCM of {', '.join([str(i) for i in integers])} = {int(r)} ("
    examples = []
    for i in integers:
        examples.append(f"{i} {m('mul')} {r // i}")
    return result + ", ".join(examples) + ")"


@commands.command(
    "Calculates the area of a circle.",
    {
        "radius": Real()
    }
)
def circle_area(r):
    return f"Area of Cirle with radius of {r} = {r * r}{m('pi')} = {r * r * math.pi} unit{m('^2')}"


@commands.command(
    "Calculates the length of a line segment from (x{_1}, y{_1}) to (x{_2}, y{_2}).",
    {
        "x{_1}": Real(),
        "y{_1}": Real(),
        "x{_2}": Real(),
        "y{_2}": Real()
    }
)
def line_length(x1, y1, x2, y2):
    l = iof(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
    return f"Length of line segment from ({iof(x1)}, {iof(y1)}) to ({iof(x2)}, {iof(y2)}) = {l}"
