"""
Integration tests for semantic vector search endpoint.
"""

def test_search_endpoint_success(client):
    payload = {
        "query": "What are the adverse events of Cardiovax in hypertension?",
        "top_k": 3,
        "min_score": 0.0,
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert len(data["results"]) > 0
    assert "similarity_score" in data["results"][0]


def test_search_endpoint_empty_query(client):
    payload = {
        "query": "   ",
        "top_k": 3,
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 400
