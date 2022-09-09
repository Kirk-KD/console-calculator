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
    addCharacter: function(char, selector, cursorSelector, updateAutocompleteFn) {
        if (NUM_CHARS.includes(char)) { // Single digit
            if (!cursorSelector.hasClass("ci-letter")) {
                removeCursor(cursorSelector);
                cursorSelector.after(
                    `<span class="ci-clickable ci-digit ci-has-cursor">${char}${CI_CURSOR}</span>`
                );
            }
        } else if (OPERATORS.includes(char)) { // Binary and Unary operators
            removeCursor(cursorSelector);

            // the current + or - sign is an unary operator
            if ((char === "+" || char === "-") &&
                (CONVERTED_OPERATORS.includes(getText(cursorSelector))
                || getText(cursorSelector) === ""))
                cursorSelector.after(
                    `<span class="ci-clickable ci-unary-op ci-has-cursor">${replaceMath(char)}${CI_CURSOR}</span>`
                );
            else {
                cursorSelector.after(
                    `<span class="ci-clickable ci-binary-op ci-has-cursor">${replaceMath(char)}${CI_CURSOR}</span>`
                );
            }
        } else if (char === "^" && (NUM_CHARS + "()").includes(getText(cursorSelector))) { // Exponent
            removeCursor(cursorSelector);
            cursorSelector.after(
                `<span class="ci-superscript"><span class="ci-section-root-cursor ci-has-cursor">${CI_CURSOR}</span></span><span class="ci-end-superscript">&#8203</span>`
            );
        }

        // commands
        else if ((UPPER_ALPHA + LOWER_ALPHA + "_").includes(char)) {
            removeCursor(cursorSelector);
            cursorSelector.after(
                `<span class="ci-clickable ci-letter ci-has-cursor">${char}${CI_CURSOR}</span>`
            );

            updateAutocompleteFn(commandInputToString(selector));
        } else if (char === " ") {
            if ( // inputting command name
                selector.children().last().hasClass("ci-letter") &&
                cursorSelector.hasClass("ci-letter") &&
                !selector.attr("has-command-name")
            ) {
                removeCursor(cursorSelector);
                cursorSelector.after(
                    `<span class="ci-clickable ci-space ci-has-cursor">&ensp;${CI_CURSOR}</span>`
                );
                selector.attr("has-command-name", "true");
            }
        } else if (char === ",") {
            if(
                selector.attr("has-command-name") &&
                !cursorSelector.hasClass("ci-space") &&
                !cursorSelector.hasClass("ci-comma") &&
                !cursorSelector.hasClass("ci-letter") &&
                !cursorSelector.next().hasClass("ci-space") &&
                !cursorSelector.next().hasClass("ci-comma") &&
                !cursorSelector.next().hasClass("ci-letter")
            ) {
                removeCursor(cursorSelector);
                cursorSelector.after(
                    `<span class="ci-clickable ci-comma ci-has-cursor">,&ensp;${CI_CURSOR}</span>`
                );
            }
        }
    },
    backspace: function(selector, cursorSelector, updateAutocompleteFn) {
        // cursor is not at the very beginning of the input
        if (!cursorSelector.hasClass("ci-root-cursor")) {
            // cursor was at the beginning of a superscript
            if (cursorSelector.hasClass("ci-section-root-cursor")) {
                // move cursor outside of the superscript and add cursor
                addCursor(cursorSelector.parent().prev());
                cursorSelector.parent().remove();
            } else if (cursorSelector.hasClass("ci-space")) {
                selector.attr("has-command-name", "");
                addCursor(cursorSelector.prev());
            } else if (cursorSelector.prev().hasClass("ci-superscript")) {
                addCursor(cursorSelector.prev().children().last());
            } else addCursor(cursorSelector.prev());

            cursorSelector.remove();

            updateAutocompleteFn(commandInputToString(selector));
        }
    },
    cursorRight: function(cursorSelector) {
        let next = cursorSelector.next();
        if (next.length) {
            if (next.hasClass("ci-superscript")) addCursor(next.children().first());
            else addCursor(next);
            removeCursor(cursorSelector);
        } else if (cursorSelector.parent().hasClass("ci-superscript")) { // cursorSelector is the last child of a ci-superscript
            let parentNext = cursorSelector.parent().next();
            if (parentNext.length) {
                addCursor(parentNext);
                removeCursor(cursorSelector);
            }
        }
    },
    cursorLeft: function(cursorSelector) {
        let prev = cursorSelector.prev();
        if (prev.length) {
            if (prev.hasClass("ci-superscript")) addCursor(prev.children().last());
            else addCursor(prev);
            removeCursor(cursorSelector);
        } else if (cursorSelector.hasClass("ci-section-root-cursor")) {
            addCursor(cursorSelector.parent().prev());
            removeCursor(cursorSelector);
        }
    },
    autocomplete: function(selector, cursorSelector, acSelectionIndex, updateAutocompleteFn) {
        let children = $(".ac-suggestions").children();
        let commandName = children[acSelectionIndex].getAttribute("command-name");

        removeCursor(cursorSelector);
        selector.html(commandNameToCommandInput(commandName)).attr("has-command-name", "true");

        updateAutocompleteFn(commandName);
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