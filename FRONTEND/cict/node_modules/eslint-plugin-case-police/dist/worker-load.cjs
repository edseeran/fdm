'use strict';

const synckit = require('synckit');
const casePolice = require('case-police');

synckit.runAsWorker(async (options) => {
  const defaults = options.noDefault ? {} : await casePolice.loadDictPresets(options.presets?.join(",") || "");
  return {
    ...defaults,
    ...options.dict
  };
});
