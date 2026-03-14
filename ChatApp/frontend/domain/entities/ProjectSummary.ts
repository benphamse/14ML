import { BaseEntity } from "./BaseEntity";

export class ProjectSummary extends BaseEntity<ProjectSummary> {
  constructor(
    id: string,
    private readonly _name: string,
    private readonly _description: string,
    private readonly _createdAt: Date,
    private readonly _updatedAt: Date,
  ) {
    super(id);
  }

  get name(): string {
    return this._name;
  }

  get description(): string {
    return this._description;
  }

  get createdAt(): Date {
    return this._createdAt;
  }

  get updatedAt(): Date {
    return this._updatedAt;
  }

  static fromServerData(data: {
    id: string;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
  }): ProjectSummary {
    return new ProjectSummary(
      data.id,
      data.name,
      data.description,
      new Date(data.created_at),
      new Date(data.updated_at),
    );
  }

  withName(name: string): ProjectSummary {
    return this.clone({ name });
  }

  protected clone(overrides: { name?: string; description?: string } = {}): ProjectSummary {
    return new ProjectSummary(
      this.id,
      overrides.name ?? this._name,
      overrides.description ?? this._description,
      this._createdAt,
      this._updatedAt,
    );
  }
}
