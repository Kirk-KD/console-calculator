from flask import Flask, render_template, request
from commands import commands

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("console.html")


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=50)
