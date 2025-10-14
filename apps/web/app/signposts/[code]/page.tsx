import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SignpostData {
  id: number
  code: string
  name: string
  description: string
  category: string
  metric_name: string
  unit: string
  direction: string
  baseline_value: number
  target_value: number
  methodology_url: string
  first_class: boolean
  short_explainer: string
  icon_emoji: string
}

interface ContentData {
  signpost_code: string
  why_matters: string
  current_state: string
  key_papers: any[]
  key_announcements: any[]
  technical_explanation: string
  updated_at: string
}

interface PredictionData {
  roadmap_name: string
  roadmap_slug: string
  prediction_text: string
  predicted_date: string
  confidence_level: string
  source_page: string
  notes: string
}

interface PaceData {
  signpost_code: string
  current_value: number
  current_date: string
  pace_metrics: Array<{
    roadmap_name: string
    roadmap_slug: string
    days_ahead: number
    status: string
    current_value: number
    current_progress: number
    predicted_date: string
  }>
  analyses: Record<string, string>
}

async function getSignpostData(code: string) {
  try {
    const res = await fetch(`${API_URL}/v1/signposts/by-code/${code}`, { cache: 'no-store' })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

async function getSignpostContent(code: string) {
  try {
    const res = await fetch(`${API_URL}/v1/signposts/by-code/${code}/content`, { cache: 'no-store' })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

async function getSignpostPredictions(code: string) {
  try {
    const res = await fetch(`${API_URL}/v1/signposts/by-code/${code}/predictions`, { cache: 'no-store' })
    if (!res.ok) return { predictions: [] }
    return await res.json()
  } catch {
    return { predictions: [] }
  }
}

async function getSignpostPace(code: string) {
  try {
    const res = await fetch(`${API_URL}/v1/signposts/by-code/${code}/pace`, { cache: 'no-store' })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

function SignpostHero({ signpost }: { signpost: SignpostData }) {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
      <div className="container mx-auto px-4 py-12">
        <div className="flex items-center gap-4 mb-4">
          {signpost.icon_emoji && (
            <span className="text-6xl">{signpost.icon_emoji}</span>
          )}
          <div>
            <h1 className="text-4xl font-bold tracking-tight">{signpost.name}</h1>
            <p className="text-xl text-muted-foreground mt-2">
              {signpost.short_explainer || signpost.description}
            </p>
          </div>
        </div>
        
        <div className="flex gap-3 mt-6">
          <Badge variant={signpost.first_class ? "default" : "secondary"}>
            {signpost.first_class ? "First-Class Benchmark" : "Signpost"}
          </Badge>
          <Badge variant="outline">{signpost.category}</Badge>
          <Badge variant="outline">
            {signpost.metric_name} ({signpost.unit})
          </Badge>
        </div>
      </div>
    </div>
  )
}

function WhyItMatters({ content }: { content: string }) {
  return (
    <section className="py-12 border-b">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-6">Why This Matters</h2>
        <div className="prose prose-lg max-w-none">
          <p className="text-lg leading-relaxed">{content}</p>
        </div>
      </div>
    </section>
  )
}

function CurrentStateSection({ content }: { content: string }) {
  return (
    <section className="py-12 bg-slate-50 border-b">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-6">Current State of the Art</h2>
        <div className="prose prose-lg max-w-none">
          <div className="whitespace-pre-wrap text-lg leading-relaxed">{content}</div>
        </div>
      </div>
    </section>
  )
}

function PaceComparison({ paceData }: { paceData: PaceData | null }) {
  if (!paceData || paceData.pace_metrics.length === 0) {
    return (
      <section className="py-12 border-b">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-6">Pace Analysis</h2>
          <p className="text-muted-foreground">
            Pace analysis will be available once we have timeline predictions for this signpost.
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="py-12 border-b">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-6">Pace Analysis: Are We Ahead or Behind?</h2>
        
        <div className="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Current Progress</p>
              <p className="text-3xl font-bold">{paceData.pace_metrics[0]?.current_progress}%</p>
            </div>
            {paceData.current_value && (
              <div>
                <p className="text-sm text-muted-foreground">Current Value</p>
                <p className="text-3xl font-bold">{paceData.current_value}</p>
              </div>
            )}
            {paceData.current_date && (
              <div>
                <p className="text-sm text-muted-foreground">As of</p>
                <p className="text-lg font-semibold">{new Date(paceData.current_date).toLocaleDateString()}</p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {paceData.pace_metrics.map((metric) => (
            <Card 
              key={metric.roadmap_slug}
              className={`border-2 ${
                metric.status === 'ahead' 
                  ? 'border-green-500 bg-green-50' 
                  : metric.status === 'behind'
                  ? 'border-red-500 bg-red-50'
                  : 'border-yellow-500 bg-yellow-50'
              }`}
            >
              <CardHeader>
                <CardTitle className="text-lg">{metric.roadmap_name}</CardTitle>
                <CardDescription>
                  Target: {new Date(metric.predicted_date).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 mb-4">
                  <span className={`text-4xl ${
                    metric.status === 'ahead' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metric.status === 'ahead' ? '↗' : '↘'}
                  </span>
                  <div>
                    <p className="text-2xl font-bold">
                      {Math.abs(metric.days_ahead)} days
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {metric.status === 'ahead' ? 'ahead of schedule' : 'behind schedule'}
                    </p>
                  </div>
                </div>
                
                {paceData.analyses[metric.roadmap_slug] && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {paceData.analyses[metric.roadmap_slug]}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

function KeyResources({ papers, announcements }: { papers: any[], announcements: any[] }) {
  // Parse JSON if needed
  const parsedPapers = typeof papers === 'string' ? JSON.parse(papers) : papers || []
  const parsedAnnouncements = typeof announcements === 'string' ? JSON.parse(announcements) : announcements || []
  
  if (parsedPapers.length === 0 && parsedAnnouncements.length === 0) {
    return null
  }

  return (
    <section className="py-12 border-b">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-6">Key Resources</h2>
        
        {parsedPapers.length > 0 && (
          <div className="mb-8">
            <h3 className="text-2xl font-semibold mb-4">Research Papers</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {parsedPapers.map((paper: any, idx: number) => (
                <Card key={idx}>
                  <CardHeader>
                    <CardTitle className="text-lg">
                      <a 
                        href={paper.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        {paper.title} →
                      </a>
                    </CardTitle>
                    <CardDescription>{paper.date}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{paper.summary}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
        
        {parsedAnnouncements.length > 0 && (
          <div>
            <h3 className="text-2xl font-semibold mb-4">Key Announcements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {parsedAnnouncements.map((announcement: any, idx: number) => (
                <Card key={idx} className="bg-blue-50 border-blue-200">
                  <CardHeader>
                    <CardTitle className="text-lg">
                      <a 
                        href={announcement.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        {announcement.title} →
                      </a>
                    </CardTitle>
                    <CardDescription>{announcement.date}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{announcement.summary}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

function TechnicalDeepDive({ content }: { content: string }) {
  return (
    <section className="py-12 bg-slate-50 border-b">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-6">Technical Deep Dive</h2>
        <div className="prose prose-lg max-w-none">
          <div className="whitespace-pre-wrap text-lg leading-relaxed">{content}</div>
        </div>
      </div>
    </section>
  )
}

function RelatedSignposts({ category, currentCode }: { category: string, currentCode: string }) {
  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-6">Related Signposts</h2>
        <p className="text-muted-foreground mb-4">
          Other signposts in the <Badge variant="outline">{category}</Badge> category:
        </p>
        <div className="flex gap-4">
          <Link 
            href="/benchmarks" 
            className="text-primary hover:underline font-medium"
          >
            View all benchmarks →
          </Link>
          <Link 
            href="/" 
            className="text-primary hover:underline font-medium"
          >
            Back to dashboard →
          </Link>
        </div>
      </div>
    </section>
  )
}

export default async function SignpostDetailPage({
  params,
}: {
  params: { code: string }
}) {
  const signpost = await getSignpostData(params.code)
  
  if (!signpost) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4">Signpost Not Found</h1>
        <p className="text-muted-foreground mb-6">
          The signpost with code "{params.code}" could not be found.
        </p>
        <Link href="/" className="text-primary hover:underline">
          ← Back to dashboard
        </Link>
      </div>
    )
  }

  const [content, predictionsData, paceData] = await Promise.all([
    getSignpostContent(params.code),
    getSignpostPredictions(params.code),
    getSignpostPace(params.code),
  ])

  return (
    <div className="min-h-screen">
      <SignpostHero signpost={signpost} />
      
      {content && (
        <>
          <WhyItMatters content={content.why_matters} />
          <CurrentStateSection content={content.current_state} />
          <PaceComparison paceData={paceData} />
          <KeyResources 
            papers={content.key_papers} 
            announcements={content.key_announcements} 
          />
          <TechnicalDeepDive content={content.technical_explanation} />
        </>
      )}
      
      <RelatedSignposts category={signpost.category} currentCode={params.code} />
    </div>
  )
}

