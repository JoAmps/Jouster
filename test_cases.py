import pytest
from pydantic import ValidationError
from models import AnalyzeResponse, SearchResponse  # adjust import path


def test_analyze_response_with_valid_data():
    """
    Test that AnalyzeResponse correctly parses valid structured data.
    Ensures that:
    - session_id is preserved
    - status is 'done'
    - awaiting_node is a tuple with the correct node
    - ai_message dictionary contains expected values
    """
    data = {
        "session_id": "12345",
        "status": "done",
        "awaiting_node": ("generate_summary",),
        "ai_message": {
            "title": "AI in Education",
            "topics": ["AI", "Education"],
            "sentiment": "positive",
            "summary": "AI is transforming learning",
            "keywords": ["AI", "learning", "edtech"],
        },
    }
    response = AnalyzeResponse(**data)

    assert response.session_id == "12345"
    assert response.status == "done"
    assert response.awaiting_node == ("generate_summary",)
    assert response.ai_message["title"] == "AI in Education"


def test_analyze_response_invalid_session_id():
    """
    Test that AnalyzeResponse raises a ValidationError
    when the session_id is missing or invalid.
    """
    data = {
        "session_id": None,  # invalid
        "status": "done",
    }
    with pytest.raises(ValidationError):
        AnalyzeResponse(**data)


def test_search_response_success():
    """
    Test that SearchResponse correctly parses a successful search result.
    Ensures:
    - status is 'success'
    - count matches number of results
    - results list is populated
    """
    data = {
        "status": "success",
        "count": 2,
        "results": [
            {"id": 1, "title": "AI in Fashion"},
            {"id": 2, "title": "AI in Education"},
        ],
    }
    response = SearchResponse(**data)

    assert response.status == "success"
    assert response.count == 2
    assert len(response.results) == 2
    assert response.results[0]["title"] == "AI in Fashion"


def test_search_response_not_found():
    """
    Test that SearchResponse correctly handles the 'not_found' case.
    Ensures:
    - status is 'not_found'
    - message is included
    - results remain None
    """
    data = {
        "status": "not_found",
        "message": "No results available",
    }
    response = SearchResponse(**data)

    assert response.status == "not_found"
    assert response.message == "No results available"
    assert response.results is None
