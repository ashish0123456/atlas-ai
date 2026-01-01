from app.llm.client import LLMClient
import json

llm_client = LLMClient()

class PlannerAgent: 

    async def plan(self, question: str) -> list[str]:
        prompt = f"""
You are an AI planner.

Available tools:
- retrieve_documents(query: string, top_k: integer)

Given the user question, decide:
1. Which tool to use
2. What arguments to pass

Respond ONLY in JSON:

{{
  "tool": "<tool_name>",
  "arguments": {{
    "query": "...",
    "top_k": 5
  }}
}}

Question:
{question}
""".strip()
        
        response = await llm_client.generate(prompt)

        return json.loads(response)