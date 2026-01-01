import httpx
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"

class LLMClient:
    def __init__(self, model:str = "phi-3"):
        self.model = model

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload
            )

        response.raise_for_status()
        data = response.json()
        return data["response"]