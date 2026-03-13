import { ChatGateway } from "@/domain/ports/ChatGateway";

const WS_URL = "ws://localhost:8000/ws/chat";
const RECONNECT_DELAY_MS = 3000;

export class WebSocketChatGateway implements ChatGateway {
  private ws: WebSocket | null = null;
  private messageHandler: ((data: Record<string, unknown>) => void) | null = null;
  private connectionHandler: ((connected: boolean) => void) | null = null;
  private shouldReconnect = true;

  connect(): void {
    this.shouldReconnect = true;
    this.createConnection();
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.ws?.close();
    this.ws = null;
  }

  send(message: object): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  onMessage(handler: (data: Record<string, unknown>) => void): void {
    this.messageHandler = handler;
  }

  onConnectionChange(handler: (connected: boolean) => void): void {
    this.connectionHandler = handler;
  }

  private createConnection(): void {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      this.connectionHandler?.(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.messageHandler?.(data);
    };

    ws.onclose = () => {
      this.connectionHandler?.(false);
      if (this.shouldReconnect) {
        setTimeout(() => this.createConnection(), RECONNECT_DELAY_MS);
      }
    };

    ws.onerror = () => {
      this.connectionHandler?.(false);
    };

    this.ws = ws;
  }
}
