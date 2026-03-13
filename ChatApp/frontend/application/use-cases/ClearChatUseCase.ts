import { BaseUseCase } from "./BaseUseCase";

export class ClearChatUseCase extends BaseUseCase {
  execute(): void {
    this.gateway.send({ type: "clear" });
  }
}
