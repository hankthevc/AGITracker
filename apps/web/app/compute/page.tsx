import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ComputePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-4">Compute & Inputs</h1>
        <p className="text-xl text-muted-foreground">
          Training compute, algorithmic efficiency, and infrastructure build-out
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>OOM meter and infrastructure tracking</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            This page will display:
          </p>
          <ul className="list-disc list-inside text-sm text-muted-foreground mt-2 space-y-1">
            <li>Training run compute (10^24 → 10^27 FLOP)</li>
            <li>Algorithmic efficiency improvements (OOM gains since 2023)</li>
            <li>Data center power commitments (0.1 GW → 10 GW)</li>
            <li>Effective compute trends (algorithmic + hardware)</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

