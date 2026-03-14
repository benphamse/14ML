import type { ConversationGateway } from "@/domain/ports/ConversationGateway";
import { ConversationSummary } from "@/domain/entities/ConversationSummary";
import { Message } from "@/domain/entities/Message";
import { ToolStep } from "@/domain/entities/ToolStep";
import type {
  ApiConversationResponse,
  ApiConversationListResponse,
  ApiConversationMessagesResponse,
} from "@/application/dto/conversation-api";
import apiClient from "./apiClient";

export class HttpConversationGateway implements ConversationGateway {
  async listConversations(
    userId: string,
    limit = 50,
    offset = 0,
    projectId?: string,
  ): Promise<ConversationSummary[]> {
    const { data } = await apiClient.get<ApiConversationListResponse>("/api/conversations", {
      params: { user_id: userId, limit, offset, ...(projectId && { project_id: projectId }) },
    });
    return data.conversations.map(ConversationSummary.fromServerData);
  }

  async createConversation(
    userId: string,
    title?: string,
    projectId?: string,
  ): Promise<ConversationSummary> {
    const { data } = await apiClient.post<ApiConversationResponse>(
      "/api/conversations",
      { ...(title && { title }), ...(projectId && { project_id: projectId }) },
      { params: { user_id: userId } },
    );
    return ConversationSummary.fromServerData(data);
  }

  async deleteConversation(id: string): Promise<boolean> {
    await apiClient.delete(`/api/conversations/${id}`);
    return true;
  }

  async renameConversation(id: string, title: string): Promise<ConversationSummary> {
    const { data } = await apiClient.patch<ApiConversationResponse>(
      `/api/conversations/${id}`,
      { title },
    );
    return ConversationSummary.fromServerData(data);
  }

  async getMessages(
    conversationId: string,
    limit = 100,
    offset = 0,
  ): Promise<Message[]> {
    const { data } = await apiClient.get<ApiConversationMessagesResponse>(
      `/api/conversations/${conversationId}/messages`,
      { params: { limit, offset } },
    );
    return data.messages.map((m) => {
      const toolSteps = (m.tool_steps ?? []).map(ToolStep.fromServerData);
      return new Message(m.id, m.role as "user" | "assistant", m.content, toolSteps);
    });
  }
}
