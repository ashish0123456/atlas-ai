from app.tools.retrieval import RetrievalTool

TOOLS = {
    RetrievalTool.name : RetrievalTool()
}

def get_tool(name: str):
    return TOOLS.get(name)