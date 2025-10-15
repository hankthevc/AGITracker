/**
 * API client for AGI Signpost Tracker
 */

import { getApiBaseUrl } from './apiBase'
import { fetchJson } from './fetchJson'

export async function fetcher(url: string) {
  const baseUrl = getApiBaseUrl()
  return fetchJson(`${baseUrl}${url}`)
}

export const apiClient = {
  getIndex: async (preset: string = 'equal', date?: string) => {
    const params = new URLSearchParams({ preset })
    if (date) params.append('date', date)
    return fetcher(`/v1/index?${params}`)
  },
  
  getSignposts: async (category?: string, firstClass?: boolean) => {
    const params = new URLSearchParams()
    if (category) params.append('category', category)
    if (firstClass !== undefined) params.append('first_class', String(firstClass))
    return fetcher(`/v1/signposts?${params}`)
  },
  
  getSignpost: async (id: number) => {
    return fetcher(`/v1/signposts/${id}`)
  },
  
  getEvidence: async (signpostId?: number, tier?: string, skip: number = 0, limit: number = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
    if (signpostId) params.append('signpost_id', String(signpostId))
    if (tier) params.append('tier', tier)
    return fetcher(`/v1/evidence?${params}`)
  },
  
  getChangelog: async (skip: number = 0, limit: number = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
    return fetcher(`/v1/changelog?${params}`)
  },
  
  getFeed: async () => {
    return fetcher('/v1/feed.json')
  },
}

