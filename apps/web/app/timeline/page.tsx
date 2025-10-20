'use client'

import { useState, useEffect } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { EventCard } from '@/components/events/EventCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getApiBaseUrl } from '@/lib/apiBase'
import { Event, EventsResponse } from '@/lib/types'

interface TimelineDataPoint {
  x: number  // Unix timestamp
  y: number  // Significance score (0-1)
  event: Event
  color: string
}

export default function TimelinePage() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [selectedTier, setSelectedTier] = useState<string | null>(null)
  
  useEffect(() => {
    fetchEvents()
  }, [selectedTier])
  
  const fetchEvents = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = getApiBaseUrl()
      const params = new URLSearchParams()
      
      if (selectedTier) params.append('tier', selectedTier)
      params.append('limit', '100')  // Get more for timeline view
      
      const url = `${apiUrl}/v1/events?${params.toString()}`
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch events: ${response.statusText}`)
      }
      
      const data: EventsResponse = await response.json()
      setEvents(data.results || data.items || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load events')
    } finally {
      setLoading(false)
    }
  }
  
  const tierColors = {
    A: '#16a34a',  // green-600
    B: '#2563eb',  // blue-600
    C: '#ca8a04',  // yellow-600
    D: '#dc2626',  // red-600
  }
  
  // Convert events to timeline data points
  const timelineData: TimelineDataPoint[] = events
    .filter(e => e.published_at || e.date)
    .map(event => {
      const dateStr = event.published_at || event.date || ''
      const timestamp = new Date(dateStr).getTime()
      
      // Use a default significance score (can be enhanced with actual analysis data)
      const significance = event.evidence_tier === 'A' ? 0.8 :
                          event.evidence_tier === 'B' ? 0.6 :
                          event.evidence_tier === 'C' ? 0.4 : 0.2
      
      return {
        x: timestamp,
        y: significance,
        event,
        color: tierColors[event.evidence_tier],
      }
    })
    .sort((a, b) => a.x - b.x)
  
  const formatXAxis = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }
  
  const formatYAxis = (value: number) => {
    return `${(value * 100).toFixed(0)}%`
  }
  
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data: TimelineDataPoint = payload[0].payload
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg max-w-xs">
          <p className="font-medium text-sm">{data.event.title}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {new Date(data.x).toLocaleDateString()}
          </p>
          <Badge className="mt-2" style={{ backgroundColor: data.color }}>
            {data.event.evidence_tier}-tier
          </Badge>
        </div>
      )
    }
    return null
  }
  
  const handleDotClick = (data: TimelineDataPoint) => {
    setSelectedEvent(data.event)
  }
  
  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">Events Timeline</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Visualize AI progress events over time
        </p>
      </div>
      
      {/* Tier Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
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
                className="cursor-pointer"
                onClick={() => setSelectedTier(tier)}
                style={selectedTier === tier ? { backgroundColor: tierColors[tier] } : {}}
              >
                {tier}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading timeline...</p>
        </div>
      )}
      
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}
      
      {!loading && !error && timelineData.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            No events found matching your filters.
          </CardContent>
        </Card>
      )}
      
      {!loading && !error && timelineData.length > 0 && (
        <>
          {/* Timeline Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Timeline</CardTitle>
              <CardDescription>
                Click on a point to view event details
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] md:h-[500px]">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart
                    margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      type="number"
                      dataKey="x"
                      name="Date"
                      tickFormatter={formatXAxis}
                      domain={['auto', 'auto']}
                      angle={-45}
                      textAnchor="end"
                    />
                    <YAxis
                      type="number"
                      dataKey="y"
                      name="Significance"
                      tickFormatter={formatYAxis}
                      domain={[0, 1]}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Scatter
                      data={timelineData}
                      onClick={(data) => handleDotClick(data)}
                      cursor="pointer"
                    >
                      {timelineData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
              
              <div className="mt-4 flex justify-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: tierColors.A }} />
                  <span>A-tier (Primary)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: tierColors.B }} />
                  <span>B-tier (Official)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: tierColors.C }} />
                  <span>C-tier (Press)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: tierColors.D }} />
                  <span>D-tier (Social)</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Selected Event Detail */}
          {selectedEvent && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Selected Event</h2>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  Clear Selection
                </button>
              </div>
              <EventCard event={selectedEvent} />
            </div>
          )}
        </>
      )}
    </div>
  )
}

