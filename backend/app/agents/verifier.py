from app.llm.client import LLMClient    

llm_client = LLMClient()

class VerifierAgent:

    async def verify(self, question: str, contexts: list[dict]) -> str:
        context_text = "\n".join(c["context"] for c in contexts)

        prompt = f"""
You are a verification agent.
Using the context below, answer the question accurately.

Context:
{context_text}

Question:
{question}

If context is insufficient, say "I don't know".
""".strip()
        
        return await llm_client.generate(prompt)