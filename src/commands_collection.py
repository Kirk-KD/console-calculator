from utils import *
from formatting import *

REAL = "Real Number"
INT = "Integer"
STRING = "String"


def arg_list_of(t: str):
    return f"List of {t}s"


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
                    result.append(iof(a))
                elif t == INT:
                    result.append(int(a))
                else:
                    result.append(a)
            except ValueError:
                return -1

        return result
    
    def convert_arguments_list(self, name: str, args: list):
        result = []
        type = self.commands[name]["arg_list_type"]

        for a in args:
            try:
                if type == REAL:
                    result.append(iof(a))
                elif type == INT:
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
                    names[name] = (
                        self.commands[name]["arg_list_name"]
                        if self.commands[name]["arg_list"]
                        else ", ".join(list(self.commands[name]["args"].keys()))
                    )
                    if len(names) == limit:
                        break
        return names
    
    def get_description(self, name: str):
        return self.commands.get(name, {"desc": None})["desc"]

    def invoke_command(self, name: str, args: list):
        if name in self.commands.keys():
            if self.commands[name]["arg_list"]:
                if len(args) > 0:
                    converted_args = self.convert_arguments_list(name, args)
                    parsed_args = ", ".join(args)

                    if converted_args == -1:  # wrong argument types
                        return (
                            parsed_args,
                            error(
                                f"{name} requires a {italic(arg_list_of(self.commands[name]['arg_list_type']))} " +
                                f"as arguments, but the wrong types were given."
                            )
                        )
                    
                    command_res = self.commands[name]["func"](*converted_args)

                    return (
                        parsed_args,
                        command_res
                    )
                else:
                    return "", error(
                        f"{name} requires at least 1 argument of type {italic(self.commands[name]['arg_list_type'])} " +
                        "for its argument list."
                    )
            else:
                if len(args) == len(self.commands[name]["args"]):
                    converted_args = self.convert_arguments(name, args)

                    arg_names = list(self.commands[name]["args"].keys())
                    parsed_args = ', '.join([f'{arg_names[i]} = {args[i]}' for i in range(len(args))])

                    if converted_args == -1:  # wrong argument types
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
                "arg_list": False,
                "func": func,
                "desc": math_format(desc),
                "args": {math_format(k): v for k, v in args.items()}
            }
            return func
        return inner
    
    def arg_list_command(self, desc: str, arg_list_name: str, arg_list_type: str):
        def inner(func):
            self.commands[func.__name__] = {
                "arg_list": True,
                "func": func,
                "desc": math_format(desc),
                "arg_list_name": math_format(arg_list_name),
                "arg_list_type": arg_list_type
            }
            return func
        return inner
    
    def command_help_html(self, name: str):
        cmd = self.commands[name]
        # args_str = (
        #     ", ".join([f"{k}: {v}" for k, v in cmd["args"].items()])
        #     if not cmd["arg_list"]
        #     else f"{cmd['arg_list_name']}: {arg_list_of(cmd['arg_list_type'])}"
        # )
        args_str = (
            ", ".join(cmd["args"].keys())
            if not cmd["arg_list"]
            else cmd["arg_list_name"]
        )
        desc = cmd["desc"]
        return f"""
        <span class="cmd-name">{name}</span> <span class="cmd-args">{args_str}</span><br>{desc}
        """
