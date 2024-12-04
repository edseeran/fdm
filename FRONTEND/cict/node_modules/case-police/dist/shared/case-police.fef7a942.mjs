import { existsSync, promises } from 'node:fs';
import path from 'node:path';
import require$$0 from 'tty';
import { dictDir } from '../dirs.mjs';

var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

function getDefaultExportFromCjs (x) {
	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
}

var picocolors = {exports: {}};

let tty = require$$0;

let isColorSupported =
	!("NO_COLOR" in process.env || process.argv.includes("--no-color")) &&
	("FORCE_COLOR" in process.env ||
		process.argv.includes("--color") ||
		process.platform === "win32" ||
		(tty.isatty(1) && process.env.TERM !== "dumb") ||
		"CI" in process.env);

let formatter =
	(open, close, replace = open) =>
	input => {
		let string = "" + input;
		let index = string.indexOf(close, open.length);
		return ~index
			? open + replaceClose(string, close, replace, index) + close
			: open + string + close
	};

let replaceClose = (string, close, replace, index) => {
	let start = string.substring(0, index) + replace;
	let end = string.substring(index + close.length);
	let nextIndex = end.indexOf(close);
	return ~nextIndex ? start + replaceClose(end, close, replace, nextIndex) : start + end
};

let createColors = (enabled = isColorSupported) => ({
	isColorSupported: enabled,
	reset: enabled ? s => `\x1b[0m${s}\x1b[0m` : String,
	bold: enabled ? formatter("\x1b[1m", "\x1b[22m", "\x1b[22m\x1b[1m") : String,
	dim: enabled ? formatter("\x1b[2m", "\x1b[22m", "\x1b[22m\x1b[2m") : String,
	italic: enabled ? formatter("\x1b[3m", "\x1b[23m") : String,
	underline: enabled ? formatter("\x1b[4m", "\x1b[24m") : String,
	inverse: enabled ? formatter("\x1b[7m", "\x1b[27m") : String,
	hidden: enabled ? formatter("\x1b[8m", "\x1b[28m") : String,
	strikethrough: enabled ? formatter("\x1b[9m", "\x1b[29m") : String,
	black: enabled ? formatter("\x1b[30m", "\x1b[39m") : String,
	red: enabled ? formatter("\x1b[31m", "\x1b[39m") : String,
	green: enabled ? formatter("\x1b[32m", "\x1b[39m") : String,
	yellow: enabled ? formatter("\x1b[33m", "\x1b[39m") : String,
	blue: enabled ? formatter("\x1b[34m", "\x1b[39m") : String,
	magenta: enabled ? formatter("\x1b[35m", "\x1b[39m") : String,
	cyan: enabled ? formatter("\x1b[36m", "\x1b[39m") : String,
	white: enabled ? formatter("\x1b[37m", "\x1b[39m") : String,
	gray: enabled ? formatter("\x1b[90m", "\x1b[39m") : String,
	bgBlack: enabled ? formatter("\x1b[40m", "\x1b[49m") : String,
	bgRed: enabled ? formatter("\x1b[41m", "\x1b[49m") : String,
	bgGreen: enabled ? formatter("\x1b[42m", "\x1b[49m") : String,
	bgYellow: enabled ? formatter("\x1b[43m", "\x1b[49m") : String,
	bgBlue: enabled ? formatter("\x1b[44m", "\x1b[49m") : String,
	bgMagenta: enabled ? formatter("\x1b[45m", "\x1b[49m") : String,
	bgCyan: enabled ? formatter("\x1b[46m", "\x1b[49m") : String,
	bgWhite: enabled ? formatter("\x1b[47m", "\x1b[49m") : String,
});

picocolors.exports = createColors();
picocolors.exports.createColors = createColors;

var picocolorsExports = picocolors.exports;
const c = /*@__PURE__*/getDefaultExportFromCjs(picocolorsExports);

const DICT_FOLDER = dictDir;
const IGNORE_KEY = "@case-police-ignore";
const DISABLE_KEY = "@case-police-disable";
const IGNORE_REGEX = /@case-police-ignore\s+([^\s]+)/g;
const UTF8_RANGE = "[\x80-\uFFFF]";
function buildRegex(dictionary) {
  const keys = Object.keys(dictionary);
  const regex = new RegExp(`\\b(${keys.join("|").replace(/\+/g, "\\+")})\\b`, "gi");
  return regex;
}
function replaceCore(code, dict, ignore = [], output, regex) {
  regex = regex || buildRegex(dict);
  Array.from(code.matchAll(IGNORE_REGEX)).forEach((match) => {
    const [, key] = match;
    ignore.push(...key.split(",").map((k) => k.trim().toLowerCase()).filter(Boolean));
  });
  let changed = false;
  code = code.replace(regex, (_, from, index) => {
    if (containsUTF8(code, from, index))
      return _;
    if (!from.match(/[A-Z]/) || !from.match(/[a-z]/))
      return _;
    const lower = from.toLowerCase();
    if (ignore.includes(lower))
      return _;
    const to = dict[lower];
    if (!to || to === from)
      return _;
    changed = true;
    output?.(code, index, from, to);
    return to;
  });
  if (changed)
    return code;
}
async function replace(code, id, _dict, regex, _ignore = []) {
  if (code.includes(DISABLE_KEY))
    return;
  const dict = _dict || await loadAllPresets();
  const ignore = _ignore.slice();
  const output = (code2, offset, original, replaced) => {
    const lines = code2.slice(0, offset).split("\n");
    const line = lines.length;
    const col = (lines[line - 1].length || 0) + 1;
    console.log(`${c.yellow(original)} ${c.dim("\u2192")} ${c.green(replaced)} 	 ${c.dim(`./${id}:${line}:${col}`)}`);
  };
  return replaceCore(
    code,
    dict,
    ignore,
    output,
    regex
  );
}
async function resolvePreset(preset) {
  let result = {};
  const file = `${preset}.json`;
  const p = path.join(DICT_FOLDER, file);
  if (existsSync(p)) {
    const content = await promises.readFile(p, "utf-8");
    result = {
      ...result,
      ...JSON.parse(content)
    };
  } else {
    throw new Error(`Preset "${preset}" not found`);
  }
  return result;
}
async function loadAllPresets() {
  const files = await promises.readdir(DICT_FOLDER);
  return Object.assign(
    {},
    ...await Promise.all(files.map((file) => resolvePreset(file.split(".")[0])))
  );
}
function containsUTF8(code, key, index) {
  const utf8Regex = new RegExp(`${UTF8_RANGE}`);
  const head = code.charAt(index - 1);
  const tail = code.charAt(index + key.length);
  return utf8Regex.test(head) || utf8Regex.test(tail);
}
async function loadDictPresets(preset) {
  const presets = (preset || "").split(",").map((i) => i.trim()).filter(Boolean);
  let dictionary = {};
  if (presets.length) {
    Object.assign(
      dictionary,
      ...await Promise.all(presets.map(resolvePreset))
    );
  } else {
    dictionary = await loadAllPresets();
  }
  return dictionary;
}

export { DICT_FOLDER as D, IGNORE_KEY as I, UTF8_RANGE as U, DISABLE_KEY as a, IGNORE_REGEX as b, buildRegex as c, replace as d, resolvePreset as e, loadDictPresets as f, commonjsGlobal as g, getDefaultExportFromCjs as h, c as i, loadAllPresets as l, replaceCore as r };
