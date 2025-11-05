module.exports = {
  extends: ['next/core-web-vitals'],
  rules: {
    // SECURITY: Prevent raw <a> tags with external URLs
    // All external links must use SafeLink component for XSS prevention
    'no-restricted-syntax': [
      'error',
      {
        selector: 'JSXOpeningElement[name.name="a"][attributes] JSXAttribute[name.name="href"] JSXExpressionContainer',
        message: 'Do not use raw <a> tags with dynamic href. Use SafeLink component from @/lib/SafeLink for external URLs to prevent javascript: and data: XSS attacks. Internal routes should use Next.js <Link>.',
      },
    ],
  },
  overrides: [
    {
      // Allow raw <a> for static hrefs (hardcoded strings)
      files: ['*.tsx', '*.ts'],
      rules: {
        'no-restricted-syntax': [
          'error',
          {
            selector: 'JSXOpeningElement[name.name="a"][attributes] JSXAttribute[name.name="href"] JSXExpressionContainer',
            message: 'Use SafeLink for dynamic external URLs. For static URLs, this is acceptable but verify the URL is safe.',
          },
        ],
      },
    },
  ],
}

