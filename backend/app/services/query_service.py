from app.agents.orchestrator import AgentOrchestrator
from app.observability.logger import JsonLogger
from app.schemas.query import QueryResponse
from typing import Callable, Optional
import asyncio

orchestrator = AgentOrchestrator()
logger = JsonLogger("query-service")

# Query timeout in seconds (5 minutes)
QUERY_TIMEOUT = 1000


class QueryService:
    """Service for processing user queries through the agent workflow"""

    async def process_query(
        self, 
        question: str, 
        trace_id: str | None = None,
        progress_callback: Optional[Callable[[str, str, dict], None]] = None
    ) -> QueryResponse:
        """
        Process a query through the multi-agent workflow.
        
        Args:
            question: User's question
            trace_id: Optional trace ID for request tracking
            progress_callback: Optional callback for progress updates (stage, message, data)
        
        Returns:
            QueryResponse with answer, contexts, and confidence
        
        Raises:
            TimeoutError: If query processing exceeds timeout
            Exception: For other processing errors
        """
        logger.log(
            "INFO",
            "query_processing_started",
            trace_id=trace_id,
            question_length=len(question)
        )

        try:
            # Run orchestrator with timeout and progress callback
            result = await asyncio.wait_for(
                orchestrator.run(question, trace_id, progress_callback),
                timeout=QUERY_TIMEOUT
            )

            # Ensure result is properly formatted
            if isinstance(result, dict):
                response = QueryResponse(**result)
            else:
                response = result

            logger.log(
                "INFO",
                "query_processing_completed",
                trace_id=trace_id,
                answer_length=len(response.answer) if response.answer else 0,
                contexts_count=len(response.contexts) if response.contexts else 0
            )

            return response

        except asyncio.TimeoutError:
            logger.log(
                "ERROR",
                "query_timeout",
                trace_id=trace_id,
                timeout=QUERY_TIMEOUT
            )
            raise TimeoutError(f"Query processing exceeded timeout of {QUERY_TIMEOUT} seconds")
        
        except Exception as e:
            logger.log(
                "ERROR",
                "query_processing_failed",
                trace_id=trace_id,
                error=str(e)
            )
            raise
