import math
from formatting import *

NUMBER = "Number"
STRING = "String"


class Commands:
    def __init__(self):
        self.commands = {}
    
    def convert_arguments(self, name: str, args: list):
        result = []
        types = list(self.commands[name]["args"].values())
        for i in range(len(args)):  # Assuming arguments length has been checked
            if types[i] == NUMBER:
                result.append(float(args[i]))
            else:
                result.append(args[i])
        return result
    
    def search_command(self, query: str, limit: int):
        names = {}
        if len(query):
            for name in self.commands.keys():
                if name.startswith(query):
                    names[name] = ", ".join(list(self.commands[name]["args"].keys()))
                    if len(names) == limit:
                        break
        return names

    def invoke_command(self, name: str, args: list):
        if name in self.commands.keys():
            if len(args) == len(self.commands[name]["args"]):
                converted_args = self.convert_arguments(name, args)
                
                arg_names = list(self.commands[name]["args"].keys())
                parsed_args = ', '.join([f'{arg_names[i]} = {args[i]}' for i in range(len(args))])

                command_res = self.commands[name]["func"](*converted_args)

                return (
                    parsed_args,
                    command_res
                )
            else:
                arg_names = list(self.commands[name]["args"].keys())
                expected_arg_len = len(arg_names)
                actual_arg_len = len(args)

                return "", error(
                    f"{name} requires {expected_arg_len} {'argument' if expected_arg_len == 1 else 'arguments'}"
                    + f" ({', '.join(arg_names)}) but {actual_arg_len} {'was' if actual_arg_len == 1 else 'were'} given."
                )
        else:
            return "", error(f"Unknown calculation command {name}.")
    
    def command(self, desc: str, args: dict[str, str]):
        def inner(func):
            self.commands[func.__name__] = {
                "func": func,
                "desc": m(desc),
                "args": {m(k): v for k, v in args.items()}
            }
            return func
        return inner


commands = Commands()


@commands.command(
    "Calculates the root(s) of a quadratic equation using a, b, and c " +
    "where ax{^2} + bx + c = 0, a != 0.",
    {
        "a": NUMBER,
        "b": NUMBER,
        "c": NUMBER
    }
)
def quadratic_roots(a, b, c):
    r = math.sqrt(abs(b**2 - 4 * a * c))
    return f"x = {solution_set([(-b + r) / (2 * a), (-b - r) / (2 * a)])}"


@commands.command(
    "Calculates the general term tn of an arithmetic sequence.",
    {
        "n": NUMBER,
        "t{_1}": NUMBER,
        "common difference": NUMBER
    }
)
def arithmetic_general_term(n, t1, d):
    tn = t1 + (n - 1) * d
    return f"t{subscript(n)} = {tn}"


@commands.command(
    "Calculates the sum Sn of an arithmetic sequence.",
    {
        "n": NUMBER,
        "t{_1}": NUMBER,
        "common difference": NUMBER
    }
)
def arithmetic_sum(n, t1, d):
    sn = (n/2) * (2 * t1 + (n - 1) * d)
    return f"S{subscript(n)} = {sn}"


@commands.command(
    "Calculates the general term tn of a geometric sequence.",
    {
        "n": NUMBER,
        "t{_1}": NUMBER,
        "common ratio": NUMBER
    }
)
def geometric_general_term(n, t1, r):
    tn = t1 * (r**(n-1))
    return f"t{subscript(n)} = {tn}"


@commands.command(
    "Calculates the sum Sn of a geometric sequence.",
    {
        "n": NUMBER,
        "t{_1}": NUMBER,
        "common ratio": NUMBER
    }
)
def geometric_sum(n, t1, r):
    sn = (t1 * (r**n - 1)) / (r - 1)
    return f"S{subscript(n)} = {sn}"


@commands.command(
    "Calculates the sum S∞ of an infinite geometric sequence, " +
    "where (-1 < common ratio < 1).",
    {
        "t{_1}": NUMBER,
        "common ratio": NUMBER
    }
)
def infinite_geometric_sum(t1, r):
    if not -1 < r < 1:
        return error("Common ratio must be greater than -1 and less than 1.")

    s_inf = t1 / (1 - r)
    return f"S∞ = {s_inf}"
