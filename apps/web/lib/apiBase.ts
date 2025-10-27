/**
 * Centralized API base URL resolver with intelligent fallbacks.
 * 
 * Resolution order:
 * 1. NEXT_PUBLIC_API_BASE_URL environment variable
 * 2. (Browser only) Auto-detect from window.location, port 8000 if on :3000
 * 3. Fallback to http://localhost:8000
 */

export function getApiBaseUrl(): string {
  // 1. Check environment variable
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/$/, '') // Remove trailing slash
  }
  
  // 2. Browser auto-detection (only works client-side)
  if (typeof window !== 'undefined') {
    const { protocol, hostname, port } = window.location
    
    // If we're on the Next.js dev server (:3000), assume API is on :8000
    if (port === '3000') {
      return `${protocol}//${hostname}:8000`
    }
    
    // Otherwise, assume API is on same origin
    return `${protocol}//${hostname}${port ? `:${port}` : ''}`
  }
  
  // 3. Fallback for SSR or unknown
  return 'http://localhost:8000'
}

