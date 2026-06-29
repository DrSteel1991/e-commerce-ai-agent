export interface User {
  id: string;
  email: string;
  full_name: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ChatSource {
  chunk_id: number;
  filename: string;
  distance: number;
  preview: string;
}

export interface ChatResponse {
  answer: string;
  sources?: ChatSource[];
  agent_action?: string;
  intent?: string;
  user_id?: string | null;
  session_id?: string | null;
  data?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: {
    intent?: string;
    agent_action?: string;
    sources?: ChatSource[];
  };
}
