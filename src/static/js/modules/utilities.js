import {
    CI_CURSOR,
    CONVERTED_OPERATORS,
    NUM_CHARS,
    OPERATORS,
    UPPER_ALPHA,
    LOWER_ALPHA
} from "./constants.js";

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
        else if (child.hasClass("ci-bracket-left")) result += "(";
        else if (child.hasClass("ci-bracket-right")) result += ")";
    });

    return result;
}

export function stringToMath(string, startingIndex = 0, useEndingBracket = false) {
    /*
    Converts a string to a ci element.
    */

    let result = "";
    let cleanString = string.replaceAll(" ", "").replaceAll("**", "^");

    let leftBracket = 1, rightBracket = 0;

    let index = startingIndex;
    while (index < cleanString.length) {
        let char = cleanString[index];

        if (NUM_CHARS.includes(char))
            result += `<span class="ci-digit">${char}</span>`;
        else if (OPERATORS.includes(char)) {
            if (("+-".includes(char)) &&
                (CONVERTED_OPERATORS.includes(cleanString[index - 1]) || index === 0))
                result += `<span class="ci-unary-op">${replaceMath(char)}</span>`;
            else
                result += `<span class="ci-binary-op">${replaceMath(char)}</span>`;
        } else if (char === "^") {
            result += `<span class="ci-superscript"><span class="ci-section-root-cursor"></span>`;
            if (cleanString[index + 1] === "(") {
                let res = stringToMath(cleanString, index + 2, true);
                result += res.result;
                index = res.endIndex;
            } else {
                while (NUM_CHARS.includes(cleanString[index])) {
                    result += `<span class="ci-digit">${cleanString[index]}</span>`;
                    index++;
                }
                index--;
            }
            result += `</span><span class="ci-end-superscript">&#8203</span>`;
        } else if (char === "(") {
            leftBracket++;
            result += `<span class="ci-bracket-left">(</span>`;
        } else if (char === ")") {
            rightBracket++;
            if (useEndingBracket && rightBracket === leftBracket) break;
            result += `<span class="ci-bracket-right">)</span>`;
        }

        index++;
    }

    return {
        result: result,
        endIndex: index + 1
    };
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
                <div class="original-expr math">${stringToMath(response.originalExpr).result}</div>
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
