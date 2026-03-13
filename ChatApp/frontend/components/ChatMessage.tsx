"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Message } from "@/domain/entities/Message";

interface ChatMessageProps {
  message: Message;
  isLoading?: boolean;
  isStreaming?: boolean;
}

const CHARS_PER_TICK = 1;
const TICK_MS = 25;

export default function ChatMessage({ message, isLoading, isStreaming }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [displayedLength, setDisplayedLength] = useState(
    isUser ? message.content.length : 0
  );
  const targetLength = useRef(0);
  const rafRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (isUser) {
      setDisplayedLength(message.content.length);
      return;
    }

    targetLength.current = message.content.length;

    const tick = () => {
      setDisplayedLength((prev) => {
        const target = targetLength.current;
        if (prev >= target) return prev;
        const next = Math.min(prev + CHARS_PER_TICK, target);
        rafRef.current = setTimeout(tick, TICK_MS);
        return next;
      });
    };

    if (displayedLength < message.content.length) {
      if (rafRef.current) clearTimeout(rafRef.current);
      rafRef.current = setTimeout(tick, TICK_MS);
    }

    return () => {
      if (rafRef.current) clearTimeout(rafRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [message.content, isUser]);

  const visibleText = isUser
    ? message.content
    : message.content.slice(0, displayedLength);

  const showCursor = !isUser && isStreaming && displayedLength < message.content.length;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className="max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
        style={{
          background: isUser ? "var(--accent)" : "var(--bg-secondary)",
          color: isUser ? "#fff" : "var(--text-primary)",
          border: isUser ? "none" : "1px solid var(--border)",
        }}
      >
        {isLoading && !message.content ? (
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full animate-bounce" style={{ animationDelay: "0ms", background: "var(--loading-dot)" }} />
            <span className="w-2 h-2 rounded-full animate-bounce" style={{ animationDelay: "150ms", background: "var(--loading-dot)" }} />
            <span className="w-2 h-2 rounded-full animate-bounce" style={{ animationDelay: "300ms", background: "var(--loading-dot)" }} />
          </div>
        ) : isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="markdown-body">
            <ReactMarkdown>{visibleText}</ReactMarkdown>
            {showCursor && (
              <span className="inline-block w-2 h-4 ml-0.5 animate-pulse" style={{ verticalAlign: "text-bottom", background: "var(--cursor-color)" }} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
