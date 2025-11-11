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
        selector: 'JSXOpeningElement[name.name="a"] JSXAttribute[name.name="href"][value.type="Literal"][value.value=/^https?:/]',
        message: 'Use <SafeLink> component for external URLs instead of raw <a> tags. Import from @/lib/SafeLink'
      },
      {
        selector: 'JSXOpeningElement[name.name="a"] JSXAttribute[name.name="href"][value.type="JSXExpressionContainer"]',
        message: 'Use <SafeLink> component for dynamic external URLs. Import from @/lib/SafeLink'
      }
    ],
  },
}

