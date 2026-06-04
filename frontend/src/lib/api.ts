import { ChatRequest, ChatResponse } from "@/types/chat";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:7991/api";

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
