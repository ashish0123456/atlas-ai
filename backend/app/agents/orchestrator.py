from app.agents.state import AgentState
from app.agents.planner import PlannerAgent
from app.agents.executer import ExecutorAgent
from app.agents.verifier import VerifierAgent
from app.observability.logger import JsonLogger
from app.observability.timing import measure_latency

planner = PlannerAgent()
executor = ExecutorAgent()
verifier = VerifierAgent()

logger = JsonLogger("agent-orchestrator")

class AgentOrchestrator:

    async def run(self, question: str, trace_id: str | None = None) -> AgentState:
        logger.log(
            "INFO",
            "agent_run_started",
            trace_id=trace_id,
            question=question
        )
        
        state = AgentState(question)

        with measure_latency() as elapsed:
            plan = await planner.plan(question)

        logger.log(
            "INFO",
            "planning_completed",
            trace_id=trace_id,
            plan=plan,
            latency=elapsed()
        )

        with measure_latency() as elapsed:
            contexts = executor.execute(plan)

        logger.log(
            "INFO",
            "execution_completed",
            trace_id=trace_id,
            contexts_count=len(contexts),
            latency=elapsed()
        )

        with measure_latency() as elapsed:
            answer = await verifier.verify(question, contexts)

        logger.log(
            "INFO",
            "verification_completed",
            trace_id=trace_id,
            latency=elapsed()
        )

        return {
            "answer": answer,
            "contexts": contexts
        }