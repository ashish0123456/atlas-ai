from app.tools.registry import get_tool

class ExecutorAgent:

    def execute(self, plan: dict):
        tool_name = plan['tool']
        args = plan['arguments']

        tool = get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        return tool.run(**args)