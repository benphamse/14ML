import { ChatGateway } from "@/domain/ports/ChatGateway";

export interface UseCase<TInput = void, TOutput = void> {
  execute(input: TInput): TOutput;
}

export abstract class BaseUseCase<TInput = void, TOutput = void>
  implements UseCase<TInput, TOutput>
{
  constructor(protected readonly gateway: ChatGateway) {}

  abstract execute(input: TInput): TOutput;
}
