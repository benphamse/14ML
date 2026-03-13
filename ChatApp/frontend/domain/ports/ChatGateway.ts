export interface ChatGateway {
  connect(conversationId: string): void;
  disconnect(): void;
  send(message: object): void;
  onMessage(handler: (data: Record<string, unknown>) => void): void;
  onConnectionChange(handler: (connected: boolean) => void): void;
}
