"""
Integration tests for document ingestion and retrieval API endpoints.
"""

def test_get_documents_list(client):
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    assert any("CARDIO-701" in d["title"] for d in data)


def test_get_document_by_id(client):
    # First get document list to get a valid ID
    list_resp = client.get("/documents")
    doc_id = list_resp.json()[0]["id"]

    response = client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert len(data["chunks"]) > 0


def test_get_document_not_found(client):
    response = client.get("/documents/non-existent-doc-uuid")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_ingest_document_success(client):
    payload = {
        "title": "NEO-909 Oncology Phase 1 Study",
        "doc_type": "study_summary",
        "content": """# NEO-909 Phase 1 Summary
Cardiovax was also studied in combination for Resistant Hypertension.
The safety profile showed minimal hypotension.""",
        "metadata": {"phase": "Phase 1"},
    }
    response = client.post("/documents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "NEO-909 Oncology Phase 1 Study"
    assert len(data["chunks"]) > 0


def test_ingest_document_empty_content(client):
    payload = {
        "title": "Empty Doc",
        "doc_type": "protocol",
        "content": "   ",
        "metadata": {},
    }
    response = client.post("/documents", json=payload)
    assert response.status_code == 400
