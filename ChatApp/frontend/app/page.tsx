"use client";

import { useChat } from "@/hooks/useChat";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import { useTheme } from "@/hooks/useTheme";
import ChatMessage from "@/components/ChatMessage";
import ToolStepComponent from "@/components/ToolStep";
import ChatInput from "@/components/ChatInput";
import Header from "@/components/Header";

export default function Home() {
  const { messages, isLoading, isConnected, sendMessage, clearChat } = useChat();
  const messagesEndRef = useAutoScroll([messages]);
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <Header
        isConnected={isConnected}
        onClear={clearChat}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

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
            {msg.role === "assistant" && msg.toolSteps.length > 0 && (
              <div className="mb-2 space-y-1">
                {msg.toolSteps.map((step, i) => (
                  <ToolStepComponent key={i} step={step} />
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
