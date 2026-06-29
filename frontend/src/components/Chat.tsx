import { useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../api/client";
import type { ChatMessage } from "../types";

interface ChatProps {
  isLoggedIn: boolean;
}

const STARTER_PROMPTS = [
  "Where is my order #1?",
  "What is your refund policy?",
  "How long does standard shipping take?",
  "What payment methods do you accept?",
  "How do I track my order?",
];

export function Chat({ isLoggedIn }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I can help with orders, refunds, and product questions. Try one of the examples below.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setError("");
    setInput("");

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendChatMessage(trimmed);

      if (response.session_id) {
        localStorage.setItem("chat_session_id", response.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer || "No answer returned.",
        meta: {
          intent: response.intent,
          agent_action: response.agent_action,
          sources: response.sources,
        },
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-layout">
      <div className="card chat-panel">
        {!isLoggedIn && (
          <p className="muted guest-note">
            Sign in to check order status. Policy and product questions work as a
            guest.
          </p>
        )}

        <div className="messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.role === "user" ? "user" : "assistant"}`}
            >
              <div className="bubble">{message.content}</div>

              {message.meta && (
                <div className="meta">
                  {message.meta.intent && (
                    <span className="tag">intent: {message.meta.intent}</span>
                  )}
                  {message.meta.agent_action && (
                    <span className="tag">
                      action: {message.meta.agent_action}
                    </span>
                  )}
                </div>
              )}

              {message.meta?.sources && message.meta.sources.length > 0 && (
                <details className="sources">
                  <summary>Sources ({message.meta.sources.length})</summary>
                  <ul>
                    {message.meta.sources.map((source) => (
                      <li key={source.chunk_id}>
                        <strong>{source.filename}</strong>
                        <p>{source.preview}</p>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="bubble typing">Thinking...</div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {error && <p className="error">{error}</p>}

        <div className="prompts">
          {STARTER_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="prompt-chip"
              onClick={() => sendMessage(prompt)}
              disabled={loading}
            >
              {prompt}
            </button>
          ))}
        </div>

        <form
          className="chat-input"
          onSubmit={(event) => {
            event.preventDefault();
            void sendMessage(input);
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about an order, refund, or product..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
