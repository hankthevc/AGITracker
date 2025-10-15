'use client'

import { use } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import Link from 'next/link'
import useSWR from 'swr'

interface EventDetail {
  id: number
  title: string
  summary?: string
  date: string
  tier: string
  source_url?: string
  source_type?: string
  needs_review: boolean
  confidence_score?: number
  created_at: string
  signpost_links?: Array<{
    signpost_code: string
    signpost_title: string
    confidence_score?: number
  }>
  entities?: Array<{
    entity_type: string
    entity_value: string
  }>
  forecast_comparison?: Array<{
    roadmap: string
    signpost_code: string
    prediction_date?: string
    prediction_value?: number
    event_date: string
    event_value?: number
    status: 'ahead_of_schedule' | 'on_track' | 'behind_schedule'
  }>
}

const TIER_BADGES = {
  A: { label: 'Tier A', class: 'bg-green-100 text-green-800 border-green-300', desc: 'Peer-reviewed / Leaderboard' },
  B: { label: 'Tier B', class: 'bg-blue-100 text-blue-800 border-blue-300', desc: 'Official lab blog' },
  C: { label: 'Tier C', class: 'bg-yellow-100 text-yellow-800 border-yellow-300', desc: 'Reputable press' },
  D: { label: 'Tier D', class: 'bg-gray-100 text-gray-800 border-gray-300', desc: 'Social media' },
}

const STATUS_BADGES = {
  ahead_of_schedule: { label: 'Ahead of Schedule', class: 'bg-green-100 text-green-800 border-green-300' },
  on_track: { label: 'On Track', class: 'bg-blue-100 text-blue-800 border-blue-300' },
  behind_schedule: { label: 'Behind Schedule', class: 'bg-red-100 text-red-800 border-red-300' },
}

export default function EventDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  const eventId = Number(resolvedParams.id)

  const { data: event, error, isLoading } = useSWR<EventDetail>(
    `/v1/events/${eventId}`,
    () => apiClient.getEvent(eventId)
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading event details...</p>
        </div>
      </div>
    )
  }

  if (error || !event) {
    return (
      <div className="space-y-4">
        <Link href="/events" className="text-primary hover:underline text-sm">
          ← Back to Events
        </Link>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Event not found or failed to load.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const tierInfo = TIER_BADGES[event.tier as keyof typeof TIER_BADGES] || TIER_BADGES.D

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link href="/events" className="text-primary hover:underline text-sm">
        ← Back to Events
      </Link>

      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <span className={`inline-block px-3 py-1 text-sm font-medium rounded border ${tierInfo.class}`}>
            {tierInfo.label}
          </span>
          <span className="text-sm text-muted-foreground">{formatDate(event.date)}</span>
          {event.needs_review && (
            <span className="inline-block px-3 py-1 text-sm font-medium rounded border bg-orange-100 text-orange-800 border-orange-300">
              Pending Review
            </span>
          )}
        </div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">{event.title}</h1>
        {event.summary && (
          <p className="text-lg text-muted-foreground">{event.summary}</p>
        )}
      </div>

      {/* Source */}
      {event.source_url && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Source</CardTitle>
          </CardHeader>
          <CardContent>
            <a
              href={event.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline break-all"
            >
              {event.source_url} ↗
            </a>
            {event.source_type && (
              <p className="text-sm text-muted-foreground mt-1">
                Source type: <span className="font-medium">{event.source_type}</span>
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Signpost mappings */}
      {event.signpost_links && event.signpost_links.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Mapped Signposts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {event.signpost_links.map((link) => (
                <div key={link.signpost_code} className="border rounded-lg p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <Link
                        href={`/signposts/${link.signpost_code}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {link.signpost_code}
                      </Link>
                      <p className="text-sm text-muted-foreground mt-1">{link.signpost_title}</p>
                    </div>
                    {link.confidence_score !== undefined && (
                      <span className="text-xs text-muted-foreground">
                        Confidence: {(link.confidence_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Forecast comparison */}
      {event.forecast_comparison && event.forecast_comparison.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Forecast Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {event.forecast_comparison.map((comparison, idx) => {
                const statusInfo = STATUS_BADGES[comparison.status]
                return (
                  <div key={idx} className="border rounded-lg p-3">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <p className="font-medium">{comparison.roadmap}</p>
                        <p className="text-sm text-muted-foreground">{comparison.signpost_code}</p>
                      </div>
                      <span className={`inline-block px-2 py-1 text-xs font-medium rounded border ${statusInfo.class}`}>
                        {statusInfo.label}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Predicted</p>
                        <p className="font-medium">
                          {comparison.prediction_date ? formatDate(comparison.prediction_date) : 'N/A'}
                          {comparison.prediction_value !== undefined && (
                            <span className="text-muted-foreground ml-2">
                              ({comparison.prediction_value})
                            </span>
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Actual</p>
                        <p className="font-medium">
                          {formatDate(comparison.event_date)}
                          {comparison.event_value !== undefined && (
                            <span className="text-muted-foreground ml-2">
                              ({comparison.event_value})
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Entities */}
      {event.entities && event.entities.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Extracted Entities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {event.entities.map((entity, idx) => (
                <span
                  key={idx}
                  className="inline-block px-2 py-1 text-sm bg-slate-100 text-slate-700 rounded"
                >
                  <span className="text-muted-foreground text-xs">{entity.entity_type}:</span>{' '}
                  {entity.entity_value}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Event Date</p>
              <p className="font-medium">{formatDate(event.date)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Added to Tracker</p>
              <p className="font-medium">{formatDate(event.created_at)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Evidence Tier</p>
              <p className="font-medium">{tierInfo.label} - {tierInfo.desc}</p>
            </div>
            {event.confidence_score !== undefined && (
              <div>
                <p className="text-muted-foreground">Mapping Confidence</p>
                <p className="font-medium">{(event.confidence_score * 100).toFixed(0)}%</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Explanation */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6 text-sm">
          <p>
            <strong>How this works:</strong> Events are automatically ingested from various sources and mapped
            to relevant signposts using keyword matching and confidence scoring. High-confidence matches
            (≥60%) are approved automatically. Only Tier A and B events move the main gauges.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

