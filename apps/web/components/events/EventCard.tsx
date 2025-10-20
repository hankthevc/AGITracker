'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'
import { Event, EventAnalysis } from '@/lib/types'
import { getApiBaseUrl } from '@/lib/apiBase'

interface EventCardProps {
  event: Event
  showAnalysis?: boolean
}

export function EventCard({ event, showAnalysis = true }: EventCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [analysis, setAnalysis] = useState<EventAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const tierColors = {
    A: 'bg-green-600 text-white hover:bg-green-700',
    B: 'bg-blue-600 text-white hover:bg-blue-700',
    C: 'bg-yellow-600 text-white hover:bg-yellow-700',
    D: 'bg-red-600 text-white hover:bg-red-700',
  }
  
  const tierLabels = {
    A: 'Primary Evidence',
    B: 'Official Lab',
    C: 'Reputable Press',
    D: 'Social Media',
  }
  
  const movesGauges = event.evidence_tier === 'A' || event.evidence_tier === 'B'
  
  const fetchAnalysis = async () => {
    if (analysis || loading) return
    
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = getApiBaseUrl()
      const response = await fetch(`${apiUrl}/v1/events/${event.id}/analysis`)
      
      if (response.status === 404) {
        setError('No analysis available yet')
        return
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch analysis: ${response.statusText}`)
      }
      
      const data = await response.json()
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }
  
  const handleToggleExpand = () => {
    if (!expanded && showAnalysis) {
      fetchAnalysis()
    }
    setExpanded(!expanded)
  }
  
  return (
    <Card 
      className="hover:shadow-lg transition-shadow" 
      data-testid={`event-card-${event.id}`}
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg flex-1">{event.title}</CardTitle>
          <div className="flex flex-col gap-2">
            <Badge
              className={tierColors[event.evidence_tier]}
              data-testid={`evidence-tier-${event.evidence_tier}`}
            >
              {event.evidence_tier}
            </Badge>
            {movesGauges && (
              <Badge variant="outline" className="text-xs">
                Moves Gauges
              </Badge>
            )}
          </div>
        </div>
        <CardDescription>{tierLabels[event.evidence_tier]}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {event.summary && (
          <p className="text-sm">{event.summary}</p>
        )}
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Source</div>
            <a
              href={event.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline truncate block"
            >
              {event.publisher || 'Unknown'}
            </a>
          </div>
          <div>
            <div className="text-muted-foreground">Published</div>
            <div>{formatDate(event.published_at || event.date || '')}</div>
          </div>
        </div>
        
        {event.signpost_links && event.signpost_links.length > 0 && (
          <div>
            <div className="text-sm text-muted-foreground mb-2">Linked Signposts</div>
            <div className="flex flex-wrap gap-2">
              {event.signpost_links.map((link) => (
                <Badge 
                  key={link.signpost_id} 
                  variant="secondary"
                  className="cursor-pointer hover:bg-secondary/80"
                  title={link.signpost_name}
                >
                  {link.signpost_code}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {showAnalysis && (event.evidence_tier === 'A' || event.evidence_tier === 'B') && (
          <div className="border-t pt-4">
            <button
              onClick={handleToggleExpand}
              className="text-sm font-medium text-primary hover:underline"
              data-testid="expand-analysis-button"
            >
              {expanded ? '▼ Hide "Why this matters"' : '▶ Show "Why this matters"'}
            </button>
            
            {expanded && (
              <div className="mt-4 space-y-4">
                {loading && (
                  <div className="text-sm text-muted-foreground">Loading analysis...</div>
                )}
                
                {error && (
                  <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
                    {error}
                  </div>
                )}
                
                {analysis && (
                  <div className="space-y-4">
                    {analysis.summary && (
                      <div>
                        <div className="text-sm font-medium mb-1">Summary</div>
                        <p className="text-sm text-muted-foreground">{analysis.summary}</p>
                      </div>
                    )}
                    
                    {analysis.relevance_explanation && (
                      <div>
                        <div className="text-sm font-medium mb-1">Why This Matters</div>
                        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                          {analysis.relevance_explanation}
                        </p>
                      </div>
                    )}
                    
                    {analysis.impact_json && (
                      <div>
                        <div className="text-sm font-medium mb-2">Impact Timeline</div>
                        <div className="space-y-2 text-sm">
                          {analysis.impact_json.short && (
                            <div>
                              <span className="font-medium">0-6 months:</span>{' '}
                              <span className="text-muted-foreground">{analysis.impact_json.short}</span>
                            </div>
                          )}
                          {analysis.impact_json.medium && (
                            <div>
                              <span className="font-medium">6-18 months:</span>{' '}
                              <span className="text-muted-foreground">{analysis.impact_json.medium}</span>
                            </div>
                          )}
                          {analysis.impact_json.long && (
                            <div>
                              <span className="font-medium">18+ months:</span>{' '}
                              <span className="text-muted-foreground">{analysis.impact_json.long}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {analysis.significance_score !== null && (
                      <div className="flex items-center gap-2">
                        <div className="text-sm font-medium">Significance:</div>
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${(analysis.significance_score || 0) * 100}%` }}
                          />
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {((analysis.significance_score || 0) * 100).toFixed(0)}%
                        </div>
                      </div>
                    )}
                    
                    {analysis.llm_version && (
                      <div className="text-xs text-muted-foreground pt-2 border-t">
                        Analysis: {analysis.llm_version} • Generated {formatDate(analysis.generated_at)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

