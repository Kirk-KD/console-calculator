import { CommandInput } from "./modules/command-input.js";
import { commandInputToString } from "./modules/utilities.js";
import { DEFAULT_COMMAND_INPUT } from "./modules/constants.js";

var commandHistory = [];
var historyIndex = 0;
var acSelectionIndex = -1;

$(".ac-suggestions").hide();
$(".loading-indicator").hide();

var commandsInfo;
var helpHTML;
$.post({
    url: "/load_commands",
    async: false // blocking because must get `commandsInfo` for other code to work
}).done(response => {
    commandsInfo = response;

    // generate HTML for help command
    let helpHTMLs = [];
    for (const [name, command] of Object.entries(commandsInfo)) {
        helpHTMLs.push(command.helpHTML);
    }
    helpHTML = `<div class="console-element">
                    <div class="only-text help-msg">
                        <hr>
                        ${helpHTMLs.join("<br><br>")}
                    </div>
                </div>`;
});

function searchCommands(query, limit) {
    let results = {};

    for (const [name, detail] of Object.entries(commandsInfo)) {
        if (name.startsWith(query)) {
            results[name] = detail.parsedArgs;
            if (Object.keys(results).length == limit) break;
        }
    }

    return results;
}

function makeCommandResultElement(response) {
    return `<div class="console-element">
                <hr>
                <div class="original-command math">
                    <span class="command-name">${response.commandName}</span> ${response.parsedArgs}
                </div>
                <span class="command-result math">${response.commandResult}</span>
            </div>`;
}

function makeEvalResultElement(response) {
    return `<div class="console-element">
                <hr>
                <div class="original-expr math">${response.originalExpr}</div>
                <span class="command-result math">${response.result}</span>
            </div>`
}

function makeAutocompleteItems(searchResults) {
    let result = "";
    for (const [name, parsedArgs] of Object.entries(searchResults)) {
        result = `<div class="ac-suggestion-item" command-name="${name}">${name} 
            <span class="ac-args">${parsedArgs}</span></div>` + result;
    }
    return result;
}

function updateAutocomplete(commandName) {
    let searchResults = searchCommands(commandName, 10);
    let resultsLength = Object.keys(searchResults).length;
    if (resultsLength > 0) {
        $(".ac-suggestions").html(makeAutocompleteItems(searchResults)).show();
        acSelectionIndex = resultsLength - 1;
        $(".ac-suggestions").children()[acSelectionIndex].id = "ac-suggestion-item-selected";
        updateDescription();
    } else {
        $(".ac-suggestions").hide();
        $(".command-description").html("");
        acSelectionIndex = -1;
    }
}

function updateDescription() {
    let commandName = $("#ac-suggestion-item-selected").attr("command-name");
    $(".command-description").html(commandsInfo[commandName].description || "");
}

function parseCommandInputText(text) {
    /* Takes the parsed string of the command input and convert it to an object. */

    if (text.includes(" ")) {
        let [commandName, rawArgs] = text.split(" ");
        let args = rawArgs.split(",")

        return {commandName: commandName, arguments: args};
    } else return {expr: text};
}

// Show autocomplete items when autofocused/loaded
updateAutocomplete("");

$(".ac-suggestions").on("click", ".ac-suggestion-item", e => {
    let commandName = e.target.getAttribute("command-name");
    $("command-input")
        .html(commandNameToCommandInput(commandName))
        .attr("has-command-name", "true");
    updateAutocomplete(commandName);
});

$(".command-input").focus().on("click", e => {
    e.target.focus();
    CommandInput.moveCursorBeginOrEnd(e);
}).on("click", ".ci-clickable", e => {
    CommandInput.moveCursorToCharacterClicked(e);
}).on("keydown", e => {
    let selector = $(".command-input");
    let cursorSelector = $(".ci-has-cursor");

    if (e.key === "Tab") e.preventDefault();

    if (e.key.length === 1 && !e.ctrlKey) {
        CommandInput.addCharacter(e.key, selector, cursorSelector, updateAutocomplete);
    } else if (e.key === "Backspace") {
        CommandInput.backspace(selector, cursorSelector, updateAutocomplete);
    } else if (e.key === "Enter") {
        let commandString = commandInputToString(selector);
        
        function afterRequest() {
            commandHistory.push(selector.html());

            historyIndex = 0;
            selector.html(DEFAULT_COMMAND_INPUT).attr("has-command-name", "");;

            $(".ac-suggestions").html("").hide();
            $(".command-description").html("");
            $(".loading-indicator").hide();

            updateAutocomplete("");
        }

        if (commandString.length !== 0 && $(".loading-indicator").is(":hidden")) {
            $(".loading-indicator").show();

            let result = parseCommandInputText(commandString);

            if (result.expr !== undefined) {
                let exprData = JSON.stringify(result);

                $.post({
                    url: "/eval",
                    data: exprData,
                    contentType: "application/json;"
                }).done(response => {
                    $(".console-container").prepend(makeEvalResultElement(response));
                    afterRequest();
                });
            } else {
                let cmdData = JSON.stringify(result);

                $.post({
                    url: "/invoke",
                    data: cmdData,
                    contentType: "application/json;"
                }).done(response => {
                    $(".console-container").prepend(makeCommandResultElement(response));
                    afterRequest();
                });
            }
        }
    } else if (e.key === "ArrowUp" && e.ctrlKey) {
        if (commandHistory.length > 0 && commandHistory.length + historyIndex - 1 >= 0) {
            historyIndex--;
            selector.html(commandHistory[commandHistory.length + historyIndex]);
        }
    } else if (e.key === "ArrowDown" && e.ctrlKey) {
        if (commandHistory.length > 0 && commandHistory.length + historyIndex + 1 < commandHistory.length) {
            historyIndex++;
            selector.html(commandHistory[commandHistory.length + historyIndex]);
        }
    } else if (e.key === "ArrowLeft") {
        CommandInput.cursorLeft(cursorSelector);
    } else if (e.key === "ArrowRight") {
        CommandInput.cursorRight(cursorSelector);
    } else if (e.key === "Tab" && acSelectionIndex !== -1) {
        CommandInput.autocomplete(selector, cursorSelector, acSelectionIndex, updateAutocomplete);
    } else if (e.key == "ArrowUp" && acSelectionIndex !== -1) {
        let children = $(".ac-suggestions").children();
        children[acSelectionIndex].removeAttribute("id");

        acSelectionIndex--;
        if (acSelectionIndex < 0) acSelectionIndex = children.length - 1;
        children[acSelectionIndex].id = "ac-suggestion-item-selected";
        updateDescription();
    } else if (e.key == "ArrowDown" && acSelectionIndex !== -1) {
        let children = $(".ac-suggestions").children();
        children[acSelectionIndex].removeAttribute("id");

        acSelectionIndex++;
        if (acSelectionIndex >= children.length) acSelectionIndex = 0;
        children[acSelectionIndex].id = "ac-suggestion-item-selected";
        updateDescription();
    }
});