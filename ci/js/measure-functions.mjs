#!/usr/bin/env node
// Function-size measurer for tests/functional/test_function_size.py (T732, SEC-T677-01).
//
// Parses JavaScript with acorn (the exact version pinned in ci/js/package.json) and prints one JSON
// array on stdout: {file, name, startLine, endLine} for every function in the file. Counted are
// function declarations and expressions, arrow functions, object and class methods, getters,
// setters and class-field functions; a nested function is reported on its own (and still counts
// towards the lines of the function around it). Lines are 1-based and inclusive.
//
// A method, getter, setter or property-valued function starts at its key (so `static async get x(`
// counts from the key line); every other function starts at its own first token.
// Names: the function's own name, else the binding, property, method or assignment target it is
// stored in, `default` for an anonymous default export, else `(anonymous)` (a callback, an IIFE).
//
// Usage: node measure-functions.mjs FILE...       measure files read from disk
//        node measure-functions.mjs --stdin NAME  measure the source on stdin, reported as NAME
// Source type by extension: .mjs module, .cjs commonjs, .js module with a fallback to script.
// Exit 0 on success, 2 when a file does not parse (file:line:column on stderr), 64 on bad usage.
import { readFileSync } from "node:fs";
import { parse } from "acorn";

const FUNCTION_TYPES = new Set(["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]);
const KEYED_PARENTS = new Set(["MethodDefinition", "Property", "PropertyDefinition"]);

function isNode(value) {
  return value !== null && typeof value === "object" && typeof value.type === "string";
}

function keyName(key, computed) {
  if (computed) return "[computed]";
  if (key.type === "Identifier") return key.name;
  if (key.type === "PrivateIdentifier") return `#${key.name}`;
  if (key.type === "Literal") return String(key.value);
  return "[computed]";
}

function targetName(target) {
  if (target.type === "Identifier") return target.name;
  if (target.type === "MemberExpression") return keyName(target.property, target.computed);
  return null;
}

function nameOf(fn, parent) {
  if (fn.id) return fn.id.name;
  if (!parent) return "(anonymous)";
  if (parent.type === "VariableDeclarator" && parent.init === fn) return targetName(parent.id);
  if (KEYED_PARENTS.has(parent.type) && parent.value === fn) return keyName(parent.key, parent.computed);
  if (parent.type === "AssignmentExpression" && parent.right === fn) return targetName(parent.left);
  if (parent.type === "AssignmentPattern" && parent.right === fn) return targetName(parent.left);
  if (parent.type === "ExportDefaultDeclaration") return "default";
  return null;
}

function startLine(fn, parent) {
  const keyed = parent && KEYED_PARENTS.has(parent.type) && parent.value === fn;
  return keyed ? parent.loc.start.line : fn.loc.start.line;
}

function collect(node, parent, out) {
  if (FUNCTION_TYPES.has(node.type)) {
    const name = nameOf(node, parent) ?? "(anonymous)";
    out.push({ name, startLine: startLine(node, parent), endLine: node.loc.end.line });
  }
  for (const [key, value] of Object.entries(node)) {
    if (key === "loc") continue;
    const children = Array.isArray(value) ? value : [value];
    for (const child of children) {
      if (isNode(child)) collect(child, node, out);
    }
  }
}

function parseSource(file, source) {
  const options = { ecmaVersion: "latest", locations: true, allowHashBang: true };
  if (file.endsWith(".cjs")) return parse(source, { ...options, sourceType: "commonjs" });
  if (!file.endsWith(".js")) return parse(source, { ...options, sourceType: "module" });
  try {
    return parse(source, { ...options, sourceType: "module" });
  } catch {
    return parse(source, { ...options, sourceType: "script" });
  }
}

function measure(file, source) {
  const out = [];
  collect(parseSource(file, source), null, out);
  out.sort((a, b) => a.startLine - b.startLine || a.endLine - b.endLine);
  return out.map((entry) => ({ file, ...entry }));
}

function sources(argv) {
  if (argv[0] === "--stdin" && argv.length === 2) return [[argv[1], readFileSync(0, "utf8")]];
  if (argv.length === 0 || argv.some((arg) => arg.startsWith("-"))) return null;
  return argv.map((file) => [file, readFileSync(file, "utf8")]);
}

function main(argv) {
  const inputs = sources(argv);
  if (!inputs) {
    process.stderr.write("usage: measure-functions.mjs FILE... | --stdin NAME\n");
    return 64;
  }
  const results = [];
  for (const [file, source] of inputs) {
    try {
      results.push(...measure(file, source));
    } catch (error) {
      const where = error.loc ? `${error.loc.line}:${error.loc.column + 1}` : "?";
      process.stderr.write(`${file}:${where}: ${String(error.message).replace(/[^\x20-\x7e]/g, "?")}\n`);
      return 2;
    }
  }
  process.stdout.write(`${JSON.stringify(results)}\n`);
  return 0;
}

process.exitCode = main(process.argv.slice(2));
