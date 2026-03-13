"use client";

interface HeaderProps {
  isConnected: boolean;
  onClear: () => void;
}

export default function Header({ isConnected, onClear }: HeaderProps) {
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
            background: isConnected ? "#064e3b" : "#7f1d1d",
            color: isConnected ? "#6ee7b7" : "#fca5a5",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: isConnected ? "#34d399" : "#f87171" }}
          />
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>

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
    </header>
  );
}
