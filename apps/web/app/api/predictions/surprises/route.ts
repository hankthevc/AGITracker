import { NextResponse } from "next/server"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api-production-8535.up.railway.app"

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/predictions/surprises?days=90&limit=10`, {
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
    console.error("Error fetching surprises:", error)
    return NextResponse.json(
      { error: "Failed to fetch surprises", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
