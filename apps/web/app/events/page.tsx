'use client'

import { Suspense, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import Link from 'next/link'
import useSWR from 'swr'

interface Event {
  id: number
  title: string
  summary?: string
  date: string
  tier: string
  source_url?: string
  needs_review: boolean
  signpost_links?: Array<{
    signpost_code: string
    signpost_title: string
  }>
}

const TIER_BADGES = {
  A: { label: 'Tier A', class: 'bg-green-100 text-green-800 border-green-300', desc: 'Peer-reviewed / Leaderboard' },
  B: { label: 'Tier B', class: 'bg-blue-100 text-blue-800 border-blue-300', desc: 'Official lab blog' },
  C: { label: 'Tier C', class: 'bg-yellow-100 text-yellow-800 border-yellow-300', desc: 'Reputable press' },
  D: { label: 'Tier D', class: 'bg-gray-100 text-gray-800 border-gray-300', desc: 'Social media' },
}

function EventsContent() {
  const searchParams = useSearchParams()
  const tierFilter = searchParams.get('tier')
  const signpostFilter = searchParams.get('signpost_id')
  
  const [selectedTier, setSelectedTier] = useState<string | null>(tierFilter)
  const [page, setPage] = useState(0)
  const limit = 20

  const { data, error, isLoading } = useSWR(
    `/v1/events?tier=${selectedTier || ''}&skip=${page * limit}&limit=${limit}`,
    () => apiClient.getEvents({
      tier: selectedTier || undefined,
      signpost_id: signpostFilter ? Number(signpostFilter) : undefined,
      skip: page * limit,
      limit,
    })
  )

  const events: Event[] = data?.items || []
  const total = data?.total || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Events Feed</h1>
        <p className="text-muted-foreground">
          Real-world developments mapped to AGI signposts, categorized by evidence tier.
        </p>
        <div className="mt-4 flex items-center gap-4">
          <span className="text-sm font-medium">Feeds:</span>
          <a
            href="/v1/events/feed.json"
            className="text-sm text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            JSON Feed (Public) ↗
          </a>
          <a
            href="/v1/events/feed.json?include_research=true"
            className="text-sm text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            JSON Feed (Research) ↗
          </a>
        </div>
      </div>

      {/* Tier filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filter by Evidence Tier</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedTier(null)}
              className={`px-3 py-1.5 text-sm rounded border transition-colors ${
                !selectedTier
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white hover:bg-slate-50 border-slate-300'
              }`}
            >
              All Events
            </button>
            {Object.entries(TIER_BADGES).map(([tier, info]) => (
              <button
                key={tier}
                onClick={() => setSelectedTier(tier)}
                className={`px-3 py-1.5 text-sm rounded border transition-colors ${
                  selectedTier === tier
                    ? info.class
                    : 'bg-white hover:bg-slate-50 border-slate-300'
                }`}
              >
                {info.label} - {info.desc}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="text-sm space-y-2">
            <p>
              <strong>Evidence Tiers:</strong> Only Tier A (peer-reviewed, leaderboards) and Tier B (official lab blogs) events
              move the main gauges. Tier C (press) and Tier D (social) are tracked but don't affect scores.
            </p>
            <p>
              <strong>Gauge Movement:</strong> Events are automatically mapped to signposts using keyword matching and confidence scoring.
              High-confidence matches (≥0.6) are approved automatically; lower-confidence matches require manual review.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Events list */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading events...</p>
        </div>
      )}

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Failed to load events. Please try again later.</p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && events.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No events found{selectedTier ? ` for tier ${selectedTier}` : ''}.
            </p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && events.length > 0 && (
        <div className="space-y-4">
          {events.map((event) => {
            const tierInfo = TIER_BADGES[event.tier as keyof typeof TIER_BADGES] || TIER_BADGES.D
            return (
              <Card key={event.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className={`inline-block px-2 py-0.5 text-xs font-medium rounded border ${tierInfo.class}`}
                        >
                          {tierInfo.label}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {formatDate(event.date)}
                        </span>
                        {event.needs_review && (
                          <span className="inline-block px-2 py-0.5 text-xs font-medium rounded border bg-orange-100 text-orange-800 border-orange-300">
                            Pending Review
                          </span>
                        )}
                      </div>
                      <Link
                        href={`/events/${event.id}`}
                        className="text-lg font-semibold hover:text-primary transition-colors block mb-2"
                      >
                        {event.title}
                      </Link>
                      {event.summary && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {event.summary}
                        </p>
                      )}
                      {event.signpost_links && event.signpost_links.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          <span className="text-xs text-muted-foreground">Mapped to:</span>
                          {event.signpost_links.map((link) => (
                            <Link
                              key={link.signpost_code}
                              href={`/signposts/${link.signpost_code}`}
                              className="inline-block px-2 py-1 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition-colors"
                            >
                              {link.signpost_code}: {link.signpost_title}
                            </Link>
                          ))}
                        </div>
                      )}
                    </div>
                    {event.source_url && (
                      <a
                        href={event.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary hover:underline flex-shrink-0"
                      >
                        Source ↗
                      </a>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Pagination */}
      {total > limit && (
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-4 py-2 text-sm border rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-muted-foreground">
            Page {page + 1} of {Math.ceil(total / limit)}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={(page + 1) * limit >= total}
            className="px-4 py-2 text-sm border rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default function EventsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <EventsContent />
    </Suspense>
  )
}

