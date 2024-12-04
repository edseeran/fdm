import { join } from 'node:path';
import { createSyncFn } from 'synckit';
import { replaceCore } from 'case-police';
import { ESLintUtils } from '@typescript-eslint/utils';
import { distDir } from './dirs.mjs';
import 'node:url';

const recommended = {
  plugins: ["case-police"],
  rules: {
    "case-police/string-check": "warn"
  }
};

const createEslintRule = ESLintUtils.RuleCreator(
  (ruleName) => ruleName
);

const RULE_NAME = "string-check";
const loadDict = createSyncFn(join(distDir, "worker-load.cjs"));
const stringCheck = createEslintRule({
  name: RULE_NAME,
  meta: {
    type: "suggestion",
    docs: {
      description: "make the case correct in string",
      recommended: "warn"
    },
    fixable: "code",
    schema: [
      {
        type: "object",
        additionalProperties: false,
        properties: {
          dict: {
            description: "Custom dictionary, will be merged with original dict.",
            type: "object"
          },
          noDefault: {
            description: "Disable the default dictionary.",
            type: "boolean"
          },
          presets: {
            description: "Filter the default presets.",
            type: "array"
          },
          ignore: {
            description: "Ignore some words.",
            type: "array"
          }
        }
      }
    ],
    messages: {
      CasePoliceError: "'{{ from }}' should be '{{ to }}'."
    }
  },
  defaultOptions: [
    {
      noDefault: false,
      dict: {},
      presets: [],
      ignore: []
    }
  ],
  create: (context, [options]) => {
    const dict = loadDict(options);
    const code = context.getSourceCode().text;
    const checkText = (node) => {
      const start = node.range[0];
      const end = node.range[1];
      const originalStr = code.slice(start, end);
      const outputs = [];
      replaceCore(originalStr, dict, options.ignore, (_, index, from, to) => {
        outputs.push({ index, from, to });
      });
      for (const { from, to, index } of outputs) {
        const loc = {
          ...node.loc.start
        };
        for (let i = 0; i < index; i++) {
          if (originalStr[i] === "\n") {
            loc.line++;
            loc.column = 0;
          } else {
            loc.column++;
          }
        }
        context.report({
          messageId: "CasePoliceError",
          data: { from, to },
          node,
          *fix(fixer) {
            yield fixer.replaceTextRange([start + index, start + index + from.length], to);
          },
          loc: {
            start: loc,
            end: {
              line: loc.line,
              column: loc.column + from.length
            }
          }
        });
      }
    };
    const scriptVisitor = {
      Literal: (node) => {
        if (typeof node.value === "string")
          checkText(node);
      },
      JSXText: (node) => {
        checkText(node);
      },
      TemplateElement: (node) => {
        checkText(node);
      }
    };
    const templateBodyVisitor = {
      VText(node) {
        checkText(node);
      }
    };
    if (context.parserServices == null || context.parserServices?.defineTemplateBodyVisitor == null)
      return scriptVisitor;
    else
      return context.parserServices?.defineTemplateBodyVisitor(templateBodyVisitor, scriptVisitor);
  }
});

const index = {
  rules: {
    "string-check": stringCheck
  },
  configs: {
    recommended
  }
};

export { index as default };
