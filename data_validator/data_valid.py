from pydantic import BaseModel, Field
from typing import List, TypedDict, Literal, Optional


class BlogBuilderState(TypedDict, total=False):
    """
    Internal state object for blog analysis workflow.

    Used to track progress between steps in the pipeline.
    This is NOT exposed to the API directly.
    """

    user_input: str
    title: str
    topics: List[str]
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str
    keywords: List[str]


class BlogDetails(BaseModel):
    """
    Represents extracted blog details after processing.
    Returned to frontend clients.
    """

    title: str = Field(..., description="Title of the blog or article.")
    topics: List[str] = Field(..., description="List of extracted topics (tags).")
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        ..., description="Overall sentiment of the blog."
    )


class ChatRequest(BaseModel):
    """
    Incoming request schema for chat/analysis endpoints.
    """

    session_id: Optional[str] = Field(
        None,
        description="Optional session ID to track analysis across requests.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    user_input: Optional[str] = Field(
        None,
        description="Raw article or blog text provided by the user.",
        example="Artificial Intelligence is reshaping the future of fashion retail.",
    )
