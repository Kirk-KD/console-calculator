import { CI_CURSOR } from "./constants.js";

export function commandInputToString(jquery) {
    /*
    Gets the content of command-input and parse it to pass 
    to the backend to be processed.

    `jquery`:
        the command-input or a child element to be parsed to 
        string recursively.
    */

    let result = "";

    jquery.children().each(function() {
        let child = $(this);
        if (
            child.hasClass("ci-digit") ||
            child.hasClass("ci-letter")
        ) result += getText(child);
        else if (
            child.hasClass("ci-binary-op") ||
            child.hasClass("ci-unary-op")
        ) result += undoReplaceMath(getText(child));
        else if (child.hasClass("ci-space")) result += " ";
        else if (child.hasClass("ci-comma")) result += ",";
        else if (child.hasClass("ci-superscript"))
            result += `**(${commandInputToString(child)})`;
    });

    return result;
}

export function getText(jquery) {
    /* Gets the text and not the children elements of a jquery. */

    return jquery[0].childNodes[0] ? jquery[0].childNodes[0].nodeValue : "";
}

export function replaceMath(input) {
    switch (input) {
        case "-": return "−"
        case "*": return "×"
        case "/": return "÷"
        default: return input
    }
}

export function undoReplaceMath(input) {
    switch (input) {
        case "−": return "-"
        case "×": return "*"
        case "÷": return "/"
        default: return input
    }
}

export function commandNameToCommandInput(commandName) {
    let html = `<span class="ci-root-cursor"></span>`;
    for (const c of commandName) {
        html += `<span class="ci-clickable ci-letter">${c}</span>`;
    }
    html += `<span class="ci-clickable ci-space ci-has-cursor">&ensp;${CI_CURSOR}</span>`;
    return html;
}

export function makeCommandResultElement(response) {
    return `<div class="console-element">
                <hr>
                <div class="original-command math">
                    <span class="command-name">${response.commandName}</span> ${response.parsedArgs}
                </div>
                <span class="command-result math">${response.commandResult}</span>
            </div>`;
}

export function makeEvalResultElement(response) {
    return `<div class="console-element">
                <hr>
                <div class="original-expr math">${response.originalExpr}</div>
                <span class="command-result math">${response.result}</span>
            </div>`
}

export function makeAutocompleteItems(searchResults) {
    let result = "";
    for (const [name, parsedArgs] of Object.entries(searchResults)) {
        result = `<div class="ac-suggestion-item" command-name="${name}">${name} 
            <span class="ac-args">${parsedArgs}</span></div>` + result;
    }
    return result;
}

export function parseCommandInputText(text) {
    /* Takes the parsed string of the command input and convert it to an object. */

    if (text.includes(" ")) {
        let [commandName, rawArgs] = text.split(" ");
        let args = rawArgs.split(",")

        return {commandName: commandName, arguments: args};
    } else return {expr: text};
}
