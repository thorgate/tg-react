#!/usr/bin/env node
/* eslint-disable */
/**
 * Extracts gettext() messages from js sources and writes them into Python file, so that they can be processed by
 * Django's builtin makemessages command.
 *
 * Give output filename and input filenames as commandline params.
 */

const fs = require('fs');
const babylon = require('babylon');
const traverse = require('babel-traverse').default;


const GETTEXT_FUNCS = [
    'ngettext',
    'npgettext',
    'pgettext',
    'gettext',
];


function getNodeValue(node) {
    if (node.type === 'StringLiteral') {
        return node.value;
    } else if (node.type === 'BinaryExpression' &&
        node.left.type === 'StringLiteral' && node.right.type === 'StringLiteral') {
        return getNodeValue(node.left) + getNodeValue(node.right);
    } else {
        return null;
    }
}


const visited_calls = [];
// Visits all call expressions, if the function name is among the ones we're interested in, then it adds info about this
//  call to visited_calls array.
const GettextVisitor = {
    CallExpression: function(path) {
        const func_name = path.node.callee.name;
        if (GETTEXT_FUNCS.indexOf(func_name) === -1) {
            return;
        }

        const call_spec = [func_name];
        path.node.arguments.forEach(function(arg, i) {
            const argValue = getNodeValue(arg);
            call_spec.push(argValue);
        });
        visited_calls.push(call_spec)
    },
};


function processFile(filename) {
    var file = fs.readFileSync(filename, 'utf8');
    var ast  = babylon.parse(file, {
        sourceType: 'module',

        plugins: [
            'jsx',
            'flow',
            'asyncFunctions',
            'classConstructorCall',
            'doExpressions',
            'trailingFunctionCommas',
            'objectRestSpread',
            'decorators',
            'classProperties',
            'exportExtensions',
            'exponentiationOperator',
            'asyncGenerators',
            'functionBind',
            'functionSent'
        ]
    });


    traverse(ast, GettextVisitor);
}


function writeOutput(filename, calls) {
    // each parsedCall is [key, [[func_name, param_1, param_2, ...], ...]]
    const parsedCalls = calls.map(function(call_spec) {
        const func_name = call_spec[0];
        if (func_name === 'gettext') {
            return [call_spec[1], [
                [func_name, call_spec[1]],
            ]];
        } else if (func_name === 'pgettext') {
            return [call_spec[1] + '\u0004' + call_spec[2], [
                [func_name, call_spec[1], call_spec[2]],
            ]];
        } else if (func_name === 'ngettext') {
            return [call_spec[1], [
                [func_name, call_spec[1], call_spec[2], 1],
                [func_name, call_spec[1], call_spec[2], 2],
            ]];
        } else if (func_name === 'npgettext') {
            return [call_spec[1] + '\u0004' + call_spec[2], [
                [func_name, call_spec[1], call_spec[2], call_spec[3], 1],
                [func_name, call_spec[1], call_spec[2], call_spec[3], 2],
            ]];
        }
    });
    // Filter out duplicates
    const seen_keys = [];
    const filteredCalls = parsedCalls.filter(function(call_spec) {
        const key = call_spec[0];
        const seen = seen_keys.indexOf(key) !== -1;
        if (!seen) {
            seen_keys.push(key);
        }
        return !seen;
    });
    filteredCalls.sort();

    // Create the output file's lines
    const lines = [
        'from django.utils.translation import gettext, pgettext, ngettext, npgettext',
        '',
        '',
        'def all_messages():',
        '    return {'
    ];
    function escapeValue(value) {
        return value.replace("'", "\\'").replace("\n", "\\n");
    }
    filteredCalls.forEach(function(call_spec) {
        lines.push("        '" + escapeValue(call_spec[0]) + "': [");
        call_spec[1].forEach(function(invocation) {
            const params = invocation.slice(1).map(function(param) {
                return (typeof param === 'number') ? param : ("'" + escapeValue(param) + "'");
            });
            lines.push("            " + invocation[0] + "(" + params.join(", ") + "),");
        });
        lines.push("        ],");
    });
    lines.push('    }');
    lines.push('');

    const source = lines.join('\n');
    fs.writeFileSync(filename, source);
}


if (process.argv.length < 4) {
    console.error('Usage:', process.argv[0], process.argv[1], '<output> <inputs>...');
    process.exit(0);
}

process.argv.slice(3).forEach(processFile);
writeOutput(process.argv[2], visited_calls);
