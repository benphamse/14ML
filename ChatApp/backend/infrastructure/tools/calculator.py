import math

from infrastructure.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    _name = "calculator"
    _description = "Evaluate a mathematical expression. Supports basic arithmetic, powers, roots, etc."
    _parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate, e.g. '2 + 2', 'sqrt(16)', '2**10'",
            },
        },
        "required": ["expression"],
    }

    async def execute(self, args: dict) -> dict:
        expression = args.get("expression", "")
        try:
            allowed = {
                k: v for k, v in math.__dict__.items() if not k.startswith("_")
            }
            allowed["abs"] = abs
            allowed["round"] = round
            result = eval(expression, {"__builtins__": {}}, allowed)
            return self.format_success(expression=expression, result=str(result))
        except Exception as e:
            return self.format_error(f"Could not evaluate: {e}")
