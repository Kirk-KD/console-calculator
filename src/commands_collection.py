from utils import *
from formatting import *

REAL = "Real Number"
INT = "Integer"
STRING = "String"


class CommandsCollection:
    def __init__(self):
        self.commands = {}
    
    def convert_arguments(self, name: str, args: list):
        result = []
        types = list(self.commands[name]["args"].values())

        for i in range(len(args)):  # Assuming arguments length has been checked
            t = types[i]
            a = args[i]

            try:
                if t == REAL:
                    result.append(int_or_float(a))
                elif t == INT:
                    result.append(int(a))
                else:
                    result.append(a)
            except ValueError:
                return -1

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

                if converted_args == -1:
                    expected_args = self.commands[name]['args']
                    return (
                        parsed_args,
                        error(
                            f"{name} requires {italic(', '.join([f'{k}: {v}' for k, v in expected_args.items()]))} " +
                            f"as {'argument' if len(expected_args) == 1 else 'arguments'}, " +
                            f"but the wrong {'type was' if len(expected_args) == 1 else 'types were'} given."
                        )
                    )

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
                "desc": math_format(desc),
                "args": {math_format(k): v for k, v in args.items()}
            }
            return func
        return inner