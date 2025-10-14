import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScenarioTimeline } from '@/components/ScenarioTimeline'

export default function AI2027RoadmapPage() {
  const milestones = [
    {
      id: 'm1',
      name: 'SWE-bench Verified 70%',
      targetDate: 'Q2 2025',
      actualDate: 'Q4 2024',
      status: 'ahead' as const,
    },
    {
      id: 'm2',
      name: 'OSWorld 50%',
      targetDate: 'Q4 2025',
      status: 'pending' as const,
    },
    {
      id: 'm3',
      name: 'Multi-week Autonomous Projects',
      targetDate: 'Q2 2026',
      status: 'pending' as const,
    },
    {
      id: 'm4',
      name: '10% Economic Displacement',
      targetDate: 'Q4 2026',
      status: 'pending' as const,
    },
    {
      id: 'm5',
      name: 'AGI Threshold (Combined Metrics)',
      targetDate: 'Q2 2027',
      status: 'pending' as const,
    },
  ]
  
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-4">AI 2027 Scenario Roadmap</h1>
        <p className="text-xl text-muted-foreground">
          Timeline-aligned signposts for near-term AGI scenarios
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Preset Weights</CardTitle>
          <CardDescription>Category weighting for this roadmap</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold">35%</div>
              <div className="text-sm text-muted-foreground">Agents</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold">30%</div>
              <div className="text-sm text-muted-foreground">Capabilities</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold">25%</div>
              <div className="text-sm text-muted-foreground">Inputs</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold">10%</div>
              <div className="text-sm text-muted-foreground">Security</div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <ScenarioTimeline milestones={milestones} scenarioName="AI 2027" />
      
      <Card>
        <CardHeader>
          <CardTitle>Scenario Overview</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <p>
            The AI 2027 scenario projects that by 2027, AI systems will be capable of autonomously
            performing the majority of economically valuable remote cognitive work. This roadmap
            emphasizes near-term milestones and explicit timeline alignment.
          </p>
          
          <h3>Key Assumptions</h3>
          <ul>
            <li>Continued exponential improvement in benchmark performance (2023-2027)</li>
            <li>Successful "unhobbling" of agentic capabilities</li>
            <li>Sufficient compute availability (10^26-10^27 FLOP training runs)</li>
            <li>Rapid real-world deployment and economic integration</li>
          </ul>
          
          <h3>Critical Milestones</h3>
          <ul>
            <li>
              <strong>2025:</strong> SWE-bench Verified 70%, OSWorld 50% - demonstrating
              practical computer use at scale
            </li>
            <li>
              <strong>2026:</strong> Multi-week autonomous projects, 10% job displacement -
              economic impact becomes measurable
            </li>
            <li>
              <strong>2027:</strong> Combined threshold crossing on all first-class benchmarks -
              AGI operational definition satisfied
            </li>
          </ul>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Status Indicators</CardTitle>
          <CardDescription>Understanding timeline alignment</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-3">
              <div className="w-12 h-8 bg-green-600 rounded flex items-center justify-center text-white text-xs font-bold">
                Ahead
              </div>
              <div>Milestone reached earlier than projected timeline</div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-8 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
                On
              </div>
              <div>Progress tracking with timeline expectations</div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-8 bg-red-600 rounded flex items-center justify-center text-white text-xs font-bold">
                Behind
              </div>
              <div>Progress slower than timeline projections</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

