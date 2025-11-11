module.exports = {
  extends: ['next/core-web-vitals'],
  rules: {
    // Relax some rules for build (can tighten after Ben's review)
    'react/no-unescaped-entities': 'warn', // Demote to warning (not error)
    'react-hooks/exhaustive-deps': 'warn',  // Demote to warning
    
    // SECURITY: Enforce SafeLink for external URLs (prevents XSS)
    // BLOCKING: This rule is set to 'error' to prevent new unsafe anchors from being committed
    // All external links must use SafeLink component
    'no-restricted-syntax': [
      'error',
      {
        // Match: <a href="http..." /> or <a href="https..." />
        selector: 'JSXElement > JSXOpeningElement[name.name="a"] JSXAttribute[name.name="href"][value.value=/^https?:/]',
        message: 'Use <SafeLink href="..."> for external links instead of <a> with an external URL. Import from @/lib/SafeLink'
      },
      {
        // Match: <a href={someVar} /> or <a href={`http...`} />
        selector: 'JSXElement > JSXOpeningElement[name.name="a"] JSXAttribute[name.name="href"][value.expression]',
        message: 'Use <SafeLink> for potentially-external href expressions (href={...}). Import from @/lib/SafeLink'
      }
    ],
  },
}

