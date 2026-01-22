module.exports = {
  root: true,
  extends: [
    'expo',
    'prettier',
  ],
  plugins: ['prettier'],
  rules: {
    'prettier/prettier': 'warn',
    'no-console': 'warn',
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
  },
  env: {
    node: true,
    es6: true,
  },
};
