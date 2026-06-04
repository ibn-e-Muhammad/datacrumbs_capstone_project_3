export type Role = "user" | "assistant" | "system";

export interface Message {
  role: Role;
  content: string;
}

export interface ChatMessage extends Message {
  id: string;
  createdAt: Date;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  reply: string;
  conversation_id?: string;
}
