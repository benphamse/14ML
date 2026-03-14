import type { ConversationGateway } from "@/domain/ports/ConversationGateway";
import { ConversationSummary } from "@/domain/entities/ConversationSummary";
import { Message } from "@/domain/entities/Message";
import { ToolStep } from "@/domain/entities/ToolStep";
import type {
  ApiConversationResponse,
  ApiConversationListResponse,
  ApiConversationMessagesResponse,
} from "@/application/dto/conversation-api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class HttpConversationGateway implements ConversationGateway {
  async listConversations(
    userId: string,
    limit = 50,
    offset = 0,
    projectId?: string,
  ): Promise<ConversationSummary[]> {
    const params = new URLSearchParams({
      user_id: userId,
      limit: String(limit),
      offset: String(offset),
    });
    if (projectId) params.set("project_id", projectId);
    const res = await fetch(`${API_BASE}/api/conversations?${params}`);
    const data: ApiConversationListResponse = await res.json();
    return data.conversations.map(ConversationSummary.fromServerData);
  }

  async createConversation(
    userId: string,
    title?: string,
    projectId?: string,
  ): Promise<ConversationSummary> {
    const params = new URLSearchParams({ user_id: userId });
    const bodyObj: Record<string, string> = {};
    if (title) bodyObj.title = title;
    if (projectId) bodyObj.project_id = projectId;
    const hasBody = Object.keys(bodyObj).length > 0;
    const res = await fetch(`${API_BASE}/api/conversations?${params}`, {
      method: "POST",
      headers: hasBody ? { "Content-Type": "application/json" } : undefined,
      body: hasBody ? JSON.stringify(bodyObj) : undefined,
    });
    const data: ApiConversationResponse = await res.json();
    return ConversationSummary.fromServerData(data);
  }

  async deleteConversation(id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/api/conversations/${id}`, {
      method: "DELETE",
    });
    return res.ok;
  }

  async renameConversation(
    id: string,
    title: string,
  ): Promise<ConversationSummary> {
    const res = await fetch(`${API_BASE}/api/conversations/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    const data: ApiConversationResponse = await res.json();
    return ConversationSummary.fromServerData(data);
  }

  async getMessages(
    conversationId: string,
    limit = 100,
    offset = 0,
  ): Promise<Message[]> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    const res = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/messages?${params}`,
    );
    const data: ApiConversationMessagesResponse = await res.json();
    return data.messages.map((m) => {
      const toolSteps = (m.tool_steps ?? []).map(ToolStep.fromServerData);
      return new Message(
        m.id,
        m.role as "user" | "assistant",
        m.content,
        toolSteps,
      );
    });
  }
}
