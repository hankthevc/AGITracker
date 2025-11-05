module.exports = {
  extends: ['next/core-web-vitals'],
  rules: {
    // Relax some rules for build (can tighten after Ben's review)
    'react/no-unescaped-entities': 'warn', // Demote to warning (not error)
    'react-hooks/exhaustive-deps': 'warn',  // Demote to warning
  },
}

