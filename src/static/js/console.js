import { CommandInput } from "./modules/command-input.js";
import {
    commandInputToString,
    getText,
    makeAutocompleteItems,
    makeCommandResultElement,
    makeEvalResultElement,
    parseCommandInputText
} from "./modules/utilities.js";
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

function onPressEnter(ciSelector) {
    let commandString = commandInputToString(ciSelector);
        
    function afterRequest() {
        commandHistory.push(ciSelector.html());

        historyIndex = 0;
        ciSelector.html(DEFAULT_COMMAND_INPUT).attr("has-command-name", "");

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
}

function onPressHistoryUp(ciSelector) {
    if (commandHistory.length > 0 && commandHistory.length + historyIndex - 1 >= 0) {
        historyIndex--;
        ciSelector.html(commandHistory[commandHistory.length + historyIndex]);
    }
}

function onPressHistoryDown(ciSelector) {
    if (commandHistory.length > 0 && commandHistory.length + historyIndex + 1 < commandHistory.length) {
        historyIndex++;
        ciSelector.html(commandHistory[commandHistory.length + historyIndex]);
    }
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
    let ciSelector = $(".command-input");
    let cursorSelector = $(".ci-has-cursor");

    CommandInput.register(ciSelector, cursorSelector, updateAutocomplete);

    if (e.key === "Tab") e.preventDefault();

    if (e.key.length === 1 && !e.ctrlKey) {
        CommandInput.addCharacter(e.key);
    } else if (e.key === "Backspace") {
        CommandInput.backspace();
    } else if (e.key === "Enter") {
        onPressEnter(ciSelector);
    } else if (e.key === "ArrowUp" && e.ctrlKey) {
        onPressHistoryUp(ciSelector);
    } else if (e.key === "ArrowDown" && e.ctrlKey) {
        onPressHistoryDown(ciSelector);
    } else if (e.key === "ArrowLeft") {
        CommandInput.cursorLeft();
    } else if (e.key === "ArrowRight") {
        CommandInput.cursorRight();
    } else if (e.key === "Tab" && acSelectionIndex !== -1) {
        CommandInput.autocomplete(acSelectionIndex);
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

$(".key").on("tap", function(e) {
    $(this).trigger("click");
    e.preventDefault();
    return false;
}).on("click", function(e) {
    let key = $(this);
    let ciSelector = $(".command-input");
    let cursorSelector = $(".ci-has-cursor");

    CommandInput.register(ciSelector, cursorSelector, updateAutocomplete);

    if (
        key.hasClass("key-letter") || key.hasClass("key-number") ||
        key.hasClass("key-op") || key.hasClass("key-comma")
    ) CommandInput.addCharacter(getText(key).toLowerCase());
    else if (key.hasClass("key-space")) CommandInput.addCharacter(" ");
    else if (key.hasClass("key-underscore")) CommandInput.addCharacter("_");
    else if (key.hasClass("key-backspace")) CommandInput.backspace();
    else if (key.hasClass("key-enter")) onPressEnter(ciSelector);
    else if (key.hasClass("key-switch")) {
        if ($(".keyboard-alpha").is(":hidden")) {
            $(".keyboard-alpha").show();
            $(".keyboard-math").hide();
        } else {
            $(".keyboard-alpha").hide();
            $(".keyboard-math").show();
        }
    } else if (key.hasClass("key-history-up")) onPressHistoryUp(ciSelector);
    else if (key.hasClass("key-history-down")) onPressHistoryDown(ciSelector);
});
