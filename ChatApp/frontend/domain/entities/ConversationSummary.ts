import { BaseEntity } from "./BaseEntity";

export class ConversationSummary extends BaseEntity<ConversationSummary> {
  constructor(
    id: string,
    private readonly _title: string,
    private readonly _createdAt: Date,
    private readonly _updatedAt: Date,
  ) {
    super(id);
  }

  get title(): string {
    return this._title;
  }

  get createdAt(): Date {
    return this._createdAt;
  }

  get updatedAt(): Date {
    return this._updatedAt;
  }

  static fromServerData(data: {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
  }): ConversationSummary {
    return new ConversationSummary(
      data.id,
      data.title,
      new Date(data.created_at),
      new Date(data.updated_at),
    );
  }

  withTitle(title: string): ConversationSummary {
    return this.clone({ title });
  }

  protected clone(overrides: { title?: string } = {}): ConversationSummary {
    return new ConversationSummary(
      this.id,
      overrides.title ?? this._title,
      this._createdAt,
      this._updatedAt,
    );
  }
}
