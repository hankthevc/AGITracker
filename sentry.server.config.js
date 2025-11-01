// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: 'https://4da7aeb6938e51d9ca13ad25ba3f4dda@o4510274025422848.ingest.us.sentry.io/4510274033811456',

  // Sample 1% of traces to reduce cost and noise
  tracesSampleRate: 0.01,

  // Enable logs to be sent to Sentry
  enableLogs: true,

  // SECURITY: Disable PII to prevent GDPR/compliance issues
  sendDefaultPii: false,

  // Scrub sensitive data before sending
  beforeSend(event, hint) {
    // Remove sensitive headers
    if (event.request?.headers) {
      delete event.request.headers['authorization']
      delete event.request.headers['x-api-key']
      delete event.request.headers['cookie']
    }
    // Remove sensitive cookies
    if (event.request?.cookies) {
      delete event.request.cookies
    }
    return event
  },

  environment: process.env.NODE_ENV || 'production',
})
