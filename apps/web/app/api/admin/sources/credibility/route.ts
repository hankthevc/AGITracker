import { NextResponse } from "next/server"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://agi-tracker-production.up.railway.app"

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/admin/source-credibility`, {
      next: { revalidate: 3600 } // Cache for 1 hour
    })

    if (!response.ok) {
      const errorText = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}`, details: errorText },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching source credibility:", error)
    return NextResponse.json(
      { error: "Failed to fetch credibility data", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
