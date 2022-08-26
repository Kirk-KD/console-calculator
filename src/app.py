import sys
import os
from flask import Flask, render_template, request
from commands import commands
from evaluate import eval_math
from utils import iof
from formatting import error

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("console.html")


@app.route("/eval", methods=["POST"])
def eval_():
    expr = request.json["expr"]
    try:
        result, unparsed = eval_math(expr)
        return {
            "originalExpr": unparsed,
            "result": iof(result)
        }
    except (ValueError, SyntaxError, TypeError):
        return {
            "originalExpr": expr,
            "result": error("Invalid math expression.")
        }
    except ZeroDivisionError:
        return {
            "originalExpr": expr,
            "result": error("Cannot divide by zero.")
        }


@app.route("/calculate", methods=["POST"])
def calculate():
    json = request.json

    command_name = json["commandName"]
    command_arguments = json["arguments"]

    command_result = commands.invoke_command(command_name, command_arguments)
    return command_result.json


@app.route("/load_commands", methods=["POST"])
def load_commands():
    return commands.load_commands_export()


@app.route("/help", methods=["POST"]) 
def help_msg():
    return '<div class="console-element"><div class="only-text help-msg"><hr>' + ("<br><br>".join(
        [commands.command_help_html(name) for name in commands.commands.keys()])) + "</div></div>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=(len(sys.argv) > 1 and sys.argv[1] == "debug"))
