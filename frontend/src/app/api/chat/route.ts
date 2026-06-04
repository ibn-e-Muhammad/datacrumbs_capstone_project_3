import { NextResponse } from "next/server";
import { ChatRequest } from "@/types/chat";

// Backend URL is localhost:8000
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7991/api";

export async function POST(request: Request) {
  try {
    const body: ChatRequest = await request.json();

    // Forward the request to the FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend returned ${response.status}: ${errorText}`);
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in chat proxy:", error);
    return NextResponse.json(
      { error: "Failed to communicate with backend service." },
      { status: 500 }
    );
  }
}
