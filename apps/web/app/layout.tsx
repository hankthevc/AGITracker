import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AGI Signpost Tracker',
  description: 'Evidence-first dashboard tracking proximity to AGI via measurable signposts',
  openGraph: {
    title: 'AGI Signpost Tracker',
    description: 'Evidence-first dashboard tracking proximity to AGI via measurable signposts',
    type: 'website',
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
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
          <nav className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <Link href="/" className="text-2xl font-bold text-primary">
                  AGI Signpost Tracker
                </Link>
                <div className="flex gap-6">
                  <Link href="/" className="text-sm font-medium hover:text-primary transition-colors">
                    Home
                  </Link>
                  <Link href="/benchmarks" className="text-sm font-medium hover:text-primary transition-colors">
                    Benchmarks
                  </Link>
                  <Link href="/compute" className="text-sm font-medium hover:text-primary transition-colors">
                    Compute
                  </Link>
                  <Link href="/security" className="text-sm font-medium hover:text-primary transition-colors">
                    Security
                  </Link>
                  <Link href="/changelog" className="text-sm font-medium hover:text-primary transition-colors">
                    Changelog
                  </Link>
                  <Link href="/methodology" className="text-sm font-medium hover:text-primary transition-colors">
                    Methodology
                  </Link>
                </div>
              </div>
            </div>
          </nav>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
          <footer className="border-t bg-white/50 mt-16">
            <div className="container mx-auto px-4 py-8">
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div>
                  <p>© 2025 AGI Signpost Tracker</p>
                  <p className="mt-1">
                    Public JSON feed:{' '}
                    <a href="/v1/feed.json" className="text-primary hover:underline">
                      CC BY 4.0
                    </a>
                  </p>
                </div>
                <div className="text-right">
                  <p>Evidence-first, neutral, and open</p>
                  <p className="mt-1">
                    <Link href="/methodology" className="text-primary hover:underline">
                      Read our methodology
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}

