from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from data_validator.data_valid import BlogBuilderState
from blog_generator.blog_details import BlogDetails


# Instantiate the BlogDetails handler
blog_details = BlogDetails()


def build_ad_graph():
    """
    Build and compile the LangGraph workflow for blog/article analysis.

    Workflow Steps:
    ---------------
    1. ask_blog_details → Prompt the user to provide a blog/article.
    2. collect_blog_details → Extract structured details (title, topics, sentiment).
    3. get_keywords → Extract top keywords (noun frequency-based).
    4. generate_summary → Generate a concise 1–2 sentence summary.
    5. END → Mark workflow as complete.

    Returns:
    --------
    graph : Compiled LangGraph object with in-memory checkpointing.
    """
    # Initialize a state graph using BlogBuilderState as the schema
    builder = StateGraph(BlogBuilderState)

    # Register nodes (each step of the pipeline)
    builder.add_node("ask_blog_details", blog_details.ask_blog_details)
    builder.add_node("collect_blog_details", blog_details.collect_blog_details)
    builder.add_node("get_keywords", blog_details.get_keywords)
    builder.add_node("generate_summary", blog_details.generate_summary)

    # Define entry point (starting node)
    builder.set_entry_point("ask_blog_details")

    # Define execution flow (edges between nodes)
    builder.add_edge("ask_blog_details", "collect_blog_details")
    builder.add_edge("collect_blog_details", "get_keywords")
    builder.add_edge("get_keywords", "generate_summary")
    builder.add_edge("generate_summary", END)

    # Use in-memory checkpointing (keeps session progress)
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    return graph
