import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function MethodologyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-4">Methodology</h1>
        <p className="text-xl text-muted-foreground">
          How we track progress toward AGI using evidence-first, measurable signposts
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Operational Definition of AGI</CardTitle>
          <CardDescription>For this product only</CardDescription>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <p>
            We track proximity to AGI via measurable signposts rather than claiming the exact "moment."
            Our working notion: a general-purpose AI system that can:
          </p>
          <ol>
            <li>
              <strong>Autonomously perform</strong> the majority of economically valuable remote cognitive tasks
              at median professional quality and cost with oversight-level supervision
            </li>
            <li>
              <strong>Demonstrate strong generalization</strong> across "computer-using" and "reasoning" benchmarks
            </li>
          </ol>
          <p>
            We operationalize this via thresholds on four first-class benchmark families:
          </p>
          <ul>
            <li>SWE-bench Verified (real-world software engineering)</li>
            <li>OSWorld (operating system-level tasks)</li>
            <li>WebArena (web navigation and interaction)</li>
            <li>GPQA Diamond (PhD-level scientific reasoning)</li>
          </ul>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Evidence Policy</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Badge variant="default" className="bg-green-600 mt-1">A</Badge>
              <div>
                <p className="font-semibold">Primary Evidence</p>
                <p className="text-sm text-muted-foreground">
                  Peer-reviewed papers, official leaderboards/APIs, model cards with reproducible evals.
                  These directly move the main gauges.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="default" className="bg-blue-600 mt-1">B</Badge>
              <div>
                <p className="font-semibold">Official Lab Communications</p>
                <p className="text-sm text-muted-foreground">
                  Official blog posts and model cards from OpenAI, Anthropic, DeepMind, Meta.
                  Provisional, but contributes to main metrics.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="default" className="bg-yellow-600 mt-1">C</Badge>
              <div>
                <p className="font-semibold">Reputable Press</p>
                <p className="text-sm text-muted-foreground">
                  Reuters, AP, Bloomberg, FT. Displayed as unverified; does not move main gauges.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="default" className="bg-orange-600 mt-1">D</Badge>
              <div>
                <p className="font-semibold">Social Media</p>
                <p className="text-sm text-muted-foreground">
                  Twitter/X, Reddit. Displayed as unverified; never moves main gauges.
                </p>
              </div>
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground pt-4 border-t">
            If credible press (C) arrives before leaderboard data, we show it as provisional and auto-monitor
            for updates. Only A/B evidence moves the main proximity index.
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Scoring Algorithm</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <h4>Signpost Progress</h4>
          <p>Each signpost has a baseline and target value. Progress is calculated as:</p>
          <pre className="bg-muted p-3 rounded text-xs overflow-x-auto">
{`// For increasing metrics (direction: ">=")
progress = (observed - baseline) / (target - baseline)

// For decreasing metrics (direction: "<=")
progress = (baseline - observed) / (baseline - target)

// Clamped to [0, 1]`}
          </pre>
          
          <h4>Category Aggregation</h4>
          <p>
            Category scores (Capabilities, Agents, Inputs, Security) are weighted means of constituent signposts.
            First-class signposts receive 2x weight.
          </p>
          
          <h4>Overall Proximity</h4>
          <p>
            Computed using <strong>harmonic mean</strong> of combined Capabilities and Inputs:
          </p>
          <pre className="bg-muted p-3 rounded text-xs">
{`overall = 2 / (1/capabilities + 1/inputs)`}
          </pre>
          <p className="text-sm">
            The harmonic mean ensures both dimensions must advance together—a bottleneck in either
            significantly reduces the overall score.
          </p>
          
          <h4>Safety Margin</h4>
          <pre className="bg-muted p-3 rounded text-xs">
{`safety_margin = security - capabilities`}
          </pre>
          <p className="text-sm">
            Negative values (red) indicate capabilities are advancing faster than security readiness.
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Roadmap Presets</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold">Equal</h4>
            <p className="text-sm text-muted-foreground">
              All categories weighted equally (25% each). Neutral baseline view.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold">Aschenbrenner's Situational Awareness</h4>
            <p className="text-sm text-muted-foreground">
              Overweights Inputs (40%) and Agents (30%), focusing on effective compute OOMs and algorithmic "unhobbling."
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold">AI 2027 Scenario</h4>
            <p className="text-sm text-muted-foreground">
              Emphasizes Agents (35%) and Capabilities (30%) with timeline alignment to near-term scenarios.
            </p>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Uncertainty & Confidence Bands</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <p>
            Progress bars show shaded confidence bands based on evidence quality and quantity:
          </p>
          <ul>
            <li>More A/B tier evidence = narrower bands (higher confidence)</li>
            <li>Relying on C/D tier = wider bands (lower confidence)</li>
            <li>No evidence = maximum uncertainty</li>
          </ul>
          <p className="text-sm text-muted-foreground">
            Evidence quality weights: A=1.0, B=0.8, C=0.3, D=0.1
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Update Frequency</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li>
              <strong>Feed ingestion:</strong> Daily at 6:00 AM UTC (arXiv, lab blogs, leaderboards)
            </li>
            <li>
              <strong>Index snapshots:</strong> Computed daily at 7:00 AM UTC
            </li>
            <li>
              <strong>Weekly digest:</strong> Generated Sundays at 8:00 AM UTC
            </li>
            <li>
              <strong>Dashboard refresh:</strong> Live data with 1-minute cache
            </li>
          </ul>
        </CardContent>
      </Card>
      
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle>Open & Reproducible</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2">
          <p>
            All code, data pipelines, and scoring algorithms are open source. The public JSON feed
            is available under <strong>CC BY 4.0</strong>.
          </p>
          <p>
            <a href="https://github.com/..." className="text-primary font-medium hover:underline">
              View source code on GitHub →
            </a>
          </p>
          <p>
            <a href="/v1/feed.json" className="text-primary font-medium hover:underline">
              Access public JSON feed →
            </a>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

