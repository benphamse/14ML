import { BaseEntity } from "./BaseEntity";
import { Message } from "./Message";

export class Conversation extends BaseEntity<Conversation> {
  constructor(
    id: string = BaseEntity.generateId(),
    private readonly _messages: Message[] = [],
  ) {
    super(id);
  }

  get messages(): Message[] {
    return [...this._messages];
  }

  get length(): number {
    return this._messages.length;
  }

  addUserMessage(content: string): Conversation {
    const userMsg = Message.createUser(content);
    const placeholder = Message.createAssistantPlaceholder();
    return this.clone({ messages: [...this._messages, userMsg, placeholder] });
  }

  updateLastAssistant(updater: (msg: Message) => Message): Conversation {
    if (this._messages.length === 0) return this;
    const last = this._messages[this._messages.length - 1];
    if (last.role !== "assistant") return this;
    const updated = updater(last);
    return this.clone({ messages: [...this._messages.slice(0, -1), updated] });
  }

  clear(): Conversation {
    return new Conversation();
  }

  protected clone(overrides: { messages?: Message[] } = {}): Conversation {
    return new Conversation(
      this.id,
      overrides.messages ?? this._messages,
    );
  }
}
