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
    except (ValueError, SyntaxError):
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

    parsed_args, command_result = commands.invoke_command(command_name, command_arguments)
    return {
        "commandName": command_name,
        "parsedArgs": parsed_args,
        "commandResult": command_result
    }


@app.route("/description", methods=["POST"])
def description():
    name = request.json["name"]
    return {
        "description": commands.get_description(name)
    }


@app.route("/search", methods=["POST"])
def search():
    query = request.json["query"]
    results = commands.search_command(query, 10)
    return {
        "isEmpty": len(results) == 0,
        "commands": results
    }

app.run(host="0.0.0.0", port=443)
