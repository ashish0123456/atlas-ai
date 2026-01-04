import httpx
from app.core.config import settings
from app.observability.logger import JsonLogger

logger = JsonLogger("llm-client")


class LLMClient:
    def __init__(self, model: str = None):
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_URL

    async def generate(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt
            max_retries: Maximum number of retry attempts
        
        Returns:
            Generated text response
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if "response" not in data:
                        raise ValueError("Invalid response format from LLM")
                    
                    return data["response"].strip()
            
            except httpx.TimeoutException as e:
                last_error = e
                logger.log(
                    "WARN",
                    "llm_timeout",
                    attempt=attempt + 1,
                    model=self.model,
                    error=str(e)
                )
                if attempt == max_retries - 1:
                    raise
            
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.log(
                    "ERROR",
                    "llm_http_error",
                    attempt=attempt + 1,
                    status_code=e.response.status_code,
                    error=str(e)
                )
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise
                if attempt == max_retries - 1:
                    raise
            
            except Exception as e:
                last_error = e
                logger.log(
                    "ERROR",
                    "llm_error",
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt == max_retries - 1:
                    raise
        
        # Should not reach here, but just in case
        raise Exception(f"Failed to generate response after {max_retries} attempts: {last_error}")