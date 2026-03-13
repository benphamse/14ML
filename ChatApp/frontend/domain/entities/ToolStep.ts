export class ToolStep {
  constructor(
    readonly type: "tool_call" | "tool_result",
    readonly tool: string,
    readonly input?: Record<string, unknown>,
    readonly result?: string
  ) {}

  get displayName(): string {
    return this.tool.replace(/_/g, " ");
  }

  static fromServerData(data: {
    type: "tool_call" | "tool_result";
    tool: string;
    input?: Record<string, unknown>;
    result?: string;
  }): ToolStep {
    return new ToolStep(data.type, data.tool, data.input, data.result);
  }
}
