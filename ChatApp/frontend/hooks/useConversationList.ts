import { useState, useRef, useEffect, useCallback } from "react";

import { ConversationSummary } from "@/domain/entities/ConversationSummary";
import { HttpConversationGateway } from "@/infrastructure/http/HttpConversationGateway";

const USER_ID = "default";

export function useConversationList(projectId: string | null = null) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const gatewayRef = useRef(new HttpConversationGateway());

  const loadConversations = useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await gatewayRef.current.listConversations(
        USER_ID,
        50,
        0,
        projectId ?? undefined,
      );
      setConversations(list);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const createConversation = useCallback(async (): Promise<ConversationSummary> => {
    const created = await gatewayRef.current.createConversation(
      USER_ID,
      undefined,
      projectId ?? undefined,
    );
    setConversations((prev) => [created, ...prev]);
    return created;
  }, [projectId]);

  const deleteConversation = useCallback(async (id: string) => {
    await gatewayRef.current.deleteConversation(id);
    setConversations((prev) => prev.filter((c) => c.id !== id));
  }, []);

  const renameConversation = useCallback(async (id: string, title: string) => {
    const updated = await gatewayRef.current.renameConversation(id, title);
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? updated : c)),
    );
  }, []);

  const refreshList = useCallback(() => {
    loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    isLoading,
    createConversation,
    deleteConversation,
    renameConversation,
    refreshList,
  };
}
