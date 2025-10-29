'use client'

import { useState, useEffect } from 'react'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { Menu, X } from 'lucide-react'
import { SentryInitializer } from '@/components/SentryInitializer'
import { SearchBar } from '@/components/SearchBar'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  // Sprint 10.5: Keyboard shortcuts
  useKeyboardShortcuts()

  return (
    <html lang="en">
      <head>
        <title>AGI Signpost Tracker</title>
        <meta name="description" content="Evidence-first dashboard tracking proximity to AGI via measurable signposts" />
      </head>
      <body className={inter.className}>
        <SentryInitializer />
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
          {/* Sprint 10.4: Mobile-responsive navigation */}
          <nav className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between gap-4">
                <Link href="/" className="text-2xl font-bold text-primary whitespace-nowrap">
                  AGI Signpost Tracker
                </Link>
                
                {/* Desktop Search Bar */}
                <div className="hidden md:block flex-1 max-w-md mx-4">
                  <SearchBar />
                </div>

                {/* Desktop Navigation */}
                <div className="hidden lg:flex gap-4 flex-wrap">
                  <Link href="/" className="text-sm font-medium hover:text-primary transition-colors">
                    Home
                  </Link>
                  <Link href="/insights" className="text-sm font-medium hover:text-primary transition-colors">
                    🔍 Insights
                  </Link>
                  <Link href="/news" className="text-sm font-medium hover:text-primary transition-colors">
                    News
                  </Link>
                  <Link href="/events" className="text-sm font-medium hover:text-primary transition-colors">
                    Events
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
                  <Link href="/admin/review" className="text-sm font-medium hover:text-primary transition-colors">
                    Admin
                  </Link>
                </div>

                {/* Mobile menu button */}
                <button
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="lg:hidden p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                  aria-label="Toggle menu"
                >
                  {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
              </div>

              {/* Mobile menu */}
              {mobileMenuOpen && (
                <div className="lg:hidden mt-4 pb-4 space-y-2">
                  {/* Mobile Search */}
                  <div className="mb-4">
                    <SearchBar />
                  </div>
                  
                  <Link
                    href="/"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Home
                  </Link>
                  <Link
                    href="/insights"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    🔍 Insights
                  </Link>
                  <Link
                    href="/news"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    News
                  </Link>
                  <Link
                    href="/events"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Events
                  </Link>
                  <Link
                    href="/benchmarks"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Benchmarks
                  </Link>
                  <Link
                    href="/compute"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Compute
                  </Link>
                  <Link
                    href="/security"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Security
                  </Link>
                  <Link
                    href="/changelog"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Changelog
                  </Link>
                  <Link
                    href="/methodology"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Methodology
                  </Link>
                  <Link
                    href="/admin/review"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-2 text-sm font-medium hover:text-primary transition-colors"
                  >
                    Admin
                  </Link>
                </div>
              )}
            </div>
          </nav>
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
                      <a href={`${process.env.NEXT_PUBLIC_API_URL}/docs`} className="hover:text-primary transition-colors" target="_blank" rel="noopener">
                        API Docs
                      </a>
                    </li>
                    <li>
                      <a href="https://github.com/hankthevc/AGITracker" className="hover:text-primary transition-colors" target="_blank" rel="noopener">
                        GitHub
                      </a>
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
                      <a href="https://creativecommons.org/licenses/by/4.0/" className="hover:text-primary transition-colors" target="_blank" rel="noopener">
                        CC BY 4.0 License
                      </a>
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
                  <a href="https://creativecommons.org/licenses/by/4.0/" className="text-primary hover:underline" target="_blank" rel="noopener">
                    CC BY 4.0
                  </a>
                </p>
                <p className="mt-2 text-xs text-muted-foreground/70">
                  ✨ Sprint 10: UX & Data Quality - URL validation active
                </p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}

