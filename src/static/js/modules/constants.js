export const UPPER_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
export const LOWER_ALPHA = UPPER_ALPHA.toLowerCase();
export const NUM_CHARS = "0123456789.";
export const OPERATORS = "+-*/";
export const CONVERTED_OPERATORS = "+−×÷";

/*
CI_CURSOR should be used as a child of a non-container ci-type such as
a ci-digit, and NOT a ci-superscript. The purpose of CI_CURSOR is only
to display the blinking cursor correctly.
*/
export const CI_CURSOR = `<span class="ci-cursor">&#8203</span>`;
export const DEFAULT_COMMAND_INPUT = `<span class="ci-root-cursor ci-has-cursor">${CI_CURSOR}</span>`;
