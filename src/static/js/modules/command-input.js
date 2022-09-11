import {
    commandInputToString,
    commandNameToCommandInput,
    getText,
    replaceMath,
    undoReplaceMath
} from "./utilities.js";
import {
    UPPER_ALPHA,
    LOWER_ALPHA,
    NUM_CHARS,
    OPERATORS,
    CONVERTED_OPERATORS,
    CI_CURSOR
} from "./constants.js";

function addCursor(jquery) {
    /* Adds a cursor to the end of a ci <span>. */

    let children = jquery.children();

    if (!children.last().hasClass("ci-cursor")) {
        jquery.append(CI_CURSOR).addClass("ci-has-cursor");
    }
}

function removeCursor(jquery) {
    /* Removes a cursor from a ci <span>. */
    
    let children = jquery.children();

    if (children.last().hasClass("ci-cursor")) {
        children.last().remove();
        jquery.removeClass("ci-has-cursor");
    }
}

export const CommandInput = {
    ciSelector: undefined,
    cursorSelector: undefined,
    updateAutocompleteFn: undefined,

    register: function(ciSelector, cursorSelector, updateAutocompleteFn) {
        CommandInput.ciSelector = ciSelector;
        CommandInput.cursorSelector = cursorSelector;
        CommandInput.updateAutocompleteFn = updateAutocompleteFn;
    },

    addCharacter: function(char) {
        if (NUM_CHARS.includes(char)) { // Single digit
            removeCursor(CommandInput.cursorSelector);
            CommandInput.cursorSelector.after(
                `<span class="ci-clickable ci-digit ci-has-cursor">${char}${CI_CURSOR}</span>`
            );
        } else if (OPERATORS.includes(char)) { // Binary and Unary operators
            removeCursor(CommandInput.cursorSelector);

            // the current + or - sign is an unary operator
            if ((char === "+" || char === "-") &&
                (CONVERTED_OPERATORS.includes(getText(CommandInput.cursorSelector))
                || getText(CommandInput.cursorSelector) === ""))
                CommandInput.cursorSelector.after(
                    `<span class="ci-clickable ci-unary-op ci-has-cursor">${replaceMath(char)}${CI_CURSOR}</span>`
                );
            else {
                CommandInput.cursorSelector.after(
                    `<span class="ci-clickable ci-binary-op ci-has-cursor">${replaceMath(char)}${CI_CURSOR}</span>`
                );
            }
        } else if (char === "^" && (NUM_CHARS + "()").includes(getText(CommandInput.cursorSelector))) { // Exponent
            removeCursor(CommandInput.cursorSelector);
            CommandInput.cursorSelector.after(
                `<span class="ci-superscript"><span class="ci-section-root-cursor ci-has-cursor">${CI_CURSOR}</span></span><span class="ci-end-superscript">&#8203</span>`
            );
        }

        // commands
        else if ((UPPER_ALPHA + LOWER_ALPHA + "_").includes(char)) {
            removeCursor(CommandInput.cursorSelector);
            CommandInput.cursorSelector.after(
                `<span class="ci-clickable ci-letter ci-has-cursor">${char}${CI_CURSOR}</span>`
            );

            CommandInput.updateAutocompleteFn(commandInputToString(CommandInput.ciSelector));
        } else if (char === " ") {
            if ( // inputting command name
                CommandInput.ciSelector.children().last().hasClass("ci-letter") &&
                CommandInput.cursorSelector.hasClass("ci-letter") &&
                !CommandInput.ciSelector.attr("has-command-name")
            ) {
                removeCursor(CommandInput.cursorSelector);
                CommandInput.cursorSelector.after(
                    `<span class="ci-clickable ci-space ci-has-cursor">&ensp;${CI_CURSOR}</span>`
                );
                CommandInput.ciSelector.attr("has-command-name", "true");
            }
        } else if (char === ",") {
            if(
                CommandInput.ciSelector.attr("has-command-name") &&
                !CommandInput.cursorSelector.hasClass("ci-space") &&
                !CommandInput.cursorSelector.hasClass("ci-comma") &&
                !CommandInput.cursorSelector.hasClass("ci-letter") &&
                !CommandInput.cursorSelector.next().hasClass("ci-space") &&
                !CommandInput.cursorSelector.next().hasClass("ci-comma") &&
                !CommandInput.cursorSelector.next().hasClass("ci-letter")
            ) {
                removeCursor(CommandInput.cursorSelector);
                CommandInput.cursorSelector.after(
                    `<span class="ci-clickable ci-comma ci-has-cursor">,&ensp;${CI_CURSOR}</span>`
                );
            }
        }
    },
    backspace: function() {
        // cursor is not at the very beginning of the input
        if (!CommandInput.cursorSelector.hasClass("ci-root-cursor")) {
            // cursor was at the beginning of a superscript
            if (CommandInput.cursorSelector.hasClass("ci-section-root-cursor")) {
                // move cursor outside of the superscript and add cursor
                addCursor(CommandInput.cursorSelector.parent().prev());
                CommandInput.cursorSelector.parent().remove();
            } else if (CommandInput.cursorSelector.hasClass("ci-space")) {
                CommandInput.ciSelector.attr("has-command-name", "");
                addCursor(CommandInput.cursorSelector.prev());
            } else if (CommandInput.cursorSelector.prev().hasClass("ci-superscript")) {
                addCursor(CommandInput.cursorSelector.prev().children().last());
            } else addCursor(CommandInput.cursorSelector.prev());

            CommandInput.cursorSelector.remove();

            CommandInput.updateAutocompleteFn(commandInputToString(CommandInput.ciSelector));
        }
    },
    cursorRight: function() {
        let next = CommandInput.cursorSelector.next();
        if (next.length) {
            if (next.hasClass("ci-superscript")) addCursor(next.children().first());
            else addCursor(next);
            removeCursor(CommandInput.cursorSelector);
        } else if (CommandInput.cursorSelector.parent().hasClass("ci-superscript")) { // cursorSelector is the last child of a ci-superscript
            let parentNext = CommandInput.cursorSelector.parent().next();
            if (parentNext.length) {
                addCursor(parentNext);
                removeCursor(CommandInput.cursorSelector);
            }
        }
    },
    cursorLeft: function() {
        let prev = CommandInput.cursorSelector.prev();
        if (prev.length) {
            if (prev.hasClass("ci-superscript")) addCursor(prev.children().last());
            else addCursor(prev);
            removeCursor(CommandInput.cursorSelector);
        } else if (CommandInput.cursorSelector.hasClass("ci-section-root-cursor")) {
            addCursor(CommandInput.cursorSelector.parent().prev());
            removeCursor(CommandInput.cursorSelector);
        }
    },
    autocomplete: function(acSelectionIndex) {
        let children = $(".ac-suggestions").children();
        let commandName = children[acSelectionIndex].getAttribute("command-name");

        removeCursor(CommandInput.cursorSelector);
        CommandInput.ciSelector.html(commandNameToCommandInput(commandName)).attr("has-command-name", "true");

        CommandInput.updateAutocompleteFn(commandName);
    },

    moveCursorBeginOrEnd: function(e) {
        let jElem = $(e.target);
        if (jElem.hasClass("command-input")) {
            let mouseX = e.pageX;
            let firstChild = jElem.children().first();
            let lastChild = jElem.children().last();
    
            if (mouseX < firstChild.offset().left) {
                removeCursor($(".ci-has-cursor"));
                addCursor(firstChild);
            } else if (mouseX > lastChild.offset().left + lastChild.width()) {
                removeCursor($(".ci-has-cursor"));
                addCursor(lastChild);
            }
        }
    },
    moveCursorToCharacterClicked: function(e) {
        let jElem = $(e.target);
        if (jElem.hasClass("ci-clickable")) {
            removeCursor($(".ci-has-cursor"));
    
            let mouseX = e.pageX - jElem.offset().left;
            let elemWidth = jElem.width();
            if (mouseX < elemWidth / 2) addCursor(jElem.prev());
            else addCursor(jElem);
        }
    }
};