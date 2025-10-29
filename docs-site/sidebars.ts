import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  gettingStartedSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/configuration',
        'getting-started/first-steps',
      ],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/overview',
        'architecture/frontend',
        'architecture/backend',
        'architecture/database',
      ],
    },
  ],

  guidesSidebar: [
    {
      type: 'category',
      label: 'User Guides',
      items: [
        'guides/events-feed',
        'guides/timeline-visualization',
        'guides/signpost-deep-dives',
        'guides/custom-presets',
        'guides/rag-chatbot',
        'guides/scenario-explorer',
        'guides/admin-panel',
        'guides/api-usage',
      ],
    },
  ],

  apiSidebar: [
    'api/overview',
    'api/authentication',
    'api/endpoints',
    'api/examples',
    'api/quick-reference',
  ],

  contributingSidebar: [
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/code-standards',
        'contributing/pull-requests',
        'contributing/testing',
      ],
    },
    {
      type: 'category',
      label: 'Deployment',
      items: [
        'deployment/vercel',
        'deployment/railway',
        'deployment/production',
      ],
    },
  ],
};

export default sidebars;
