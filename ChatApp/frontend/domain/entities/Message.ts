import { BaseEntity } from "./BaseEntity";
import { ToolStep } from "./ToolStep";

export class Message extends BaseEntity<Message> {
  constructor(
    id: string,
    readonly role: "user" | "assistant",
    private readonly _content: string,
    private readonly _toolSteps: ToolStep[] = []
  ) {
    super(id);
  }

  get content(): string {
    return this._content;
  }

  get toolSteps(): ToolStep[] {
    return [...this._toolSteps];
  }

  static createUser(content: string): Message {
    return new Message(BaseEntity.generateId(), "user", content);
  }

  static createAssistantPlaceholder(): Message {
    return new Message(BaseEntity.generateId(), "assistant", "", []);
  }

  withContent(content: string): Message {
    return this.clone({ content });
  }

  withAppendedContent(chunk: string): Message {
    return this.clone({ content: this._content + chunk });
  }

  withToolStep(step: ToolStep): Message {
    return this.clone({ toolSteps: [...this._toolSteps, step] });
  }

  withToolSteps(steps: ToolStep[]): Message {
    return this.clone({ toolSteps: [...steps] });
  }

  protected clone(overrides: { content?: string; toolSteps?: ToolStep[] } = {}): Message {
    return new Message(
      this.id,
      this.role,
      overrides.content ?? this._content,
      overrides.toolSteps ?? this._toolSteps,
    );
  }
}
