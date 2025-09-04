from data.postgres_db import PostgreSQL

# Initialize Postgres client
postgresql = PostgreSQL()


async def get_actual_ai_message(session_id: str, state: dict):
    """
    Extracts the final AI-generated blog/article analysis from the LangGraph state
    and persists it to PostgreSQL.

    Args:
        session_id (str): Unique session identifier for tracking analysis runs.
        state (dict): Current LangGraph state containing extracted information.

    Returns:
        dict | str:
            - A structured dict with {title, topics, sentiment, summary, keywords}
              if all required fields exist.
            - The interrupt message if user input is missing or incomplete.
            - The raw state if details are incomplete and not ready for storage.
    """
    required_keys = ["topics", "sentiment", "summary", "keywords"]

    # Case 1: Workflow has a "next" step → likely still collecting details
    if state.next:
        # If the next step is `collect_blog_details`, try inserting if data is complete
        if state.next[0] == "collect_blog_details":
            if all(k in state[0] for k in required_keys):
                await postgresql.insert_blog_details(
                    session_id=session_id,
                    title=state[0].get("title"),
                    topics=state[0]["topics"],
                    sentiment=state[0]["sentiment"],
                    summary=state[0]["summary"],
                    keywords=state[0]["keywords"],
                )
                return {
                    "title": state[0].get("title"),
                    "topics": state[0]["topics"],
                    "sentiment": state[0]["sentiment"],
                    "summary": state[0]["summary"],
                    "keywords": state[0]["keywords"],
                }
            # If required keys are missing, return interrupt value
            return {"response": state.interrupts[0].value}

        # Otherwise return the raw state (workflow not ready yet)
        return {"response": state}

    # Case 2: Workflow has ended (no `next`) → check if we can persist final result
    if all(k in state[0] for k in required_keys):
        await postgresql.insert_blog_details(
            session_id=session_id,
            title=state[0].get("title"),
            topics=state[0]["topics"],
            sentiment=state[0]["sentiment"],
            summary=state[0]["summary"],
            keywords=state[0]["keywords"],
        )
        return {
            "title": state[0].get("title"),
            "topics": state[0]["topics"],
            "sentiment": state[0]["sentiment"],
            "summary": state[0]["summary"],
            "keywords": state[0]["keywords"],
        }

    # Case 3: Fallback — incomplete state
    return {"response": state}
