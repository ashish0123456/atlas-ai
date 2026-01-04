from app.llm.client import LLMClient
from app.core.config import settings
from app.observability.logger import JsonLogger
import json
import re

llm_client = LLMClient()
logger = JsonLogger("planner-agent")


class PlannerAgent:
    """Agent responsible for planning tool usage based on user questions"""

    async def plan(self, question: str) -> dict:
        """
        Plan which tool to use and with what arguments.
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with 'tool' and 'arguments' keys
        """
        prompt = f"""You are an AI planner that decides which tools to use.

Available tools:
- retrieve_documents(query: string, top_k: integer): Search for relevant documents

Given the user question, respond ONLY with valid JSON (no markdown, no code blocks):

{{
  "tool": "retrieve_documents",
  "arguments": {{
    "query": "<extract the key search terms from the question>",
    "top_k": {settings.RETRIEVAL_TOP_K}
  }}
}}

Question: {question}

JSON Response:"""

        try:
            response = await llm_client.generate(prompt)
            
            # Clean response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                # Remove markdown code blocks
                response = re.sub(r"^```(?:json)?\s*", "", response, flags=re.MULTILINE)
                response = re.sub(r"```\s*$", "", response, flags=re.MULTILINE)
            
            response = response.strip()
            
            # Parse JSON
            plan = json.loads(response)
            
            # Validate plan structure
            if "tool" not in plan or "arguments" not in plan:
                raise ValueError("Invalid plan structure: missing 'tool' or 'arguments'")
            
            # Ensure top_k is set
            if "top_k" not in plan["arguments"]:
                plan["arguments"]["top_k"] = settings.RETRIEVAL_TOP_K
            
            logger.log("INFO", "plan_created", tool=plan["tool"], query=plan["arguments"].get("query"))
            
            return plan
        
        except json.JSONDecodeError as e:
            logger.log("ERROR", "plan_json_parse_failed", error=str(e), response=response[:200])
            # Fallback to default plan
            return {
                "tool": "retrieve_documents",
                "arguments": {
                    "query": question,
                    "top_k": settings.RETRIEVAL_TOP_K
                }
            }
        except Exception as e:
            logger.log("ERROR", "plan_failed", error=str(e))
            # Fallback to default plan
            return {
                "tool": "retrieve_documents",
                "arguments": {
                    "query": question,
                    "top_k": settings.RETRIEVAL_TOP_K
                }
            }