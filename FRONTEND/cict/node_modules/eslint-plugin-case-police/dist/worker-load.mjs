import { runAsWorker } from 'synckit';
import { loadDictPresets } from 'case-police';

runAsWorker(async (options) => {
  const defaults = options.noDefault ? {} : await loadDictPresets(options.presets?.join(",") || "");
  return {
    ...defaults,
    ...options.dict
  };
});
