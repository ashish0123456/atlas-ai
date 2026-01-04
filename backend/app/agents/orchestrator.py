from app.agents.planner import PlannerAgent
from app.agents.executer import ExecutorAgent
from app.agents.verifier import VerifierAgent
from app.agents.evaluator import EvaluatorAgent
from app.observability.logger import JsonLogger
from app.observability.timing import measure_latency
from typing import Optional, Callable

planner = PlannerAgent()
executor = ExecutorAgent()
verifier = VerifierAgent()
evaluator = EvaluatorAgent()

logger = JsonLogger("agent-orchestrator")

# Feedback loop configuration
MAX_ITERATIONS = 3
MIN_QUALITY_THRESHOLD = 0.6


class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow:
    1. Planner: Determines which tools to use
    2. Executor: Executes the planned tools
    3. Verifier: Generates final answer from retrieved contexts
    """

    async def run(
        self, 
        question: str, 
        trace_id: str | None = None,
        progress_callback: Optional[Callable[[str, str, dict], None]] = None
    ) -> dict:
        """
        Execute the complete multi-agent workflow with feedback loop.
        
        Flow:
        1. Plan → Execute → Verify → Evaluate
        2. If quality is low and iterations < max: Refine → Execute → Verify → Evaluate
        3. Repeat until quality threshold met or max iterations reached
        
        Args:
            question: User's question
            trace_id: Optional trace ID for request tracking
        
        Returns:
            Dictionary with answer, contexts, confidence, and quality_score
        
        Raises:
            ValueError: If question is invalid
            RuntimeError: If workflow execution fails
        """
        # Validate input
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        # Emit progress: starting
        if progress_callback:
            progress_callback("starting", "Initializing query processing...", {"question": question[:100]})

        logger.log(
            "INFO",
            "agent_workflow_started",
            trace_id=trace_id,
            question_length=len(question),
            max_iterations=MAX_ITERATIONS
        )

        best_answer = None
        best_contexts = []
        best_quality = 0.0
        current_question = question
        all_contexts = []

        try:
            for iteration in range(MAX_ITERATIONS):
                if iteration > 0 and progress_callback:
                    progress_callback(
                        "refining",
                        f"Refining search (iteration {iteration + 1}/{MAX_ITERATIONS})...",
                        {"iteration": iteration + 1}
                    )

                logger.log(
                    "INFO",
                    "iteration_started",
                    trace_id=trace_id,
                    iteration=iteration + 1,
                    max_iterations=MAX_ITERATIONS
                )

                # Phase 1: Planning
                if progress_callback:
                    progress_callback("planning", "Creating execution plan...", {"iteration": iteration + 1})
                
                with measure_latency() as elapsed:
                    plan = await planner.plan(current_question)

                logger.log(
                    "INFO",
                    "planning_completed",
                    trace_id=trace_id,
                    iteration=iteration + 1,
                    tool=plan.get("tool"),
                    latency_ms=round(elapsed() * 1000, 2)
                )

                # Validate plan
                if not plan or "tool" not in plan or "arguments" not in plan:
                    raise ValueError("Invalid plan returned from planner")

                # Phase 2: Execution
                if progress_callback:
                    progress_callback("retrieving", "Retrieving relevant document contexts...", {"iteration": iteration + 1})
                
                with measure_latency() as elapsed:
                    contexts = await executor.execute(plan)
                
                if progress_callback:
                    progress_callback(
                        "retrieving",
                        f"Retrieved {len(contexts)} context chunks",
                        {"contexts_count": len(contexts), "iteration": iteration + 1}
                    )

                logger.log(
                    "INFO",
                    "execution_completed",
                    trace_id=trace_id,
                    iteration=iteration + 1,
                    contexts_count=len(contexts) if contexts else 0,
                    latency_ms=round(elapsed() * 1000, 2)
                )

                # Validate contexts
                if not contexts:
                    if iteration == 0:
                        # First iteration with no contexts - return early
                        logger.log(
                            "WARN",
                            "no_contexts_retrieved",
                            trace_id=trace_id,
                            iteration=iteration + 1
                        )
                        return {
                            "answer": "I couldn't find any relevant information in the uploaded documents to answer this question. Please ensure relevant documents are uploaded.",
                            "contexts": [],
                            "confidence": 0.0,
                            "quality_score": 0.0
                        }
                    else:
                        # Later iteration with no contexts - use previous best
                        logger.log(
                            "WARN",
                            "no_contexts_in_refinement",
                            trace_id=trace_id,
                            iteration=iteration + 1
                        )
                        break

                # Accumulate contexts
                all_contexts.extend(contexts)

                # Phase 3: Verification/Answer Generation
                if progress_callback:
                    progress_callback("verifying", "Generating answer from contexts...", {"iteration": iteration + 1})
                
                with measure_latency() as elapsed:
                    answer = await verifier.verify(current_question, contexts)

                logger.log(
                    "INFO",
                    "verification_completed",
                    trace_id=trace_id,
                    iteration=iteration + 1,
                    answer_length=len(answer) if answer else 0,
                    latency_ms=round(elapsed() * 1000, 2)
                )

                # Phase 4: Evaluation
                if progress_callback:
                    progress_callback("evaluating", "Assessing answer quality...", {"iteration": iteration + 1})
                
                with measure_latency() as elapsed:
                    evaluation = await evaluator.evaluate(
                        question, 
                        answer, 
                        contexts,
                        iteration=iteration
                    )
                
                if progress_callback:
                    progress_callback(
                        "evaluating",
                        f"Quality score: {evaluation['quality_score']:.2f}",
                        {"quality_score": evaluation["quality_score"], "iteration": iteration + 1}
                    )

                quality_score = evaluation["quality_score"]
                needs_refinement = evaluation["needs_refinement"]

                logger.log(
                    "INFO",
                    "evaluation_completed",
                    trace_id=trace_id,
                    iteration=iteration + 1,
                    quality_score=quality_score,
                    needs_refinement=needs_refinement,
                    latency_ms=round(elapsed() * 1000, 2)
                )

                # Track best answer so far
                if quality_score > best_quality:
                    best_quality = quality_score
                    best_answer = answer
                    best_contexts = all_contexts.copy()

                # Check if we should continue refining
                if not needs_refinement or quality_score >= MIN_QUALITY_THRESHOLD:
                    logger.log(
                        "INFO",
                        "quality_threshold_met",
                        trace_id=trace_id,
                        iteration=iteration + 1,
                        quality_score=quality_score,
                        threshold=MIN_QUALITY_THRESHOLD
                    )
                    break

                # Refine query for next iteration
                if evaluation.get("suggested_query_improvement"):
                    current_question = evaluation["suggested_query_improvement"]
                    logger.log(
                        "INFO",
                        "refining_query",
                        trace_id=trace_id,
                        iteration=iteration + 1,
                        new_query=current_question[:100]
                    )
                else:
                    # Use original question with emphasis
                    current_question = f"{question} (searching for more specific information)"

            # Calculate final confidence (combination of quality and context count)
            context_confidence = min(1.0, len(best_contexts) / 5.0) if best_contexts else 0.0
            final_confidence = (best_quality * 0.7) + (context_confidence * 0.3)

            result = {
                "answer": best_answer or "I couldn't generate an answer. Please try again.",
                "contexts": best_contexts,
                "confidence": round(final_confidence, 2),
                "quality_score": best_quality
            }

            logger.log(
                "INFO",
                "agent_workflow_completed",
                trace_id=trace_id,
                final_confidence=final_confidence,
                quality_score=best_quality,
                iterations_used=min(iteration + 1, MAX_ITERATIONS)
            )

            # Emit progress: complete
            if progress_callback:
                progress_callback(
                    "complete",
                    "Answer ready!",
                    {
                        "confidence": final_confidence,
                        "quality_score": best_quality,
                        "contexts_count": len(best_contexts)
                    }
                )

            return result

        except ValueError as e:
            logger.log("ERROR", "workflow_validation_error", trace_id=trace_id, error=str(e))
            raise
        except Exception as e:
            logger.log(
                "ERROR",
                "agent_workflow_failed",
                trace_id=trace_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise RuntimeError(f"Agent workflow failed: {str(e)}") from e