"use client";

import { useState, useEffect, useCallback } from "react";

import { useChat } from "@/hooks/useChat";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import { useTheme } from "@/hooks/useTheme";
import { useConversationList } from "@/hooks/useConversationList";
import { useProjectList } from "@/hooks/useProjectList";
import { useSidebar } from "@/hooks/useSidebar";
import ChatMessage from "@/components/ChatMessage";
import ToolStepComponent from "@/components/ToolStep";
import ChatInput from "@/components/ChatInput";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";

export default function Home() {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

  const {
    projects,
    isLoading: isProjectsLoading,
    createProject,
    deleteProject,
    updateProject,
  } = useProjectList();

  const {
    conversations,
    isLoading: isConversationsLoading,
    createConversation,
    deleteConversation,
    renameConversation,
    refreshList,
  } = useConversationList(activeProjectId);

  const { messages, isLoading, isConnected, isHistoryLoading, sendMessage, clearChat } =
    useChat(activeConversationId);
  const messagesEndRef = useAutoScroll([messages]);
  const { theme, toggleTheme } = useTheme();
  const sidebar = useSidebar();

  // On first load or project switch: select most recent conversation or create one
  useEffect(() => {
    if (isConversationsLoading) return;

    // If active conversation exists in current list, keep it
    if (activeConversationId && conversations.some((c) => c.id === activeConversationId)) {
      return;
    }

    if (conversations.length > 0) {
      setActiveConversationId(conversations[0].id);
    } else {
      setActiveConversationId(null);
    }
  }, [conversations, isConversationsLoading, activeConversationId]);

  const handleNewChat = useCallback(async () => {
    const conv = await createConversation();
    setActiveConversationId(conv.id);
  }, [createConversation]);

  const handleDeleteConversation = useCallback(
    async (id: string) => {
      await deleteConversation(id);
      if (id === activeConversationId) {
        const remaining = conversations.filter((c) => c.id !== id);
        if (remaining.length > 0) {
          setActiveConversationId(remaining[0].id);
        } else {
          setActiveConversationId(null);
        }
      }
    },
    [activeConversationId, conversations, deleteConversation],
  );

  const handleSendMessage = useCallback(
    async (content: string) => {
      // Auto-create a conversation if none is active
      if (!activeConversationId) {
        const conv = await createConversation();
        setActiveConversationId(conv.id);
        // Wait a tick for the WS to connect before sending
        setTimeout(() => sendMessage(content), 300);
      } else {
        sendMessage(content);
      }
      setTimeout(refreshList, 2000);
    },
    [activeConversationId, createConversation, sendMessage, refreshList],
  );

  const handleSelectProject = useCallback((id: string | null) => {
    setActiveProjectId(id);
    setActiveConversationId(null);
  }, []);

  const handleCreateProject = useCallback(
    async (name: string) => {
      const project = await createProject(name);
      setActiveProjectId(project.id);
      setActiveConversationId(null);
    },
    [createProject],
  );

  const handleDeleteProject = useCallback(
    async (id: string) => {
      await deleteProject(id);
      if (id === activeProjectId) {
        setActiveProjectId(null);
        setActiveConversationId(null);
      }
    },
    [deleteProject, activeProjectId],
  );

  const handleRenameProject = useCallback(
    async (id: string, name: string) => {
      await updateProject(id, name);
    },
    [updateProject],
  );

  return (
    <div className="flex h-screen" style={{ background: "var(--bg-primary)" }}>
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        isOpen={sidebar.isOpen}
        onToggle={sidebar.toggle}
        onSelectConversation={setActiveConversationId}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={renameConversation}
        isLoading={isConversationsLoading}
        projects={projects}
        activeProjectId={activeProjectId}
        isProjectsLoading={isProjectsLoading}
        onSelectProject={handleSelectProject}
        onCreateProject={handleCreateProject}
        onDeleteProject={handleDeleteProject}
        onRenameProject={handleRenameProject}
      />

      <div className="flex flex-col flex-1 min-w-0">
        <Header
          isConnected={isConnected}
          onClear={clearChat}
          theme={theme}
          onToggleTheme={toggleTheme}
          isSidebarOpen={sidebar.isOpen}
          onToggleSidebar={sidebar.toggle}
          onNewChat={handleNewChat}
        />

        <main className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          <div className="max-w-4xl mx-auto w-full space-y-4">
            {isHistoryLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="flex items-center gap-2" style={{ color: "var(--text-secondary)" }}>
                  <span className="text-sm">Loading conversation...</span>
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center pt-32">
                <div className="text-4xl mb-4">&#x1f916;</div>
                <h2 className="text-xl font-semibold mb-2" style={{ color: "var(--text-primary)" }}>
                  Agentic AI Chat
                </h2>
                <p className="text-sm max-w-md" style={{ color: "var(--text-secondary)" }}>
                  I can search the web, do calculations, check the time, and take notes.
                  Ask me anything!
                </p>
              </div>
            ) : (
              messages.map((msg) => (
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
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </main>

        <div className="max-w-4xl mx-auto w-full">
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
