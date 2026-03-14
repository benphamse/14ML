export interface ApiConversationResponse {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ApiConversationListResponse {
  conversations: ApiConversationResponse[];
}

export interface ApiMessageResponse {
  id: string;
  role: string;
  content: string;
  tool_steps: Array<{
    type: "tool_call" | "tool_result";
    tool: string;
    input?: Record<string, unknown>;
    result?: string;
  }> | null;
  created_at: string;
}

export interface ApiConversationMessagesResponse {
  messages: ApiMessageResponse[];
}
