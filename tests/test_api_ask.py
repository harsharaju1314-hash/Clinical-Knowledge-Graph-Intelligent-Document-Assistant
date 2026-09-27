"""
Integration tests for Multi-Agent /ask endpoint and health check.
"""

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_documents"] >= 5
    assert data["total_entities"] >= 15


def test_ask_endpoint_cardiovax_query(client):
    payload = {
        "question": "What clinical studies evaluated Cardiovax and what outcomes were reported?",
        "include_graph": True,
        "include_vector": True,
        "top_k": 3,
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["grounded"] is True
    assert len(data["citations"]) > 0
    assert len(data["graph_context"]) > 0
    assert len(data["agent_traces"]) == 3
    assert "SYNTHETIC DATA NOTICE" in data["disclaimer"]
    assert "Cardiovax" in data["answer"]


def test_ask_endpoint_empty_question(client):
    payload = {
        "question": "   ",
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 400


def test_seed_endpoint(client):
    response = client.post("/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["documents_seeded"] >= 5
