"use client";

import { useState } from "react";
import { ToolStep as ToolStepEntity } from "@/domain/entities/ToolStep";

interface ToolStepProps {
  step: ToolStepEntity;
}

const TOOL_ICONS: Record<string, string> = {
  web_search: "&#x1f50d;",
  calculator: "&#x1f4ca;",
  get_current_time: "&#x1f552;",
  create_note: "&#x1f4dd;",
};

export default function ToolStepComponent({ step }: ToolStepProps) {
  const [expanded, setExpanded] = useState(false);

  if (step.type === "tool_call") {
    const icon = TOOL_ICONS[step.tool] || "&#x2699;";
    return (
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg w-full text-left transition-colors cursor-pointer"
        style={{
          background: "var(--tool-call-bg)",
          color: "var(--accent-hover)",
          border: "1px solid var(--tool-call-border)",
        }}
      >
        <span dangerouslySetInnerHTML={{ __html: icon }} />
        <span className="font-medium">Using {step.displayName}</span>
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
            style={{ background: "var(--tool-call-pre-bg)" }}
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
          background: "var(--tool-result-bg)",
          color: "var(--tool-result-color)",
          border: "1px solid var(--tool-result-border)",
        }}
      >
        <span>&#x2705;</span>
        <span className="font-medium">Result from {step.displayName}</span>
        <span className="ml-auto" style={{ color: "var(--text-secondary)" }}>
          {expanded ? "▲" : "▼"}
        </span>
        {expanded && (
          <pre
            className="mt-2 p-2 rounded text-xs overflow-x-auto w-full"
            style={{ background: "var(--tool-result-pre-bg)" }}
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
