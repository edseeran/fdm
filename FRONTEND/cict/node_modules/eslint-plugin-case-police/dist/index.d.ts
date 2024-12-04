import * as _typescript_eslint_utils_dist_ts_eslint_Rule from '@typescript-eslint/utils/dist/ts-eslint/Rule';
import { Presets } from 'case-police';

interface RuleOption {
    dict?: Record<string, string>;
    noDefault?: boolean;
    presets?: Presets[];
    ignore?: string[];
}

declare const _default: {
    rules: {
        'string-check': _typescript_eslint_utils_dist_ts_eslint_Rule.RuleModule<"CasePoliceError", [RuleOption], _typescript_eslint_utils_dist_ts_eslint_Rule.RuleListener>;
    };
    configs: {
        recommended: {
            plugins: string[];
            rules: {
                'case-police/string-check': string;
            };
        };
    };
};

export { _default as default };
