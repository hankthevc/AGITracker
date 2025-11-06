import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { SentryInitializer } from '@/components/SentryInitializer'
import { Navigation } from '@/components/Navigation'
import { KeyboardShortcutsProvider } from '@/components/KeyboardShortcutsProvider'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { SafeLink } from '@/lib/SafeLink'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AGI Signpost Tracker',
  description: 'Evidence-first dashboard tracking proximity to AGI via measurable signposts',
  openGraph: {
    title: 'AGI Signpost Tracker',
    description: 'Evidence-first dashboard tracking proximity to AGI via measurable signposts',
    type: 'website',
    images: [
      {
        url: '/api/og?title=AGI%20Signpost%20Tracker&description=Evidence-first%20dashboard%20tracking%20proximity%20to%20AGI',
        width: 1200,
        height: 630,
        alt: 'AGI Signpost Tracker',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AGI Signpost Tracker',
    description: 'Evidence-first dashboard tracking proximity to AGI via measurable signposts',
    images: ['/api/og?title=AGI%20Signpost%20Tracker&description=Evidence-first%20dashboard%20tracking%20proximity%20to%20AGI'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SentryInitializer />
        <ErrorBoundary>
          <KeyboardShortcutsProvider>
            <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
              <Navigation />
              <main className="container mx-auto px-4 py-8">
                {children}
              </main>
          <footer className="border-t bg-white/50 mt-16">
            <div className="container mx-auto px-4 py-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
                <div>
                  <h3 className="font-semibold text-sm mb-3">About</h3>
                  <p className="text-sm text-muted-foreground">
                    Evidence-first dashboard tracking proximity to AGI via measurable signposts.
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    © 2025 AGI Signpost Tracker
                  </p>
                </div>
                
                <div>
                  <h3 className="font-semibold text-sm mb-3">Resources</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>
                      <Link href="/methodology" className="hover:text-primary transition-colors">
                        Methodology
                      </Link>
                    </li>
                    <li>
                      <SafeLink href={`${process.env.NEXT_PUBLIC_API_URL}/docs`} className="hover:text-primary transition-colors">
                        API Docs
                      </SafeLink>
                    </li>
                    <li>
                      <SafeLink href="https://github.com/hankthevc/AGITracker" className="hover:text-primary transition-colors">
                        GitHub
                      </SafeLink>
                    </li>
                    <li>
                      <Link href="/changelog" className="hover:text-primary transition-colors">
                        Changelog
                      </Link>
                    </li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-semibold text-sm mb-3">Legal</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>
                      <Link href="/legal/privacy" className="hover:text-primary transition-colors">
                        Privacy Policy
                      </Link>
                    </li>
                    <li>
                      <Link href="/legal/terms" className="hover:text-primary transition-colors">
                        Terms of Service
                      </Link>
                    </li>
                    <li>
                      <SafeLink href="https://creativecommons.org/licenses/by/4.0/" className="hover:text-primary transition-colors">
                        CC BY 4.0 License
                      </SafeLink>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="pt-6 border-t text-center text-sm text-muted-foreground">
                <p>
                  All data available via{' '}
                  <a href="/v1/feed.json" className="text-primary hover:underline">
                    JSON feeds
                  </a>
                  {' • '}
                  Licensed under{' '}
                  <SafeLink href="https://creativecommons.org/licenses/by/4.0/" className="text-primary hover:underline">
                    CC BY 4.0
                  </SafeLink>
                </p>
                <p className="mt-2 text-xs text-muted-foreground/70">
                  ✨ Sprint 10: UX & Data Quality - URL validation active
                </p>
              </div>
            </div>
          </footer>
        </div>
          </KeyboardShortcutsProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}

