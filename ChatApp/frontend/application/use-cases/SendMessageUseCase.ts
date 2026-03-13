import { BaseUseCase } from "./BaseUseCase";

export class SendMessageUseCase extends BaseUseCase<string, void> {
  execute(content: string): void {
    this.gateway.send({ type: "message", content });
  }
}
