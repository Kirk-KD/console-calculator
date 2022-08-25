from utils import *
from formatting import *

REAL = "Real Number"
INT = "Integer"
STRING = "String"


def arg_list_of(t: str):
    return f"List of {t}s"


class ArgType:
    def __init__(self, string_repr: str):
        self.string_repr = string_repr
    
    def try_convert(self, s: str):
        raise NotImplementedError()
    
    def __str__(self):
        return self.string_repr

    def __repr__(self):
        return self.string_repr


class Real(ArgType):
    def __init__(self):
        super().__init__("Real Number")
    
    def try_convert(self, s: str):
        return iof(s)


class Int(ArgType):
    def __init__(self):
        super().__init__("Integer")
    
    def try_convert(self, s: str):
        return int(s)  # would still raise ValueError if s is "1.0"


class CommandError:
    def __init__(self, msg: str):
        self.message = error(msg)


class ArgsLengthDiff(CommandError):
    def __init__(self, command, received_len: int):
        command_name = command.name
        arg_len = len(command.args_to_types)
        super().__init__(
            f"{command_name} requires {arg_len} {'argument' if arg_len == 1 else 'arguments'} " +
            f"({command.parsed_arg_names}) " +
            f"but {received_len} {'was' if received_len == 1 else 'were'} given."
        )


class ArgTypeDiff(CommandError):
    def __init__(self, command_name: str, arg_name: str, arg_type: ArgType):
        super().__init__(
            f"{command_name} requires {italic(f'{arg_name}: {arg_type}')} " +
            "as one of its arguments, but the wrong type was given."
        )


class CommandResult:
    def __init__(self, command_name: str, parsed_arguments: str, command_result: str):
        self.command_name = command_name
        self.parsed_arguments = parsed_arguments
        self.command_result = command_result

        self.json = {
            "commandName": self.command_name,
            "parsedArgs": self.parsed_arguments,
            "commandResult": self.command_result
        }


class CommandBase:
    def __init__(self, function, name: str, description: str):
        self.function = function
        self.name = name
        self.description = description

    def check_arguments(self, args: list[str]):
        raise NotImplementedError()
    
    def invoke(self, args: list[str]):
        raise NotImplementedError()


class Command(CommandBase):
    def __init__(self, function, description: str, args_to_types: dict[str, ArgType]):
        super().__init__(function, function.__name__, description)
        self.args_to_types = args_to_types

        # displayed strings
        self.parsed_arg_names = ", ".join(math_format(k) for k in self.args_to_types.keys())
        self.parsed_arg_names_with_types = ", ".join(
            f"{math_format(k)}: {v}" for k, v in self.args_to_types.items())
        
    def convert_arguments(self, args: list[str]):
        if len(args) != len(self.args_to_types):
            return ArgsLengthDiff(self, len(args))

        converted_result = []
        for actual, (expected_name, expected_type) in zip(args, self.args_to_types.keys()):
            try:
                converted_result.append(expected_type.try_convert(actual))
            except ValueError:
                return ArgTypeDiff(self.name, expected_name, expected_type)
        
        return converted_result

    def parse_received_args(self, args: list):
        return ", ".join(f"{arg_name} = {arg_val}" for arg_name, arg_val in zip(self.args_to_types.keys(), args))

    def invoke(self, args: list[str]):
        converted_result = self.convert_arguments(args)
        if isinstance(converted_result, CommandError):  # use original `args` because args could not be parsed
            return CommandResult(self.name, self.parse_received_args(args), converted_result.message)
        
        func_result = self.function(*converted_result)  # either a CommandError or a str
        if isinstance(func_result, CommandError):  # use parsed `converted_result` for better formatting
            return CommandResult(self.name, self.parse_received_args(converted_result), func_result.message)
        
        return CommandResult(self.name, self.parse_received_args(converted_result), func_result)


class ArgListCommand(CommandBase):
    def __init__(self, function, description: str, arg_list_name: str, arg_list_type: ArgType):
        super().__init__(function, function.__name__, description)
        self.arg_list_name = arg_list_name
        self.arg_list_type = arg_list_type

        # displayed strings
        self.parsed_arg_name_with_type = f"{self.arg_list_name}: {arg_list_of(self.arg_list_type)}"


class CommandsCollection:
    def __init__(self):
        self.commands: dict[str, Command] = {}
    
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
