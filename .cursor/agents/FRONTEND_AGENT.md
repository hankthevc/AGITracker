# 🎨 FRONTEND AGENT - UI/UX Polish Specialist

**Role**: Implement viral features, dark mode, PWA, mobile optimization, and social sharing.

**Priority**: P1-P2 (High to Medium) - You make the dashboard beautiful and shareable.

**Reporting To**: Supervisor Agent

**Dependencies**: Backend Agent (needs stable API)

---

## Your Mission

Transform the AGI Tracker UI from functional to viral-ready. Add dark mode, PWA features, social sharing, and mobile optimizations to create a beautiful, shareable experience.

**Success Criteria**:
- Dark mode fully functional
- PWA installable on mobile
- Social sharing with beautiful OpenGraph previews
- Lighthouse score >90
- Mobile-first design perfected
- <2s page load time

---

## Week 3-4 Priority: Viral Features & Polish

### Task 1: Dark Mode Implementation (4-6 hours)

**Problem**: Dark mode mentioned in roadmap but not implemented.

**Your Actions**:

1. **Configure shadcn/ui Dark Theme**:
   ```bash
   cd apps/web
   
   # Install next-themes (shadcn uses this)
   npm install next-themes
   ```

2. **Add Theme Provider**:
   ```typescript
   // apps/web/app/providers.tsx
   'use client'
   
   import { ThemeProvider } from 'next-themes'
   import { ReactNode } from 'react'
   
   export function Providers({ children }: { children: ReactNode }) {
     return (
       <ThemeProvider
         attribute="class"
         defaultTheme="system"
         enableSystem
         disableTransitionOnChange
       >
         {children}
       </ThemeProvider>
     )
   }
   ```

3. **Update Root Layout**:
   ```typescript
   // apps/web/app/layout.tsx
   import { Providers } from './providers'
   
   export default function RootLayout({ children }: { children: React.ReactNode }) {
     return (
       <html lang="en" suppressHydrationWarning>
         <body>
           <Providers>
             {children}
           </Providers>
         </body>
       </html>
     )
   }
   ```

4. **Create Theme Toggle Component**:
   ```typescript
   // apps/web/components/theme-toggle.tsx
   'use client'
   
   import { Moon, Sun } from 'lucide-react'
   import { useTheme } from 'next-themes'
   import { Button } from '@/components/ui/button'
   import {
     DropdownMenu,
     DropdownMenuContent,
     DropdownMenuItem,
     DropdownMenuTrigger,
   } from '@/components/ui/dropdown-menu'
   
   export function ThemeToggle() {
     const { setTheme } = useTheme()
   
     return (
       <DropdownMenu>
         <DropdownMenuTrigger asChild>
           <Button variant="outline" size="icon">
             <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
             <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
             <span className="sr-only">Toggle theme</span>
           </Button>
         </DropdownMenuTrigger>
         <DropdownMenuContent align="end">
           <DropdownMenuItem onClick={() => setTheme('light')}>
             Light
           </DropdownMenuItem>
           <DropdownMenuItem onClick={() => setTheme('dark')}>
             Dark
           </DropdownMenuItem>
           <DropdownMenuItem onClick={() => setTheme('system')}>
             System
           </DropdownMenuItem>
         </DropdownMenuContent>
       </DropdownMenu>
     )
   }
   ```

5. **Add to Navigation**:
   ```typescript
   // apps/web/components/nav.tsx
   import { ThemeToggle } from './theme-toggle'
   
   export function Nav() {
     return (
       <nav className="flex items-center justify-between p-4">
         {/* ... existing nav items ... */}
         <ThemeToggle />
       </nav>
     )
   }
   ```

6. **Update Tailwind Config**:
   ```javascript
   // apps/web/tailwind.config.ts
   module.exports = {
     darkMode: ['class'],
     // ... rest of config
   }
   ```

7. **Test All Components in Dark Mode**:
   ```bash
   # Manual testing checklist
   - [ ] CompositeGauge readable in dark mode
   - [ ] LaneProgress visible in dark mode
   - [ ] SafetyDial clear in dark mode
   - [ ] Evidence cards styled for dark mode
   - [ ] Forms and inputs usable in dark mode
   - [ ] Charts (Recharts) styled for dark mode
   ```

**Deliverable**: Fully functional dark mode with system preference detection.

---

### Task 2: PWA Features (4-6 hours)

**Problem**: App not installable, no offline support.

**Your Actions**:

1. **Create Web App Manifest**:
   ```json
   // apps/web/public/manifest.json
   {
     "name": "AGI Signpost Tracker",
     "short_name": "AGI Tracker",
     "description": "Evidence-first dashboard tracking proximity to AGI via measurable signposts",
     "start_url": "/",
     "display": "standalone",
     "background_color": "#ffffff",
     "theme_color": "#000000",
     "orientation": "portrait",
     "icons": [
       {
         "src": "/icons/icon-192x192.png",
         "sizes": "192x192",
         "type": "image/png",
         "purpose": "any maskable"
       },
       {
         "src": "/icons/icon-512x512.png",
         "sizes": "512x512",
         "type": "image/png",
         "purpose": "any maskable"
       }
     ],
     "categories": ["productivity", "news", "education"],
     "screenshots": [
       {
         "src": "/screenshots/desktop-1.png",
         "sizes": "1280x720",
         "type": "image/png",
         "form_factor": "wide"
       },
       {
         "src": "/screenshots/mobile-1.png",
         "sizes": "750x1334",
         "type": "image/png",
         "form_factor": "narrow"
       }
     ]
   }
   ```

2. **Link Manifest in Layout**:
   ```typescript
   // apps/web/app/layout.tsx
   export const metadata = {
     title: 'AGI Signpost Tracker',
     description: 'Evidence-first AGI proximity dashboard',
     manifest: '/manifest.json',
     themeColor: [
       { media: '(prefers-color-scheme: light)', color: '#ffffff' },
       { media: '(prefers-color-scheme: dark)', color: '#000000' },
     ],
     appleWebApp: {
       capable: true,
       statusBarStyle: 'default',
       title: 'AGI Tracker',
     },
   }
   ```

3. **Create App Icons**:
   ```bash
   # Generate icons from a source image
   # Use https://realfavicongenerator.net/ or similar
   
   # Save to apps/web/public/icons/
   icon-192x192.png
   icon-512x512.png
   apple-touch-icon.png
   favicon.ico
   ```

4. **Add Service Worker (Optional - Basic Caching)**:
   ```typescript
   // apps/web/app/sw.ts
   /// <reference lib="webworker" />
   
   const CACHE_NAME = 'agi-tracker-v1'
   const STATIC_ASSETS = [
     '/',
     '/manifest.json',
     '/icons/icon-192x192.png',
     '/icons/icon-512x512.png',
   ]
   
   self.addEventListener('install', (event: ExtendableEvent) => {
     event.waitUntil(
       caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
     )
   })
   
   self.addEventListener('fetch', (event: FetchEvent) => {
     event.respondWith(
       caches.match(event.request).then((response) => {
         return response || fetch(event.request)
       })
     )
   })
   ```

5. **Register Service Worker**:
   ```typescript
   // apps/web/app/layout.tsx (in client component)
   useEffect(() => {
     if ('serviceWorker' in navigator) {
       navigator.serviceWorker.register('/sw.js')
         .then(reg => console.log('SW registered', reg))
         .catch(err => console.log('SW registration failed', err))
     }
   }, [])
   ```

6. **Add Install Prompt**:
   ```typescript
   // apps/web/components/install-prompt.tsx
   'use client'
   
   import { useState, useEffect } from 'react'
   import { Button } from './ui/button'
   
   export function InstallPrompt() {
     const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
     const [showPrompt, setShowPrompt] = useState(false)
   
     useEffect(() => {
       const handler = (e: Event) => {
         e.preventDefault()
         setDeferredPrompt(e)
         setShowPrompt(true)
       }
   
       window.addEventListener('beforeinstallprompt', handler)
       return () => window.removeEventListener('beforeinstallprompt', handler)
     }, [])
   
     const handleInstall = async () => {
       if (!deferredPrompt) return
   
       deferredPrompt.prompt()
       const { outcome } = await deferredPrompt.userChoice
       
       if (outcome === 'accepted') {
         setShowPrompt(false)
       }
       
       setDeferredPrompt(null)
     }
   
     if (!showPrompt) return null
   
     return (
       <div className="fixed bottom-4 right-4 p-4 bg-card border rounded-lg shadow-lg">
         <p className="mb-2">Install AGI Tracker for quick access</p>
         <Button onClick={handleInstall}>Install</Button>
       </div>
     )
   }
   ```

**Deliverable**: PWA installable on mobile/desktop, offline support for key pages.

---

### Task 3: Social Sharing & OpenGraph (6-8 hours)

**Problem**: No social sharing, link previews not optimized.

**Your Actions**:

1. **Add OpenGraph Meta Tags**:
   ```typescript
   // apps/web/app/layout.tsx
   export const metadata = {
     metadataBase: new URL('https://agi-tracker.vercel.app'),
     title: {
       default: 'AGI Signpost Tracker',
       template: '%s | AGI Tracker',
     },
     description: 'Evidence-first dashboard tracking proximity to AGI via measurable signposts',
     openGraph: {
       title: 'AGI Signpost Tracker',
       description: 'Track AGI progress through peer-reviewed evidence and expert roadmaps',
       url: 'https://agi-tracker.vercel.app',
       siteName: 'AGI Tracker',
       images: [
         {
           url: '/og-image.png',
           width: 1200,
           height: 630,
           alt: 'AGI Signpost Tracker Dashboard',
         },
       ],
       locale: 'en_US',
       type: 'website',
     },
     twitter: {
       card: 'summary_large_image',
       title: 'AGI Signpost Tracker',
       description: 'Evidence-first AGI proximity dashboard',
       images: ['/og-image.png'],
       creator: '@yourusername',
     },
   }
   ```

2. **Generate Dynamic OpenGraph Images for Events**:
   ```typescript
   // apps/web/app/events/[id]/opengraph-image.tsx
   import { ImageResponse } from 'next/og'
   
   export const runtime = 'edge'
   export const size = { width: 1200, height: 630 }
   
   export default async function Image({ params }: { params: { id: string } }) {
     // Fetch event data
     const event = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/events/${params.id}`)
       .then(res => res.json())
   
     return new ImageResponse(
       (
         <div
           style={{
             display: 'flex',
             flexDirection: 'column',
             width: '100%',
             height: '100%',
             padding: '40px',
             backgroundColor: '#000',
             color: '#fff',
           }}
         >
           <div style={{ fontSize: 48, fontWeight: 'bold' }}>
             {event.title}
           </div>
           <div style={{ fontSize: 24, marginTop: 20, opacity: 0.8 }}>
             {event.source_type} • Tier {event.tier}
           </div>
           <div style={{ fontSize: 20, marginTop: 'auto' }}>
             AGI Signpost Tracker
           </div>
         </div>
       ),
       size
     )
   }
   ```

3. **Create Share Buttons Component**:
   ```typescript
   // apps/web/components/share-buttons.tsx
   'use client'
   
   import { Twitter, Linkedin, Link as LinkIcon } from 'lucide-react'
   import { Button } from './ui/button'
   import { toast } from 'sonner'
   
   interface ShareButtonsProps {
     url: string
     title: string
     description?: string
   }
   
   export function ShareButtons({ url, title, description }: ShareButtonsProps) {
     const fullUrl = `https://agi-tracker.vercel.app${url}`
   
     const shareTwitter = () => {
       const text = `${title}\n\n${description || ''}\n\nvia @agitracker`
       const tweetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(fullUrl)}`
       window.open(tweetUrl, '_blank')
     }
   
     const shareLinkedIn = () => {
       const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`
       window.open(linkedinUrl, '_blank')
     }
   
     const copyLink = async () => {
       try {
         await navigator.clipboard.writeText(fullUrl)
         toast.success('Link copied to clipboard!')
       } catch (err) {
         toast.error('Failed to copy link')
       }
     }
   
     return (
       <div className="flex gap-2">
         <Button variant="outline" size="sm" onClick={shareTwitter}>
           <Twitter className="h-4 w-4 mr-2" />
           Tweet
         </Button>
         <Button variant="outline" size="sm" onClick={shareLinkedIn}>
           <Linkedin className="h-4 w-4 mr-2" />
           Share
         </Button>
         <Button variant="outline" size="sm" onClick={copyLink}>
           <LinkIcon className="h-4 w-4 mr-2" />
           Copy
         </Button>
       </div>
     )
   }
   ```

4. **Add Pre-filled Tweet Templates**:
   ```typescript
   // apps/web/lib/share-templates.ts
   export function generateEventTweet(event: Event): string {
     const impact = event.significance_score > 0.8 ? '🚨 Major' : '📊 Notable'
     
     return `${impact} AI Development:\n\n${event.title}\n\nTier ${event.tier} evidence from ${event.source_type}\n\nTrack AGI progress: https://agi-tracker.vercel.app/events/${event.id}`
   }
   
   export function generateWeeklyDigestTweet(digest: WeeklyDigest): string {
     const topMoves = digest.top_events.slice(0, 3).map(e => `• ${e.title}`).join('\n')
     
     return `📈 This Week in AGI Progress:\n\n${topMoves}\n\n+ ${digest.total_events - 3} more developments\n\nFull digest: https://agi-tracker.vercel.app/digest/${digest.week}`
   }
   ```

5. **Test Social Previews**:
   ```bash
   # Test tools:
   # Twitter: https://cards-dev.twitter.com/validator
   # LinkedIn: https://www.linkedin.com/post-inspector/
   # Facebook: https://developers.facebook.com/tools/debug/
   
   # Verify og:image renders correctly
   # Verify og:title and og:description display
   # Verify twitter:card shows as summary_large_image
   ```

**Deliverable**: Social sharing working, beautiful OpenGraph previews, pre-filled tweet templates.

---

### Task 4: Mobile Optimization (4-6 hours)

**Your Actions**:

1. **Responsive Design Audit**:
   ```bash
   # Test on:
   - iPhone SE (375px width)
   - iPhone 12 Pro (390px)
   - iPad (768px)
   - Desktop (1280px+)
   ```

2. **Fix Mobile Issues**:
   ```typescript
   // Common fixes:
   
   // 1. Scrollable tables
   <div className="overflow-x-auto">
     <table className="min-w-full">
       {/* ... */}
     </table>
   </div>
   
   // 2. Responsive grids
   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
     {/* ... */}
   </div>
   
   // 3. Mobile-friendly navigation
   <nav className="fixed bottom-0 md:static md:flex">
     {/* Mobile: bottom bar, Desktop: top nav */}
   </nav>
   
   // 4. Touch-friendly buttons
   <Button size="lg" className="min-h-[44px] min-w-[44px]">
     {/* Minimum 44x44px for iOS */}
   </Button>
   ```

3. **Optimize Chart Rendering**:
   ```typescript
   // apps/web/components/composite-gauge.tsx
   import { useState, useEffect } from 'react'
   
   export function CompositeGauge({ value }: { value: number }) {
     const [isMobile, setIsMobile] = useState(false)
   
     useEffect(() => {
       setIsMobile(window.innerWidth < 768)
     }, [])
   
     return (
       <ResponsiveContainer
         width="100%"
         height={isMobile ? 200 : 300}
       >
         {/* Smaller on mobile */}
       </ResponsiveContainer>
     )
   }
   ```

4. **Add Mobile Gestures**:
   ```typescript
   // Swipe gestures for timeline navigation
   import { useSwipeable } from 'react-swipeable'
   
   export function Timeline() {
     const handlers = useSwipeable({
       onSwipedLeft: () => nextPage(),
       onSwipedRight: () => prevPage(),
       trackMouse: true,
     })
   
     return <div {...handlers}>{/* timeline */}</div>
   }
   ```

**Deliverable**: Perfect mobile experience, tested on iOS/Android devices.

---

### Task 5: Performance Optimization (6-8 hours)

**Your Actions**:

1. **Run Lighthouse Audit**:
   ```bash
   cd apps/web
   npx lighthouse http://localhost:3000 --output json --output-path ./lighthouse-report.json
   ```

2. **Fix Performance Issues**:
   
   **Bundle Size Optimization**:
   ```javascript
   // next.config.js
   module.exports = {
     // ... existing config
     webpack: (config, { isServer }) => {
       if (!isServer) {
         // Reduce client bundle size
         config.optimization.splitChunks = {
           chunks: 'all',
           cacheGroups: {
             vendor: {
               test: /[\\/]node_modules[\\/]/,
               name(module) {
                 const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1]
                 return `npm.${packageName.replace('@', '')}`
               },
             },
           },
         }
       }
       return config
     },
   }
   ```

   **Dynamic Imports**:
   ```typescript
   // Lazy load heavy components
   const Timeline = dynamic(() => import('@/components/timeline'), {
     loading: () => <Skeleton />,
     ssr: false, // Client-side only if needed
   })
   ```

   **Image Optimization**:
   ```typescript
   import Image from 'next/image'
   
   // Use Next.js Image for automatic optimization
   <Image
     src="/hero.png"
     alt="AGI Tracker"
     width={1200}
     height={630}
     priority // LCP image
   />
   ```

3. **Implement Loading States**:
   ```typescript
   // apps/web/app/loading.tsx
   export default function Loading() {
     return (
       <div className="flex items-center justify-center min-h-screen">
         <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary" />
       </div>
     )
   }
   ```

**Deliverable**: Lighthouse score >90, bundle size <800KB, LCP <2s.

---

## Your File Ownership

**Primary**:
- `apps/web/app/**/*.tsx` (pages)
- `apps/web/components/**/*.tsx`
- `apps/web/styles/**/*.css`
- `apps/web/public/**/*`
- `apps/web/tailwind.config.ts`
- `apps/web/next.config.js`

**Shared** (coordinate with Testing Agent):
- `apps/web/e2e/**/*.ts` (when E2E tests need UI changes)

---

## Daily Status Template

Write to `.cursor/agents/status/FRONTEND_status.md`:

```markdown
# Frontend Agent Status - YYYY-MM-DD

## Accomplishments
- ✅ [Feature] - [details]

## In Progress
- [Feature] - [% complete]

## Blockers
- [ ] None
- [ ] [Blocker]

## Tomorrow
- [ ] [Next feature]

## Metrics
- Lighthouse Score: [X]
- Bundle Size: [X KB]
- LCP: [Xs]
- Dark Mode Components: [X / Y]
```

---

**YOU ARE THE ARTIST. MAKE IT BEAUTIFUL. MAKE IT SHAREABLE.**

