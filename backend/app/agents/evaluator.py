from app.llm.client import LLMClient
from app.observability.logger import JsonLogger
from typing import Dict, Any

llm_client = LLMClient()
logger = JsonLogger("evaluator-agent")


class EvaluatorAgent:
    """Agent responsible for evaluating answer quality and determining if refinement is needed"""

    async def evaluate(
        self, 
        question: str, 
        answer: str, 
        contexts: list[dict],
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of the generated answer.
        
        Args:
            question: Original user question
            answer: Generated answer
            contexts: Retrieved contexts used for answer
            iteration: Current iteration number
        
        Returns:
            Dictionary with:
            - quality_score: float (0.0 to 1.0)
            - needs_refinement: bool
            - feedback: str (reasoning for the evaluation)
        """
        if not answer or not answer.strip():
            return {
                "quality_score": 0.0,
                "needs_refinement": True,
                "feedback": "Answer is empty"
            }

        # Check if answer indicates insufficient information
        insufficient_indicators = [
            "i don't know",
            "i don't have enough",
            "cannot find",
            "not in the provided",
            "insufficient information"
        ]
        
        answer_lower = answer.lower()
        if any(indicator in answer_lower for indicator in insufficient_indicators):
            return {
                "quality_score": 0.2,
                "needs_refinement": True,
                "feedback": "Answer indicates insufficient information"
            }

        # Use LLM to evaluate answer quality
        context_count = len(contexts) if contexts else 0
        context_summary = f"{context_count} context chunks retrieved"
        
        evaluation_prompt = f"""You are an answer quality evaluator. Evaluate if the answer adequately addresses the question based on the retrieved contexts.

Question: {question}

Answer: {answer}

Context Information: {context_summary}

Evaluate:
1. Does the answer directly address the question? (Yes/No)
2. Is the answer based on the provided contexts? (Yes/No/Uncertain)
3. Is the answer complete and informative? (Yes/No/Partial)
4. Would retrieving more or different contexts improve the answer? (Yes/No)

Respond in JSON format:
{{
  "quality_score": <0.0 to 1.0>,
  "needs_refinement": <true/false>,
  "feedback": "<brief explanation>",
  "suggested_query_improvement": "<if needs_refinement is true, suggest better search query>"
}}

JSON Response:"""

        try:
            response = await llm_client.generate(evaluation_prompt)
            
            # Clean and parse JSON response
            import json
            import re
            
            response = response.strip()
            if response.startswith("```"):
                response = re.sub(r"^```(?:json)?\s*", "", response, flags=re.MULTILINE)
                response = re.sub(r"```\s*$", "", response, flags=re.MULTILINE)
            
            evaluation = json.loads(response.strip())
            
            # Validate and normalize
            quality_score = float(evaluation.get("quality_score", 0.5))
            quality_score = max(0.0, min(1.0, quality_score))  # Clamp to [0, 1]
            
            needs_refinement = evaluation.get("needs_refinement", False)
            
            # Don't refine if we've already tried multiple times
            if iteration >= 2:
                needs_refinement = False
                logger.log(
                    "INFO",
                    "max_iterations_reached",
                    iteration=iteration,
                    quality_score=quality_score
                )
            
            result = {
                "quality_score": round(quality_score, 2),
                "needs_refinement": needs_refinement and iteration < 2,
                "feedback": evaluation.get("feedback", "No feedback provided"),
                "suggested_query_improvement": evaluation.get("suggested_query_improvement")
            }
            
            logger.log(
                "INFO",
                "evaluation_completed",
                quality_score=quality_score,
                needs_refinement=needs_refinement,
                iteration=iteration
            )
            
            return result
            
        except Exception as e:
            logger.log("ERROR", "evaluation_failed", error=str(e))
            # Default to moderate quality, no refinement on error
            return {
                "quality_score": 0.5,
                "needs_refinement": False,
                "feedback": f"Evaluation failed: {str(e)}"
            }

