'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatPercent } from '@/lib/utils'

interface CompositeGaugeProps {
  value: number
  label?: string
  description?: string
}

export function CompositeGauge({ value, label = "Overall Proximity", description }: CompositeGaugeProps) {
  // Clamp value between 0 and 1
  const clampedValue = Math.max(0, Math.min(1, value))
  
  // Color gradient: green (low) -> yellow -> red (high)
  const getColor = (val: number) => {
    if (val < 0.3) return 'rgb(34, 197, 94)' // green
    if (val < 0.6) return 'rgb(234, 179, 8)' // yellow
    return 'rgb(239, 68, 68)' // red
  }
  
  const color = getColor(clampedValue)
  const rotation = clampedValue * 180 - 90 // -90 to 90 degrees
  
  return (
    <Card data-testid="composite-gauge" className="w-full">
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center p-6">
        <div className="relative w-64 h-32 mb-4">
          {/* Background arc */}
          <svg viewBox="0 0 200 100" className="w-full h-full">
            <path
              d="M 10 90 A 90 90 0 0 1 190 90"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
              strokeLinecap="round"
            />
            {/* Filled arc */}
            <path
              d="M 10 90 A 90 90 0 0 1 190 90"
              fill="none"
              stroke={color}
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={`${clampedValue * 283} 283`}
            />
            {/* Needle */}
            <line
              x1="100"
              y1="90"
              x2="100"
              y2="20"
              stroke="#1f2937"
              strokeWidth="3"
              strokeLinecap="round"
              transform={`rotate(${rotation} 100 90)`}
            />
            <circle cx="100" cy="90" r="5" fill="#1f2937" />
          </svg>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold" style={{ color }}>
            {formatPercent(clampedValue)}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {clampedValue < 0.3 ? 'Early Stage' : clampedValue < 0.6 ? 'Progressing' : 'Advanced'}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

