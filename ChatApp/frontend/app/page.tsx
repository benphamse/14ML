"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import ChatMessage from "@/components/ChatMessage";
import ToolStep from "@/components/ToolStep";
import ChatInput from "@/components/ChatInput";
import Header from "@/components/Header";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolSteps?: ToolStepData[];
}

export interface ToolStepData {
  type: "tool_call" | "tool_result";
  tool: string;
  input?: Record<string, unknown>;
  result?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pendingToolSteps = useRef<ToolStepData[]>([]);
  const streamedContent = useRef("");

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const updateLastAssistant = useCallback(
    (updater: (msg: Message) => Message) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.role === "assistant") {
          return [...prev.slice(0, -1), updater(last)];
        }
        return prev;
      });
    },
    []
  );

  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/chat");

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "tool_call" || data.type === "tool_result") {
        pendingToolSteps.current.push(data);
        updateLastAssistant((msg) => ({
          ...msg,
          toolSteps: [...pendingToolSteps.current],
        }));
      } else if (data.type === "stream") {
        // Append streamed text chunk
        streamedContent.current += data.content;
        const currentContent = streamedContent.current;
        updateLastAssistant((msg) => ({
          ...msg,
          content: currentContent,
        }));
      } else if (data.type === "reply") {
        // Final reply - mark as done
        setIsLoading(false);
        const finalContent = data.content;
        updateLastAssistant((msg) => ({
          ...msg,
          content: finalContent,
          toolSteps: [...pendingToolSteps.current],
        }));
        pendingToolSteps.current = [];
        streamedContent.current = "";
      } else if (data.type === "status") {
        // Show status message (e.g. rate limit retry)
        updateLastAssistant((msg) => ({
          ...msg,
          content: data.content,
        }));
      } else if (data.type === "error") {
        setIsLoading(false);
        updateLastAssistant((msg) => ({
          ...msg,
          content: `Error: ${data.message}`,
        }));
        pendingToolSteps.current = [];
        streamedContent.current = "";
      } else if (data.type === "cleared") {
        setMessages([]);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    wsRef.current = ws;
  }, [updateLastAssistant]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      wsRef.current?.close();
    };
  }, [connectWebSocket]);

  const sendMessage = (content: string) => {
    if (!content.trim() || !wsRef.current || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: crypto.randomUUID(), role: "assistant", content: "", toolSteps: [] },
    ]);

    setIsLoading(true);
    pendingToolSteps.current = [];
    streamedContent.current = "";

    wsRef.current.send(JSON.stringify({ type: "message", content }));
  };

  const clearChat = () => {
    wsRef.current?.send(JSON.stringify({ type: "clear" }));
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <Header isConnected={isConnected} onClear={clearChat} />

      <main className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-4xl mb-4">&#x1f916;</div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: "var(--text-primary)" }}>
              Agentic AI Chat
            </h2>
            <p className="text-sm max-w-md" style={{ color: "var(--text-secondary)" }}>
              I can search the web, do calculations, check the time, and take notes.
              Ask me anything!
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            {msg.role === "assistant" && msg.toolSteps && msg.toolSteps.length > 0 && (
              <div className="mb-2 space-y-1">
                {msg.toolSteps.map((step, i) => (
                  <ToolStep key={i} step={step} />
                ))}
              </div>
            )}
            {(msg.content || msg.role === "user") && (
              <ChatMessage
                message={msg}
                isLoading={isLoading && msg.role === "assistant" && !msg.content}
                isStreaming={isLoading && msg.role === "assistant"}
              />
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}
