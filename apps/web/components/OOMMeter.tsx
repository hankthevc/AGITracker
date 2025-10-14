'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface OOMMeterProps {
  currentOOM: number
  targetOOM: number
  label?: string
}

export function OOMMeter({ currentOOM, targetOOM, label = "Effective Compute" }: OOMMeterProps) {
  // OOM scale from 24 to 27 (10^24 to 10^27 FLOP)
  const minOOM = 24
  const maxOOM = 27
  const range = maxOOM - minOOM
  
  // Calculate percentages
  const currentPercent = ((currentOOM - minOOM) / range) * 100
  const targetPercent = ((targetOOM - minOOM) / range) * 100
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        <CardDescription>Training run compute (FLOP)</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center p-6">
        <div className="relative w-16 h-64 bg-gray-200 rounded-full overflow-hidden">
          {/* Target marker */}
          <div
            className="absolute left-0 right-0 h-1 bg-red-500 border-t-2 border-red-600"
            style={{ bottom: `${targetPercent}%` }}
          />
          
          {/* Current fill */}
          <div
            className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-blue-600 to-blue-400 transition-all duration-500"
            style={{ height: `${currentPercent}%` }}
          />
        </div>
        
        <div className="mt-6 text-center space-y-2">
          <div>
            <div className="text-2xl font-bold">10^{currentOOM.toFixed(1)}</div>
            <div className="text-sm text-muted-foreground">Current</div>
          </div>
          <div className="text-sm">
            <div className="text-muted-foreground">Target: 10^{targetOOM}</div>
          </div>
        </div>
        
        {/* Legend */}
        <div className="mt-4 space-y-1 text-xs text-muted-foreground">
          <div>10^24: GPT-3 scale</div>
          <div>10^26: Intermediate</div>
          <div>10^27: Target threshold</div>
        </div>
      </CardContent>
    </Card>
  )
}

