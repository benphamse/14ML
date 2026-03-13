export interface WsToolCall {
  type: "tool_call";
  tool: string;
  input: Record<string, unknown>;
}

export interface WsToolResult {
  type: "tool_result";
  tool: string;
  result: string;
}

export interface WsStream {
  type: "stream";
  content: string;
}

export interface WsReply {
  type: "reply";
  content: string;
}

export interface WsError {
  type: "error";
  message: string;
}

export interface WsStatus {
  type: "status";
  content: string;
}

export interface WsCleared {
  type: "cleared";
}

export type WsServerMessage =
  | WsToolCall
  | WsToolResult
  | WsStream
  | WsReply
  | WsError
  | WsStatus
  | WsCleared;
