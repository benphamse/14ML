"use client";

import { Plus, PanelLeftClose, MessageSquare } from "lucide-react";

import type { ConversationSummary } from "@/domain/entities/ConversationSummary";
import type { ProjectSummary } from "@/domain/entities/ProjectSummary";
import ConversationItem from "./ConversationItem";
import ProjectSelector from "./ProjectSelector";

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  isOpen: boolean;
  onToggle: () => void;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation: (id: string, title: string) => void;
  isLoading: boolean;
  projects: ProjectSummary[];
  activeProjectId: string | null;
  isProjectsLoading: boolean;
  onSelectProject: (id: string | null) => void;
  onCreateProject: (name: string) => void;
  onDeleteProject: (id: string) => void;
  onRenameProject: (id: string, name: string) => void;
}

export default function Sidebar({
  conversations,
  activeConversationId,
  isOpen,
  onToggle,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  onRenameConversation,
  isLoading,
  projects,
  activeProjectId,
  isProjectsLoading,
  onSelectProject,
  onCreateProject,
  onDeleteProject,
  onRenameProject,
}: SidebarProps) {
  return (
    <aside
      className="flex flex-col h-screen shrink-0 border-r transition-all duration-200 overflow-hidden"
      style={{
        width: isOpen ? 280 : 0,
        borderColor: isOpen ? "var(--border)" : "transparent",
        background: "var(--bg-secondary)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-3 py-3 border-b shrink-0"
        style={{ borderColor: "var(--border)" }}
      >
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer flex-1 mr-2"
          style={{
            background: "var(--accent)",
            color: "#fff",
          }}
        >
          <Plus size={16} />
          New Chat
        </button>
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md transition-colors cursor-pointer"
          style={{
            color: "var(--text-secondary)",
            background: "var(--bg-tertiary)",
          }}
          title="Close sidebar"
        >
          <PanelLeftClose size={18} />
        </button>
      </div>

      {/* Project Selector */}
      <ProjectSelector
        projects={projects}
        activeProjectId={activeProjectId}
        isLoading={isProjectsLoading}
        onSelectProject={onSelectProject}
        onCreateProject={onCreateProject}
        onDeleteProject={onDeleteProject}
        onRenameProject={onRenameProject}
      />

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
        {isLoading ? (
          <div className="space-y-2 px-2 pt-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-12 rounded-lg animate-pulse"
                style={{ background: "var(--bg-tertiary)" }}
              />
            ))}
          </div>
        ) : conversations.length === 0 ? (
          <div
            className="flex flex-col items-center justify-center h-full text-center px-4"
            style={{ color: "var(--text-secondary)" }}
          >
            <MessageSquare size={32} className="mb-2 opacity-40" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              isActive={conv.id === activeConversationId}
              onSelect={() => onSelectConversation(conv.id)}
              onDelete={() => onDeleteConversation(conv.id)}
              onRename={(title) => onRenameConversation(conv.id, title)}
            />
          ))
        )}
      </div>
    </aside>
  );
}
