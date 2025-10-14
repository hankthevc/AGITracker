import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function BenchmarksPage() {
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
          <Card key={benchmark.name} data-testid="benchmark-card">
            <CardHeader>
              <CardTitle>{benchmark.name}</CardTitle>
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
              
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                    benchmark.status === 'In Progress' 
                      ? 'bg-yellow-100 text-yellow-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
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
            These four benchmark families represent our "first-class" signposts—core capabilities
            required for economically transformative AI:
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
          </ul>
          <p>
            These benchmarks were chosen because they measure <em>economically relevant</em> capabilities
            rather than narrow technical skills. Progress here directly correlates with ability to perform
            valuable remote cognitive work.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

