"""
Integration tests for Knowledge Graph and entity endpoints.
"""

def test_get_ontology_schema(client):
    response = client.get("/graph/ontology")
    assert response.status_code == 200
    data = response.json()
    assert "entity_types" in data
    assert "relation_types" in data
    assert "Drug" in data["entity_types"]


def test_list_entities(client):
    response = client.get("/entities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    entity_ids = [e["id"] for e in data]
    assert "DRUG-CARDIOVAX" in entity_ids


def test_list_entities_with_type_filter(client):
    response = client.get("/entities?entity_type=Drug")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(e["entity_type"] == "Drug" for e in data)


def test_get_entity_details(client):
    response = client.get("/entities/DRUG-CARDIOVAX")
    assert response.status_code == 200
    data = response.json()
    assert data["entity"]["id"] == "DRUG-CARDIOVAX"
    assert "outgoing" in data
    assert len(data["outgoing"]) > 0


def test_get_entity_not_found(client):
    response = client.get("/entities/NON-EXISTENT-ENTITY")
    assert response.status_code == 404


def test_create_entity(client):
    payload = {
        "id": "DRUG-NOVAMED",
        "name": "NovaMed",
        "entity_type": "Drug",
        "description": "Synthetic trial molecule",
        "properties": {"phase": "Preclinical"},
    }
    response = client.post("/entities", json=payload)
    assert response.status_code == 201
    assert response.json()["id"] == "DRUG-NOVAMED"


def test_create_entity_invalid_ontology_type(client):
    payload = {
        "id": "BAD-01",
        "name": "BadEntity",
        "entity_type": "BogusType",
        "description": "Invalid",
    }
    response = client.post("/entities", json=payload)
    assert response.status_code == 400


def test_create_relationship_success(client):
    payload = {
        "source_id": "DRUG-CARDIOVAX",
        "relation_type": "treats",
        "target_id": "COND-HYPERTENSION",
    }
    response = client.post("/relationships", json=payload)
    assert response.status_code == 201


def test_query_graph_endpoint(client):
    payload = {
        "entity_id": "DRUG-CARDIOVAX",
        "max_hops": 2,
    }
    response = client.post("/graph/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_triples"] > 0
    assert len(data["triples"]) > 0
