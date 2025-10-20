'use client'

import { useState, useEffect } from 'react'
import { EventCard } from '@/components/events/EventCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getApiBaseUrl } from '@/lib/apiBase'
import { Event, EventsResponse } from '@/lib/types'

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTier, setSelectedTier] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [skip, setSkip] = useState(0)
  const [total, setTotal] = useState(0)
  const limit = 50
  
  useEffect(() => {
    fetchEvents()
  }, [selectedTier, startDate, endDate, skip])
  
  const fetchEvents = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = getApiBaseUrl()
      const params = new URLSearchParams()
      
      if (selectedTier) params.append('tier', selectedTier)
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      params.append('skip', skip.toString())
      params.append('limit', limit.toString())
      
      const url = `${apiUrl}/v1/events?${params.toString()}`
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch events: ${response.statusText}`)
      }
      
      const data: EventsResponse = await response.json()
      setEvents(data.results || data.items || [])
      setTotal(data.total || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load events')
    } finally {
      setLoading(false)
    }
  }
  
  const handleSearch = () => {
    setSkip(0)
    fetchEvents()
  }
  
  const handleExportJSON = () => {
    const dataStr = JSON.stringify(events, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `events_${new Date().toISOString().split('T')[0]}.json`
    link.click()
  }
  
  const handleExportCSV = () => {
    const headers = ['ID', 'Title', 'Publisher', 'Published', 'Tier', 'URL']
    const rows = events.map(e => [
      e.id,
      `"${e.title.replace(/"/g, '""')}"`,
      e.publisher || '',
      e.published_at || e.date || '',
      e.evidence_tier,
      e.source_url,
    ])
    
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const dataBlob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `events_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
  }
  
  const tierColors = {
    A: 'bg-green-600 text-white hover:bg-green-700',
    B: 'bg-blue-600 text-white hover:bg-blue-700',
    C: 'bg-yellow-600 text-white hover:bg-yellow-700',
    D: 'bg-red-600 text-white hover:bg-red-700',
  }
  
  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">Events Feed</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Browse AI progress events across all evidence tiers
        </p>
      </div>
      
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter events by tier, date range, or search</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Tier Filter */}
          <div>
            <div className="text-sm font-medium mb-2">Evidence Tier</div>
            <div className="flex gap-2">
              <Badge
                variant={selectedTier === null ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setSelectedTier(null)}
              >
                All
              </Badge>
              {(['A', 'B', 'C', 'D'] as const).map((tier) => (
                <Badge
                  key={tier}
                  variant={selectedTier === tier ? 'default' : 'outline'}
                  className={`cursor-pointer ${selectedTier === tier ? tierColors[tier] : ''}`}
                  onClick={() => setSelectedTier(tier)}
                  data-testid={`tier-filter-${tier}`}
                >
                  {tier}
                </Badge>
              ))}
            </div>
          </div>
          
          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="start-date" className="text-sm font-medium block mb-2">
                Start Date
              </label>
              <input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
            <div>
              <label htmlFor="end-date" className="text-sm font-medium block mb-2">
                End Date
              </label>
              <input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
          </div>
          
          {/* Export Buttons */}
          <div className="flex gap-2 pt-4 border-t">
            <button
              onClick={handleExportJSON}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 text-sm"
              disabled={events.length === 0}
            >
              Export JSON
            </button>
            <button
              onClick={handleExportCSV}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 text-sm"
              disabled={events.length === 0}
            >
              Export CSV
            </button>
          </div>
        </CardContent>
      </Card>
      
      {/* Results */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading events...</p>
        </div>
      )}
      
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}
      
      {!loading && !error && events.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            No events found matching your filters.
          </CardContent>
        </Card>
      )}
      
      {!loading && !error && events.length > 0 && (
        <>
          <div className="text-sm text-muted-foreground">
            Showing {skip + 1}–{Math.min(skip + limit, total)} of {total} events
          </div>
          
          <div className="grid grid-cols-1 gap-6">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
          
          {/* Pagination */}
          <div className="flex justify-center gap-4 pt-6">
            <button
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setSkip(skip + limit)}
              disabled={skip + limit >= total}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
