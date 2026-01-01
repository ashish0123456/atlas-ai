def build_rag_prompt(question: str, contexts: list[dict]) -> str:
    context_text = "\n\n".join(
        f"- {c['content']}" for c in contexts
    )

    return f"""
You are an AI assistant answering questions based ONLY on the provided context.

Context:
{context_text}

Question:
{question}

Rules:
- Use only the context above
- If the answer is not in the context, say "I don't know"
- Be concise and factual

Answer: 
""".strip()