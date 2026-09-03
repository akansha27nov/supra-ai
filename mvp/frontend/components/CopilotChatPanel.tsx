// frontend/components/CopilotChatPanel.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Send, ShieldAlert } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { sendCopilotMessage, type ChatMessage } from "@/lib/api";

// Shared markdown component overrides — keeps assistant replies on the same
// typography/spacing scale as the rest of the panel instead of falling back
// to the browser's default <ul>/<strong> styling.
const markdownComponents = {
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong className="font-semibold text-on-surface">{children}</strong>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="mb-2 last:mb-0 list-disc pl-4 space-y-1">{children}</ul>
  ),
  ol: ({ children }: { children?: React.ReactNode }) => (
    <ol className="mb-2 last:mb-0 list-decimal pl-4 space-y-1">{children}</ol>
  ),
  li: ({ children }: { children?: React.ReactNode }) => (
    <li className="leading-relaxed">{children}</li>
  ),
  code: ({ children }: { children?: React.ReactNode }) => (
    <code className="font-code-sm bg-surface-container-highest px-1 py-0.5 rounded text-xs">
      {children}
    </code>
  ),
};

// Local display type — api.ts's ChatMessage is the wire shape (role/content
// only); `grounded` is per-reply UI metadata, never sent back to the server.
type DisplayMessage = ChatMessage & { grounded?: boolean };

interface CopilotChatPanelProps {
  recordId: string;
  supplierName?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function CopilotChatPanel({ recordId, supplierName, isOpen, onClose }: CopilotChatPanelProps) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isLoading) return;

    const history: ChatMessage[] = messages.map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      const { reply, grounded } = await sendCopilotMessage(recordId, { message: question, history });
      setMessages((prev) => [...prev, { role: "assistant", content: reply, grounded }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong reaching the co-pilot.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-stretch justify-end">
      <div className="bg-surface-container-lowest w-full max-w-md h-full border-l border-outline-variant shadow-xl flex flex-col">
        {/* Header — mirrors the Gap Notice modal header pattern */}
        <div className="flex justify-between items-center px-5 py-4 border-b border-surface-variant">
          <h3 className="text-lg font-bold text-on-surface flex items-center gap-2">
            <Bot size={20} className="text-primary" /> Case Co-pilot
          </h3>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface font-bold">
            ✕
          </button>
        </div>

        <div className="px-5 py-1.5 text-xs text-on-surface-variant border-b border-surface-variant truncate">
          {supplierName ? `${supplierName} · ` : ""}
          <span className="font-code-sm">{recordId}</span>
        </div>

        {/* Persistent disclosure — consistent with the compliance/transparency story */}
        <div className="mx-5 mt-3 mb-1 flex items-start gap-2 rounded-lg bg-surface-container px-3 py-2 text-xs text-on-surface-variant border border-outline-variant">
          <ShieldAlert size={14} className="text-primary mt-0.5 shrink-0" />
          AI-generated answers grounded in this case's evidence only — not a compliance decision.
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-3 custom-scrollbar">
          {messages.length === 0 && (
            <div className="text-sm text-on-surface-variant italic">
              Ask about this case — e.g. "why was this flagged?" or "what evidence supports the RoHS violation?"
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={
                  m.role === "user"
                    ? "max-w-[85%] rounded-lg bg-primary px-3 py-2 text-sm text-on-primary"
                    : "max-w-[85%] rounded-lg bg-surface-container px-3 py-2 text-sm text-on-surface"
                }
              >
                {m.role === "assistant" ? (
                  <ReactMarkdown components={markdownComponents}>{m.content}</ReactMarkdown>
                ) : (
                  <div className="whitespace-pre-wrap">{m.content}</div>
                )}
                {m.role === "assistant" && m.grounded === false && (
                  <div className="mt-1.5 border-t border-outline-variant pt-1.5 text-[11px] text-error flex items-center gap-1">
                    <ShieldAlert size={12} /> This may go beyond the evidence on file for this case.
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-surface-container px-3 py-2 text-sm text-on-surface-variant animate-pulse">
                Thinking…
              </div>
            </div>
          )}
          {error && (
            <div className="rounded-lg border border-error/20 bg-error-container/30 px-3 py-2 text-sm text-error">
              {error}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-surface-variant p-4">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about this case…"
              rows={1}
              disabled={isLoading}
              className="flex-1 resize-none rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary disabled:opacity-70"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="flex items-center gap-1.5 px-3 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium hover:bg-surface-tint transition-colors shadow-sm disabled:opacity-50"
            >
              <Send size={14} /> Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
