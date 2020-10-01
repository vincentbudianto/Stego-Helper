/* All string-related utility function is stored here */
let a = "A";

module.exports = {
    /**
     * Removes all non alphabet and capitalize each letters (including spaces & newlines)
     * @param {String} input
     * @returns {String}
     */
    removeNonAlphabet : function (input) {
        return input.replace(/[^a-zA-Z]/gi, '').toUpperCase();
    },

    /**
     * Converts all alphabet to ASCII
     * @param {String} input - All characters must be upper case alphabet
     * @returns {Array} - Array of order numbers
     */
    toASCII: function(input) {
        let out = [];

        for (var i = 0; i < input.length; i++) {
            out.push(input.charCodeAt(i));
        }

        return out;
    },

    /**
     * Converts all alphabet to its order in alphabet (e.g. J -> 10)
     * @param {String} input - All characters must be upper case alphabet
     * @returns {Array} - Array of order numbers
     */
    toNumbers: function(input) {
        input = this.removeNonAlphabet(input);

        let out = 0;

        for (let i = 0; i < input.length; i++) {
            out += (input.charCodeAt(i) - a.charCodeAt(0));
        }

        return out;
    },

    /**
     * Mod operator (eg: mod(-10, 26) = 16)
     * @param {Number} a
     * @param {Number} b
     * @returns {Number}
     */
    mod: function(a, b) {
        let res = a % b;

        return Math.floor(res >= 0 ? res : this.mod(a + b, b));
    }
}