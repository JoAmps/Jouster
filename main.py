from fastapi import FastAPI, HTTPException
import uvicorn
import uuid
from langgraph.types import Command
from data.postgres_db import PostgreSQL
from graph_builder.build_graph import build_ad_graph
from llm_models.llm import LLMHandler
from data_validator.data_valid import ChatRequest
from helper_functions.extract_results import get_actual_ai_message
from models import AnalyzeResponse, SearchResponse


app = FastAPI(
    title="AI Blog/Ad Analysis API",
    description="API for analyzing blog/ad content using LLMs and LangGraph. "
    "Supports session-based interactions, structured extraction, and keyword/topic search.",
    version="1.0.0",
)

graph = build_ad_graph()
with open("ad_graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())


# Initialize components
model = LLMHandler()
postgresql = PostgreSQL()
graph = build_ad_graph()
SESSIONS: dict = {}


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze or Continue Analysis",
    description="""
Start or continue an analysis session on blog/article input.

- **New session:** Omit `session_id`. The server will return a new session with a prompt for input.
- **Continue session:** Provide an existing `session_id` along with `user_input`.

The LLM + graph will extract:
- Title (if available)
- Topics (3 key topics)
- Sentiment (positive / neutral / negative)
- Summary
- Keywords
    """,
    responses={
        200: {"description": "Analysis processed successfully"},
        404: {"description": "Invalid session_id"},
        500: {"description": "LLM or processing failure"},
    },
)
async def chat_endpoint(request: ChatRequest):
    try:
        # Start new session
        if request.session_id is None:
            session_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": session_id}}

            result = graph.invoke({}, config=config)
            SESSIONS[session_id] = config

            state = graph.get_state(config)
            return AnalyzeResponse(
                session_id=session_id,
                status="awaiting_user_input",
                awaiting_node=state.next,
                message=result["__interrupt__"][0].value,
            )

        # Resume session
        session_id = request.session_id
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Invalid session_id")

        config = SESSIONS[session_id]
        cmd = Command(resume=request.user_input or "")
        result = graph.invoke(cmd, config=config)
        state = graph.get_state(config)

        if not result.get("__interrupt__"):
            node = await get_actual_ai_message(session_id, state)
            return AnalyzeResponse(
                session_id=session_id,
                status="done",
                awaiting_node=state.next[0] if state.next else None,
                ai_message=node,
            )
        else:
            node = await get_actual_ai_message(session_id, state)
            return AnalyzeResponse(
                session_id=session_id,
                status="awaiting_user_input",
                awaiting_node=state.next[0] if state.next else None,
                message=result["__interrupt__"][0].value,
                ai_message=node,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get(
    "/search",
    response_model=SearchResponse,
    summary="Search Stored Analyses",
    description="""
Search all stored analyses by topic or keyword.

Example:
- `GET /search?topic=climate`
- `GET /search?topic=AI`

Returns all analyses containing that topic or keyword.
    """,
    responses={
        200: {"description": "Search executed successfully"},
        404: {"description": "No analyses found"},
        500: {"description": "Database or query failure"},
    },
)
async def search(topic: str):
    try:
        results = await postgresql.search_by_topic_or_keyword(topic)

        if not results:
            return SearchResponse(
                status="not_found",
                message=f"No analyses found for '{topic}'",
            )

        return SearchResponse(status="success", count=len(results), results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ---------- RUN SERVER ----------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
