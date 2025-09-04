from typing import List, Optional, Dict, Any, Tuple, Union

from pydantic import BaseModel, Field

# ---------- RESPONSE MODELS ----------


class AnalyzeResponse(BaseModel):
    session_id: str = Field(..., description="Unique ID for the analysis session")
    status: str = Field(
        ...,
        description="Current status of the session: 'awaiting_user_input' or 'done'",
    )
    awaiting_node: Optional[Union[str, Tuple[str, ...]]] = Field(
        None,
        description="The next node(s) in the analysis graph as a string or tuple of strings",
    )
    message: Optional[str] = Field(
        None, description="Message or prompt from the AI if awaiting input"
    )
    ai_message: Optional[Dict[str, Any]] = Field(
        None, description="Final structured AI analysis results"
    )


class SearchResponse(BaseModel):
    status: str = Field(..., description="Result status: 'success' or 'not_found'")
    count: Optional[int] = Field(None, description="Number of results found")
    results: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of stored analyses matching the search query"
    )
    message: Optional[str] = Field(
        None, description="Error or info message if no results found"
    )
