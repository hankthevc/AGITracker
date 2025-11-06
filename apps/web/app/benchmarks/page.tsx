import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { SafeLink } from '@/lib/SafeLink'

/**
 * Check if HLE data should show smoothing indicator.
 * Display-only guard: if latest sample < 7 days old and only 1 sample,
 * suppress delta arrows and show "smoothed (≥7d)" tooltip.
 */
function isSmoothedHLE(claims: Array<{ observed_at: string }> | null): boolean {
  if (!claims || claims.length === 0) return false
  if (claims.length >= 2) return false // Multiple samples, show delta normally
  
  const latestDate = new Date(claims[0].observed_at)
  const daysSinceLatest = (Date.now() - latestDate.getTime()) / (1000 * 60 * 60 * 24)
  
  return daysSinceLatest < 7 // Single sample < 7 days old = smoothed
}

export default function BenchmarksPage() {
  const benchmarkCodes: Record<string, string> = {
    'SWE-bench Verified': 'swe_bench_85',
    'OSWorld': 'osworld_50',
    'WebArena': 'webarena_60',
    'GPQA Diamond': 'gpqa_75',
    'Humanity\'s Last Exam (Text-Only)': 'hle_text_50',
  }
  
  const benchmarks = [
    {
      name: 'SWE-bench Verified',
      description: 'Real-world software engineering tasks from GitHub pull requests',
      url: 'https://www.swebench.com',
      current: '~65%',
      target: '85-90%',
      status: 'In Progress',
    },
    {
      name: 'OSWorld',
      description: 'Complex operating system-level tasks requiring multi-step reasoning',
      url: 'https://os-world.github.io',
      current: '~22%',
      target: '65-85%',
      status: 'Early Stage',
    },
    {
      name: 'WebArena',
      description: 'Web navigation and interaction tasks simulating real-world usage',
      url: 'https://webarena.dev',
      current: '~45%',
      target: '70-85%',
      status: 'In Progress',
    },
    {
      name: 'GPQA Diamond',
      description: 'PhD-level scientific reasoning questions across multiple domains',
      url: 'https://github.com/idavidrein/gpqa',
      current: '~60%',
      target: '75-85%',
      status: 'In Progress',
    },
    {
      name: 'Humanity\'s Last Exam (Text-Only)',
      description: 'PhD-level reasoning breadth benchmark across multiple subjects',
      url: 'https://scale.com/leaderboard/hle',
      current: '~37.5%',
      target: '50-70%',
      status: 'Monitor-Only',
      provisional: true,
      version: 'Text-2500', // Optional version identifier
      qualityNote: 'Note: Bio/Chem subsets have known label-quality issues. Currently B-tier (Provisional) evidence only.',
      qualityTooltip: 'HLE is tracked as a long-horizon indicator (2026-2028) but does not affect main composite gauges until A-tier evidence becomes available.',
      // Note: When integrating live claim data, use isSmoothedHLE() to suppress
      // weekly delta arrows for single samples <7 days old and show "smoothed (≥7d)" tooltip
    },
  ]
  
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-4">Benchmark Progress</h1>
        <p className="text-xl text-muted-foreground">
          Live tracking of AI performance on first-class benchmarks
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {benchmarks.map((benchmark) => (
          <Card 
            key={benchmark.name} 
            data-testid={benchmark.provisional ? "hle-benchmark-tile" : "benchmark-card"}
            className={benchmark.provisional ? "border-orange-200 bg-orange-50/30" : ""}
          >
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="flex-1">{benchmark.name}</CardTitle>
                <div className="flex flex-wrap gap-2 items-start">
                  {benchmark.provisional && (
                    <Badge 
                      variant="secondary" 
                      className="bg-orange-100 text-orange-800 hover:bg-orange-200"
                      data-testid="hle-provisional-badge"
                    >
                      Provisional
                    </Badge>
                  )}
                  {(benchmark as any).version && (
                    <Badge 
                      variant="outline" 
                      className="bg-slate-50 text-slate-700 border-slate-300"
                      data-testid="hle-version-pill"
                    >
                      v{(benchmark as any).version}
                    </Badge>
                  )}
                </div>
              </div>
              <CardDescription>{benchmark.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Current SOTA</p>
                  <p className="text-2xl font-bold">{benchmark.current}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Target Range</p>
                  <p className="text-2xl font-bold">{benchmark.target}</p>
                </div>
              </div>
              
              {benchmark.qualityNote && (
                <div 
                  className="bg-yellow-50 border border-yellow-200 rounded-md p-3 text-xs text-yellow-800"
                  data-testid="hle-quality-note"
                >
                  <span className="font-semibold">⚠️ Data Quality:</span> {benchmark.qualityNote}{' '}
                  <SafeLink 
                    href="https://scale.com/leaderboard/hle" 
                    className="underline hover:text-yellow-900"
                  >
                    Learn more
                  </SafeLink>
                </div>
              )}
              
              <div className="pt-4 border-t space-y-3">
                <div className="flex items-center justify-between">
                  <span 
                    className={`text-sm font-medium px-3 py-1 rounded-full ${
                      benchmark.status === 'In Progress' 
                        ? 'bg-yellow-100 text-yellow-800' 
                        : benchmark.status === 'Monitor-Only'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                    data-testid={benchmark.status === 'Monitor-Only' ? 'hle-monitor-only' : undefined}
                    title={(benchmark as any).qualityTooltip}
                  >
                    {benchmark.status}
                  </span>
                  <a
                    href={benchmark.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    View Leaderboard →
                  </a>
                </div>
                
                {benchmarkCodes[benchmark.name] && (
                  <div className="pt-2">
                    <Link 
                      href={`/signposts/${benchmarkCodes[benchmark.name]}`}
                      className="text-sm font-medium text-primary hover:underline flex items-center gap-1"
                    >
                      📚 Learn more: Why this benchmark matters →
                    </Link>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle>About These Benchmarks</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <p>
            These benchmark families track AI progress toward economically transformative capabilities:
          </p>
          <ul>
            <li>
              <strong>SWE-bench Verified:</strong> Tests ability to solve real software engineering tasks,
              including bug fixes and feature additions from actual GitHub PRs.
            </li>
            <li>
              <strong>OSWorld:</strong> Measures proficiency in complex computer use, from file management
              to application interaction across multiple OS environments.
            </li>
            <li>
              <strong>WebArena:</strong> Evaluates web interaction capabilities including navigation,
              form filling, and multi-step task completion on realistic websites.
            </li>
            <li>
              <strong>GPQA Diamond:</strong> Assesses scientific reasoning at PhD level across physics,
              chemistry, and biology—requiring deep domain knowledge.
            </li>
            <li>
              <strong>HLE (Humanity&apos;s Last Exam):</strong> Monitor-only. PhD-level reasoning breadth 
              benchmark with known label-quality issues in Bio/Chem subsets. Currently B-tier (Provisional) 
              evidence only. Does not affect main composite until A-tier evidence available.
            </li>
          </ul>
          <p>
            The first four benchmarks measure <em>economically relevant</em> capabilities and directly impact 
            our main progress gauges. HLE is tracked separately as a long-horizon indicator (2026-2028) and 
            remains monitor-only pending data quality improvements or peer-reviewed validation.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

