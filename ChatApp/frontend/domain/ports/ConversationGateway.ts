import type { ConversationSummary } from "@/domain/entities/ConversationSummary";
import type { Message } from "@/domain/entities/Message";

export interface ConversationGateway {
  listConversations(userId: string, limit?: number, offset?: number, projectId?: string): Promise<ConversationSummary[]>;
  createConversation(userId: string, title?: string, projectId?: string): Promise<ConversationSummary>;
  deleteConversation(id: string): Promise<boolean>;
  renameConversation(id: string, title: string): Promise<ConversationSummary>;
  getMessages(conversationId: string, limit?: number, offset?: number): Promise<Message[]>;
}
