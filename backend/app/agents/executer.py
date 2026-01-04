from app.tools.registry import get_tool
from app.observability.logger import JsonLogger
from typing import Any

logger = JsonLogger("executor-agent")


class ExecutorAgent:
    """Agent responsible for executing planned tool calls"""

    async def execute(self, plan: dict) -> list[dict]:
        """
        Execute a planned tool call asynchronously.
        
        Args:
            plan: Dictionary with 'tool' and 'arguments' keys
        
        Returns:
            Tool execution results (list of context dictionaries)
        
        Raises:
            ValueError: If plan is invalid or tool not found
            Exception: If tool execution fails
        """
        # Validate plan structure
        if not plan:
            raise ValueError("Plan cannot be empty")
        
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a dictionary")
        
        if 'tool' not in plan:
            raise ValueError("Invalid plan: missing 'tool' key")
        
        if 'arguments' not in plan:
            raise ValueError("Invalid plan: missing 'arguments' key")
        
        tool_name = plan['tool']
        args = plan['arguments']

        if not isinstance(args, dict):
            raise ValueError("Plan arguments must be a dictionary")

        logger.log(
            "INFO",
            "executing_tool",
            tool=tool_name,
            args_keys=list(args.keys()) if args else []
        )

        # Get tool from registry
        tool = get_tool(tool_name)
        if not tool:
            error_msg = f"Tool '{tool_name}' not found in registry"
            logger.log("ERROR", "tool_not_found", tool=tool_name)
            raise ValueError(error_msg)
        
        try:
            # Execute tool (tools may be sync, so we handle both)
            import asyncio
            import inspect
            
            if inspect.iscoroutinefunction(tool.run):
                result = await tool.run(**args)
            else:
                # Run sync tool in thread pool to avoid blocking
                result = await asyncio.to_thread(tool.run, **args)
            
            # Ensure result is a list
            if not isinstance(result, list):
                logger.log("WARN", "tool_result_not_list", tool=tool_name, result_type=type(result).__name__)
                result = [result] if result else []
            
            logger.log(
                "INFO",
                "tool_execution_completed",
                tool=tool_name,
                results_count=len(result)
            )
            
            return result
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.log(
                "ERROR",
                "tool_execution_failed",
                tool=tool_name,
                error=str(e),
                error_type=type(e).__name__
            )
            raise RuntimeError(f"Tool execution failed: {str(e)}") from e