import { useState, useRef, useEffect, useCallback } from "react";

import { Conversation } from "@/domain/entities/Conversation";
import { ToolStep } from "@/domain/entities/ToolStep";
import { SendMessageUseCase } from "@/application/use-cases/SendMessageUseCase";
import { ClearChatUseCase } from "@/application/use-cases/ClearChatUseCase";
import { WebSocketChatGateway } from "@/infrastructure/websocket/WebSocketChatGateway";
import type { WsServerMessage } from "@/application/dto/ws-messages";

export function useChat() {
  const [conversation, setConversation] = useState(new Conversation());
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const gatewayRef = useRef<WebSocketChatGateway | null>(null);
  const sendMessageRef = useRef<SendMessageUseCase | null>(null);
  const clearChatRef = useRef<ClearChatUseCase | null>(null);
  const pendingToolSteps = useRef<ToolStep[]>([]);
  const streamedContent = useRef("");

  const handleMessage = useCallback((raw: Record<string, unknown>) => {
    const data = raw as unknown as WsServerMessage;

    if (data.type === "tool_call" || data.type === "tool_result") {
      const step = ToolStep.fromServerData(data as {
        type: "tool_call" | "tool_result";
        tool: string;
        input?: Record<string, unknown>;
        result?: string;
      });
      pendingToolSteps.current.push(step);
      const steps = [...pendingToolSteps.current];
      setConversation((prev) =>
        prev.updateLastAssistant((msg) => msg.withToolSteps(steps))
      );
    } else if (data.type === "stream") {
      streamedContent.current += data.content;
      const currentContent = streamedContent.current;
      setConversation((prev) =>
        prev.updateLastAssistant((msg) => msg.withContent(currentContent))
      );
    } else if (data.type === "reply") {
      setIsLoading(false);
      const finalContent = data.content;
      const steps = [...pendingToolSteps.current];
      setConversation((prev) =>
        prev.updateLastAssistant((msg) =>
          msg.withContent(finalContent).withToolSteps(steps)
        )
      );
      pendingToolSteps.current = [];
      streamedContent.current = "";
    } else if (data.type === "status") {
      setConversation((prev) =>
        prev.updateLastAssistant((msg) => msg.withContent(data.content))
      );
    } else if (data.type === "error") {
      setIsLoading(false);
      const errorMsg = `Error: ${data.message}`;
      setConversation((prev) =>
        prev.updateLastAssistant((msg) => msg.withContent(errorMsg))
      );
      pendingToolSteps.current = [];
      streamedContent.current = "";
    } else if (data.type === "cleared") {
      setConversation(new Conversation());
    }
  }, []);

  useEffect(() => {
    const gateway = new WebSocketChatGateway();
    gatewayRef.current = gateway;
    sendMessageRef.current = new SendMessageUseCase(gateway);
    clearChatRef.current = new ClearChatUseCase(gateway);

    gateway.onConnectionChange(setIsConnected);
    gateway.onMessage(handleMessage);
    gateway.connect();

    return () => {
      gateway.disconnect();
    };
  }, [handleMessage]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!content.trim() || isLoading) return;

      setConversation((prev) => prev.addUserMessage(content));
      setIsLoading(true);
      pendingToolSteps.current = [];
      streamedContent.current = "";

      sendMessageRef.current?.execute(content);
    },
    [isLoading]
  );

  const clearChat = useCallback(() => {
    clearChatRef.current?.execute();
    setConversation(new Conversation());
  }, []);

  return {
    messages: conversation.messages,
    isLoading,
    isConnected,
    sendMessage,
    clearChat,
  };
}
