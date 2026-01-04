from app.llm.client import LLMClient
from app.observability.logger import JsonLogger

llm_client = LLMClient()
logger = JsonLogger("verifier-agent")


class VerifierAgent:
    """Agent responsible for generating final answers from retrieved contexts"""

    async def verify(self, question: str, contexts: list[dict]) -> str:
        """
        Generate answer from retrieved contexts with verification focus.
        
        Args:
            question: User's question
            contexts: List of retrieved context dictionaries with 'content' key
        
        Returns:
            Generated answer string
        """
        if not contexts:
            return "I don't have enough information to answer this question. Please upload relevant documents first."
        
        # Extract content from contexts (handle both 'content' and 'context' keys for compatibility)
        context_list = []
        for c in contexts:
            content = c.get("content") or c.get("context", "")
            if content:
                context_list.append({"content": content})
        
        if not context_list:
            return "I don't have enough information to answer this question."
        
        # Build verification-focused prompt
        context_text = "\n\n".join(
            f"[Context {i+1}]: {c['content']}" 
            for i, c in enumerate(context_list)
        )
        
        prompt = f"""You are a verification agent that answers questions based ONLY on the provided context.

Your role is to:
1. Verify that the answer can be derived from the given context
2. Provide accurate, factual answers based solely on the context
3. Clearly state when the context is insufficient

Context:
{context_text}

Question: {question}

Instructions:
- Answer the question using ONLY information from the context above
- If the answer cannot be found in the context, respond with "I don't have enough information in the provided documents to answer this question."
- Be precise and cite relevant parts of the context when possible
- Do not make assumptions or use knowledge outside the provided context

Answer:"""

        try:
            answer = await llm_client.generate(prompt)
            logger.log("INFO", "verification_completed", question_length=len(question), contexts_count=len(context_list))
            return answer.strip()
        except Exception as e:
            logger.log("ERROR", "verification_failed", error=str(e))
            return "I encountered an error while generating a response. Please try again."