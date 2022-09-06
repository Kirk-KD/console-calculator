from evaluate import eval_math
from utils import *
from formatting import *


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


class ArgListTypeDiff(CommandError):
    def __init__(self, command_name: str, arg_list_name: str, arg_list_type: ArgType):
        super().__init__(
            f"{command_name} requires a {italic(arg_list_of(arg_list_type))} for its " +
            f"argument list, {italic(arg_list_name)}, but the wrong types were given."
        )


class ArgListNotEnoughArgs(CommandError):
    def __init__(self, command_name: str, arg_list_name: str):
        super().__init__(
            f"{command_name} requires at least 1 argument for its argument list, {italic(arg_list_name)}."
        )


class CommandNotFound(CommandError):
    def __init__(self, command_name: str):
        super().__init__(
            f"Unknown calculation command {command_name}"
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

        self.json = {}  # in browser command info
        self.parsed_arg_names_with_types = ""
        self.help_html = ""

    def convert_arguments(self, args: list[str]):
        raise NotImplementedError()
    
    def parse_arguments(self, args: list):
        raise NotImplementedError()
    
    def invoke(self, args: list[str]):
        raise NotImplementedError()
    
    def command_suggestion_json(self):
        raise NotImplementedError()


class Command(CommandBase):
    def __init__(self, function, description: str, args_to_types: dict[str, ArgType]):
        super().__init__(function, function.__name__, description)
        self.args_to_types = args_to_types

        self.parsed_arg_names = ", ".join(self.args_to_types.keys())
        self.parsed_arg_names_with_types = ", ".join(
            f"{k}: {v}" for k, v in self.args_to_types.items())
        
        self.help_html = (
            f'<span class="cmd-name">{self.name}</span> ' +
            f'<span class="cmd-args">{self.parsed_arg_names}</span><br>{self.description}'
        )
        self.json = {
            "parsedArgs": self.parsed_arg_names,
            "description": self.description,
            "helpHTML": self.help_html
        }
        
    def convert_arguments(self, args: list[str]):
        if len(args) != len(self.args_to_types):
            return ArgsLengthDiff(self, len(args))

        converted_result = []
        for actual, (expected_name, expected_type) in zip(args, self.args_to_types.items()):
            try:
                converted_result.append(expected_type.try_convert(actual))
            except ValueError:
                return ArgTypeDiff(self.name, expected_name, expected_type)
        
        return converted_result

    def parse_arguments(self, args: list):
        return ", ".join(f"{arg_name} = {arg_val}" for arg_name, arg_val in zip(self.args_to_types.keys(), args))

    def invoke(self, args: list[str]):
        converted_result = self.convert_arguments(args)
        if isinstance(converted_result, CommandError):  # use original `args` because args could not be parsed
            return CommandResult(self.name, self.parse_arguments(args), converted_result.message)
        
        func_result = self.function(*converted_result)  # either a CommandError or a str
        if isinstance(func_result, CommandError):  # use parsed `converted_result` for better formatting
            return CommandResult(self.name, self.parse_arguments(converted_result), func_result.message)
        
        return CommandResult(self.name, self.parse_arguments(converted_result), func_result)


class ArgListCommand(CommandBase):
    def __init__(self, function, description: str, arg_list_name: str, arg_list_type: ArgType):
        super().__init__(function, function.__name__, description)
        self.arg_list_name = arg_list_name
        self.arg_list_type = arg_list_type

        self.parsed_arg_names_with_type = f"{self.arg_list_name}: {arg_list_of(self.arg_list_type)}"

        self.help_html = (
            f'<span class="cmd-name">{self.name}</span> ' +
            f'<span class="cmd-args">{self.arg_list_name}</span><br>{self.description}'
        )
        self.json = {
            "parsedArgs": self.arg_list_name,
            "description": self.description,
            "helpHTML": self.help_html
        }
    
    def convert_arguments(self, args: list[str]):
        if len(args) == 0:
            return ArgListNotEnoughArgs(self.name, self.arg_list_name)

        converted_result = []
        for arg in args:
            try:
                converted_result.append(self.arg_list_type.try_convert(arg))
            except ValueError:
                return ArgListTypeDiff(self.name, self.arg_list_name, self.arg_list_type)
        
        return converted_result
    
    def parse_arguments(self, args: list):
        return ", ".join(str(i) for i in args)
    
    def invoke(self, args: list[str]):
        converted_result = self.convert_arguments(args)
        if isinstance(converted_result, CommandError):
            return CommandResult(self.name, self.parse_arguments(args), converted_result.message)
        
        func_result = self.function(*converted_result)
        if isinstance(func_result, CommandError):
            return CommandResult(self.name, self.parse_arguments(converted_result), func_result.message)
        
        return CommandResult(self.name, self.parse_arguments(converted_result), func_result)


class CommandsCollection:
    def __init__(self):
        self.commands: dict[str, CommandBase] = {}
    
    def load_commands_export(self):
        """Export a dict/json for command suggestions in frontend."""

        return {k: v.json for k, v in self.commands.items()}
    
    def invoke_command(self, command_name: str, arguments: list[str]):
        if command_name not in self.commands:
            return CommandResult(command_name, "", CommandNotFound(command_name).message)
        
        args_after_eval = []
        for arg in arguments:
            try:
                result, _ = eval_math(arg, do_unparse=False)
                args_after_eval.append(iof(result))
            except (ValueError, SyntaxError, TypeError):
                return CommandResult(command_name, "", error("Invalid math expression."))
            except ZeroDivisionError:
                return CommandResult(command_name, "", error("Cannot divide by zero."))

        return self.commands[command_name].invoke(args_after_eval)

    def search_commands(self, query: str, limit: int):
        matches = {}

        for command_name, command in self.commands.items():
            if command_name.startswith(query):
                matches[command_name] = command.parsed_arg_names_with_types
                if len(matches) == limit:
                    break
        
        return matches
    
    def command(self, description: str, args_to_types: dict[str, ArgType]):
        def inner(func):
            self.commands[func.__name__] = Command(
                func, math_format(description), {math_format(k): v for k, v in args_to_types.items()})
            return func
        return inner
    
    def arg_list_command(self, description: str, arg_list_name: str, arg_list_type: ArgType):
        def inner(func):
            self.commands[func.__name__] = ArgListCommand(
                func, math_format(description), math_format(arg_list_name), arg_list_type)
            return func
        return inner
