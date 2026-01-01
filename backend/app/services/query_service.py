from app.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

class QueryService: 

    async def process_query(self, question: str, trace_id: str):
        return await orchestrator.run(question, trace_id)
