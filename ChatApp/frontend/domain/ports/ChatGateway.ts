export interface ChatGateway {
  connect(): void;
  disconnect(): void;
  send(message: object): void;
  onMessage(handler: (data: Record<string, unknown>) => void): void;
  onConnectionChange(handler: (connected: boolean) => void): void;
}
