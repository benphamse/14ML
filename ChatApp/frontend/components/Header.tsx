"use client";

import type { Theme } from "@/hooks/useTheme";

interface HeaderProps {
  isConnected: boolean;
  onClear: () => void;
  theme: Theme;
  onToggleTheme: () => void;
}

export default function Header({ isConnected, onClear, theme, onToggleTheme }: HeaderProps) {
  return (
    <header
      className="flex items-center justify-between px-4 py-3 border-b"
      style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}
    >
      <div className="flex items-center gap-3">
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
