from abc import ABC, abstractmethod
from typing import Dict, Any

class Tool(ABC):
    """Base class for all tools in the agent system"""
    
    name: str
    description: str
    input_schema: Dict[str, Any]

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """
        Execute the tool with given arguments.
        
        Args:
            **kwargs: Tool-specific arguments
        
        Returns:
            Tool execution result
        """
        pass

    