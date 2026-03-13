export abstract class BaseEntity<T extends BaseEntity<T>> {
  constructor(readonly id: string) {}

  equals(other: T): boolean {
    return this.id === other.id;
  }

  protected abstract clone(overrides?: Partial<Record<string, unknown>>): T;

  protected static generateId(): string {
    return crypto.randomUUID();
  }
}
