"use client";

import { useState } from "react";
import type { ToolStepData } from "@/app/page";

interface ToolStepProps {
  step: ToolStepData;
}

const TOOL_ICONS: Record<string, string> = {
  web_search: "&#x1f50d;",
  calculator: "&#x1f4ca;",
  get_current_time: "&#x1f552;",
  create_note: "&#x1f4dd;",
};

export default function ToolStep({ step }: ToolStepProps) {
  const [expanded, setExpanded] = useState(false);

  if (step.type === "tool_call") {
    const icon = TOOL_ICONS[step.tool] || "&#x2699;";
    return (
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg w-full text-left transition-colors cursor-pointer"
        style={{
          background: "#1a1a2e",
          color: "var(--accent-hover)",
          border: "1px solid #2a2a4a",
        }}
      >
        <span dangerouslySetInnerHTML={{ __html: icon }} />
        <span className="font-medium">Using {step.tool.replace(/_/g, " ")}</span>
        {step.input && Object.keys(step.input).length > 0 && (
          <span style={{ color: "var(--text-secondary)" }} className="truncate">
            {JSON.stringify(step.input).slice(0, 60)}
          </span>
        )}
        <span className="ml-auto" style={{ color: "var(--text-secondary)" }}>
          {expanded ? "▲" : "▼"}
        </span>
        {expanded && step.input && (
          <pre
            className="mt-2 p-2 rounded text-xs overflow-x-auto"
            style={{ background: "#0d0d1a" }}
            onClick={(e) => e.stopPropagation()}
          >
            {JSON.stringify(step.input, null, 2)}
          </pre>
        )}
      </button>
    );
  }

  if (step.type === "tool_result") {
    let parsed: unknown = step.result;
    try {
      parsed = JSON.parse(step.result || "{}");
    } catch {
      // keep as string
    }

    return (
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg w-full text-left transition-colors cursor-pointer"
        style={{
          background: "#0d1a0d",
          color: "#6ee7b7",
          border: "1px solid #1a3a1a",
        }}
      >
        <span>&#x2705;</span>
        <span className="font-medium">Result from {step.tool.replace(/_/g, " ")}</span>
        <span className="ml-auto" style={{ color: "var(--text-secondary)" }}>
          {expanded ? "▲" : "▼"}
        </span>
        {expanded && (
          <pre
            className="mt-2 p-2 rounded text-xs overflow-x-auto w-full"
            style={{ background: "#0a140a" }}
            onClick={(e) => e.stopPropagation()}
          >
            {typeof parsed === "object" ? JSON.stringify(parsed, null, 2) : String(parsed)}
          </pre>
        )}
      </button>
    );
  }

  return null;
}
