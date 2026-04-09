module.exports = {
  extends: ['stylelint-config-standard', 'stylelint-config-recess-order'],
  customSyntax: 'postcss-html',
  ignoreFiles: ['dist/**', 'node_modules/**'],
  rules: {
    'selector-class-pattern': null,
    'declaration-empty-line-before': null,
    'at-rule-no-unknown': [true, { ignoreAtRules: ['tailwind', 'layer', 'apply', 'variants', 'responsive', 'screen'] }],
  },
}
