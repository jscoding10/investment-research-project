// prettier.config.js   (or prettier.config.cjs)
module.exports = {
  tabWidth: 2,
  useTabs: false,
  printWidth: 120,
  semi: true,
  singleQuote: true,
  quoteProps: 'consistent',
  trailingComma: 'all',
  bracketSpacing: true,
  bracketSameLine: true,
  arrowParens: 'always',
  singleAttributePerLine: true,
  plugins: ['prettier-plugin-tailwindcss'], // optional but recommended
  overrides: [
    {
      files: '*.html',
      options: { parser: 'angular' },
    },
  ],
};