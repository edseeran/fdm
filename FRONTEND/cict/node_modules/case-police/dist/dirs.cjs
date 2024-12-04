'use strict';

const node_url = require('node:url');
const path = require('node:path');

const distDir = node_url.fileURLToPath(new URL("../dist", (typeof document === 'undefined' ? require('u' + 'rl').pathToFileURL(__filename).href : (document.currentScript && document.currentScript.src || new URL('dirs.cjs', document.baseURI).href))));
const dictDir = path.resolve(distDir, "../dict");

exports.dictDir = dictDir;
exports.distDir = distDir;
