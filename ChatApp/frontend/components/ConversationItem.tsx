"use client";

import { useState, useRef, useEffect } from "react";
import { Trash2, Pencil, Check, X } from "lucide-react";

import type { ConversationSummary } from "@/domain/entities/ConversationSummary";

interface ConversationItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (title: string) => void;
}

function formatRelativeTime(date: Date): string {
  const now = Date.now();
  const diff = now - date.getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "now";
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d`;
  return date.toLocaleDateString();
}

export default function ConversationItem({
  conversation,
  isActive,
  onSelect,
  onDelete,
  onRename,
}: ConversationItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) inputRef.current?.focus();
  }, [isEditing]);

  const handleSubmitRename = () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== conversation.title) {
      onRename(trimmed);
    }
    setIsEditing(false);
  };

  const handleCancelRename = () => {
    setEditTitle(conversation.title);
    setIsEditing(false);
  };

  return (
    <button
      onClick={isEditing ? undefined : onSelect}
      className="group flex items-center gap-2 w-full px-3 py-2.5 rounded-lg text-left transition-colors cursor-pointer"
      style={{
        background: isActive ? "var(--bg-tertiary)" : "transparent",
        color: "var(--text-primary)",
      }}
    >
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <div className="flex items-center gap-1">
            <input
              ref={inputRef}
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSubmitRename();
                if (e.key === "Escape") handleCancelRename();
              }}
              className="w-full text-sm bg-transparent outline-none px-1 py-0.5 rounded"
              style={{
                border: "1px solid var(--accent)",
                color: "var(--text-primary)",
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <button
              onClick={(e) => { e.stopPropagation(); handleSubmitRename(); }}
              className="p-0.5 rounded hover:opacity-80 cursor-pointer"
              style={{ color: "var(--status-connected-color)" }}
            >
              <Check size={14} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleCancelRename(); }}
              className="p-0.5 rounded hover:opacity-80 cursor-pointer"
              style={{ color: "var(--text-secondary)" }}
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <>
            <p className="text-sm truncate">{conversation.title}</p>
            <p
              className="text-xs mt-0.5"
              style={{ color: "var(--text-secondary)" }}
            >
              {formatRelativeTime(conversation.updatedAt)}
            </p>
          </>
        )}
      </div>

      {!isEditing && (
        <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setEditTitle(conversation.title);
              setIsEditing(true);
            }}
            className="p-1 rounded hover:opacity-80 cursor-pointer"
            style={{ color: "var(--text-secondary)" }}
            title="Rename"
          >
            <Pencil size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="p-1 rounded hover:opacity-80 cursor-pointer"
            style={{ color: "var(--status-disconnected-color)" }}
            title="Delete"
          >
            <Trash2 size={14} />
          </button>
        </div>
      )}
    </button>
  );
}
