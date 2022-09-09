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
