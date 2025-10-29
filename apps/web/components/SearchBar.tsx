"use client"

import { useState, useEffect, useRef } from "react"
import { Search, X, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

interface SearchResult {
  id: number
  title: string
  summary: string
  publisher: string
  published_at: string
  evidence_tier: "A" | "B" | "C" | "D"
}

export function SearchBar() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      setIsOpen(false)
      return
    }

    setIsLoading(true)
    const timer = setTimeout(async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
        const response = await fetch(
          `${apiUrl}/v1/search?q=${encodeURIComponent(query)}&limit=5`
        )
        if (response.ok) {
          const data = await response.json()
          setResults(data.results || [])
          setIsOpen(true)
        }
      } catch (error) {
        console.error("Search error:", error)
      } finally {
        setIsLoading(false)
      }
    }, 300) // 300ms debounce

    return () => clearTimeout(timer)
  }, [query])

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const tierColors = {
    A: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
    B: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
    C: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20",
    D: "bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20",
  }

  return (
    <div ref={searchRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search events..."
          className="pl-10 pr-10"
          onFocus={() => query.length >= 2 && setIsOpen(true)}
        />
        {query && (
          <button
            onClick={() => {
              setQuery("")
              setResults([])
              setIsOpen(false)
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <X className="h-4 w-4" />
            )}
          </button>
        )}
      </div>

      {/* Search results dropdown */}
      {isOpen && results.length > 0 && (
        <div className="absolute top-full mt-2 w-full bg-white dark:bg-gray-900 border rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {results.map((result) => (
            <Link
              key={result.id}
              href={`/events/${result.id}`}
              onClick={() => setIsOpen(false)}
              className="block p-3 hover:bg-gray-50 dark:hover:bg-gray-800 border-b last:border-b-0 transition-colors"
            >
              <div className="flex items-start gap-2 mb-1">
                <Badge
                  variant="outline"
                  className={`${tierColors[result.evidence_tier]} text-xs`}
                >
                  {result.evidence_tier}
                </Badge>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-1">
                    {result.title}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mt-1">
                    {result.summary}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {result.publisher} • {new Date(result.published_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </Link>
          ))}
          {results.length === 5 && (
            <Link
              href={`/events?search=${encodeURIComponent(query)}`}
              onClick={() => setIsOpen(false)}
              className="block p-3 text-center text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
            >
              See all results →
            </Link>
          )}
        </div>
      )}

      {isOpen && query.length >= 2 && results.length === 0 && !isLoading && (
        <div className="absolute top-full mt-2 w-full bg-white dark:bg-gray-900 border rounded-lg shadow-lg z-50 p-4 text-center text-sm text-gray-600 dark:text-gray-400">
          No results found for "{query}"
        </div>
      )}
    </div>
  )
}
