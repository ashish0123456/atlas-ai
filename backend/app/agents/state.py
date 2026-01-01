from typing import List, Dict, Any

class AgentState:
    def __init__(self, question: str):
        self.question = question
        self.tasks: List[str] = []
        self.contexts: List[Dict[str, Any]] = []
        self.answer: str | None = None
        