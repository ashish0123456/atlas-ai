from abc import ABC, abstractmethod
from typing import Dict, Any

class Tool(ABC):
    name: str
    description: str
    input_schema: Dict[str, Any]

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass

    