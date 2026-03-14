"use client";

import { PanelLeftOpen, Plus } from "lucide-react";

import type { Theme } from "@/hooks/useTheme";

interface HeaderProps {
  isConnected: boolean;
  onClear: () => void;
  theme: Theme;
  onToggleTheme: () => void;
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  onNewChat: () => void;
}

export default function Header({
  isConnected,
  onClear,
  theme,
  onToggleTheme,
  isSidebarOpen,
  onToggleSidebar,
  onNewChat,
}: HeaderProps) {
  return (
    <header
      className="flex items-center justify-between px-4 py-3 border-b"
      style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}
    >
      <div className="flex items-center gap-3">
        {!isSidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 rounded-md transition-colors cursor-pointer mr-1"
            style={{
              color: "var(--text-secondary)",
              background: "var(--bg-tertiary)",
            }}
            title="Open sidebar"
          >
            <PanelLeftOpen size={18} />
          </button>
        )}
        <button
          onClick={onNewChat}
          className="p-1.5 rounded-md transition-colors cursor-pointer"
          style={{
            color: "var(--text-secondary)",
            background: "var(--bg-tertiary)",
          }}
          title="New chat"
        >
          <Plus size={18} />
        </button>
        <h1 className="text-lg font-semibold">Agentic AI Chat</h1>
        <span
          className="flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full"
          style={{
            background: isConnected
              ? "var(--status-connected-bg)"
              : "var(--status-disconnected-bg)",
            color: isConnected
              ? "var(--status-connected-color)"
              : "var(--status-disconnected-color)",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{
              background: isConnected
                ? "var(--status-connected-dot)"
                : "var(--status-disconnected-dot)",
            }}
          />
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onToggleTheme}
          className="text-xs px-3 py-1.5 rounded-md transition-colors cursor-pointer"
          style={{
            background: "var(--bg-tertiary)",
            color: "var(--text-secondary)",
            border: "1px solid var(--border)",
          }}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? "Light" : "Dark"}
        </button>
        <button
          onClick={onClear}
          className="text-xs px-3 py-1.5 rounded-md transition-colors cursor-pointer"
          style={{
            background: "var(--bg-tertiary)",
            color: "var(--text-secondary)",
            border: "1px solid var(--border)",
          }}
        >
          Clear Chat
        </button>
      </div>
    </header>
  );
}
