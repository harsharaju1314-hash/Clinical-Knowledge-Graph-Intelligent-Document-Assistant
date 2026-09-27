"""
Knowledge Graph Engine.
Provides relational persistence and NetworkX in-memory graph traversal,
subgraph extraction for RAG prompts, and clinical ontology validation.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
import networkx as nx
from sqlalchemy.orm import Session
from app.core.models import EntityModel, RelationshipModel
from app.core.ontology import ClinicalOntology
from app.core.schemas import (
    EntityCreate,
    RelationshipCreate,
    GraphTripleItem,
    EntityWithNeighborsResponse,
    EntityResponse,
)


class KnowledgeGraphEngine:
    def __init__(self):
        self._nx_graph = nx.DiGraph()

    def sync_from_database(self, db: Session) -> None:
        """Synchronize the in-memory NetworkX graph with database records."""
        self._nx_graph.clear()
        entities = db.query(EntityModel).all()
        for e in entities:
            self._nx_graph.add_node(
                e.id,
                name=e.name,
                entity_type=e.entity_type,
                description=e.description,
                properties=e.properties_json or {},
            )

        relationships = db.query(RelationshipModel).all()
        for r in relationships:
            self._nx_graph.add_edge(
                r.source_id,
                r.target_id,
                id=r.id,
                relation_type=r.relation_type,
                properties=r.properties_json or {},
            )

    def add_entity(self, db: Session, entity_in: EntityCreate) -> EntityModel:
        """Add or update an entity after ontology type verification."""
        if not ClinicalOntology.is_valid_entity_type(entity_in.entity_type):
            raise ValueError(
                f"Invalid entity type '{entity_in.entity_type}'. "
                f"Must be one of {sorted(ClinicalOntology.get_ontology_schema()['entity_types'])}"
            )

        existing = db.query(EntityModel).filter(EntityModel.id == entity_in.id).first()
        if existing:
            existing.name = entity_in.name
            existing.entity_type = entity_in.entity_type
            existing.description = entity_in.description
            existing.properties_json = entity_in.properties
            db.commit()
            db.refresh(existing)
            self._nx_graph.add_node(
                existing.id,
                name=existing.name,
                entity_type=existing.entity_type,
                description=existing.description,
                properties=existing.properties_json,
            )
            return existing

        entity_obj = EntityModel(
            id=entity_in.id,
            name=entity_in.name,
            entity_type=entity_in.entity_type,
            description=entity_in.description,
            properties_json=entity_in.properties,
        )
        db.add(entity_obj)
        db.commit()
        db.refresh(entity_obj)

        self._nx_graph.add_node(
            entity_obj.id,
            name=entity_obj.name,
            entity_type=entity_obj.entity_type,
            description=entity_obj.description,
            properties=entity_obj.properties_json,
        )
        return entity_obj

    def add_relationship(self, db: Session, rel_in: RelationshipCreate) -> RelationshipModel:
        """Add a directed relationship after validating ontology constraints."""
        source = db.query(EntityModel).filter(EntityModel.id == rel_in.source_id).first()
        if not source:
            raise ValueError(f"Source entity ID '{rel_in.source_id}' does not exist.")

        target = db.query(EntityModel).filter(EntityModel.id == rel_in.target_id).first()
        if not target:
            raise ValueError(f"Target entity ID '{rel_in.target_id}' does not exist.")

        # Validate against clinical domain ontology
        is_valid, msg = ClinicalOntology.validate_relationship(
            source.entity_type, rel_in.relation_type, target.entity_type
        )
        if not is_valid:
            raise ValueError(f"Ontology Constraint Violation: {msg}")

        # Check for existing identical relationship
        existing = (
            db.query(RelationshipModel)
            .filter(
                RelationshipModel.source_id == rel_in.source_id,
                RelationshipModel.relation_type == rel_in.relation_type,
                RelationshipModel.target_id == rel_in.target_id,
            )
            .first()
        )
        if existing:
            existing.properties_json = rel_in.properties
            db.commit()
            db.refresh(existing)
            return existing

        rel_obj = RelationshipModel(
            source_id=rel_in.source_id,
            relation_type=rel_in.relation_type,
            target_id=rel_in.target_id,
            properties_json=rel_in.properties,
        )
        db.add(rel_obj)
        db.commit()
        db.refresh(rel_obj)

        self._nx_graph.add_edge(
            rel_obj.source_id,
            rel_obj.target_id,
            id=rel_obj.id,
            relation_type=rel_obj.relation_type,
            properties=rel_obj.properties_json,
        )
        return rel_obj

    def get_entity_with_connections(self, db: Session, entity_id: str) -> Optional[EntityWithNeighborsResponse]:
        """Fetch entity details with 1-hop outgoing and incoming connections."""
        entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
        if not entity:
            return None

        outgoing = []
        for r in entity.outgoing_relations:
            outgoing.append({
                "relationship_id": r.id,
                "relation": r.relation_type,
                "target_id": r.target_id,
                "target_name": r.target_entity.name if r.target_entity else "Unknown",
                "target_type": r.target_entity.entity_type if r.target_entity else "Unknown",
                "properties": r.properties_json,
            })

        incoming = []
        for r in entity.incoming_relations:
            incoming.append({
                "relationship_id": r.id,
                "relation": r.relation_type,
                "source_id": r.source_id,
                "source_name": r.source_entity.name if r.source_entity else "Unknown",
                "source_type": r.source_entity.entity_type if r.source_entity else "Unknown",
                "properties": r.properties_json,
            })

        return EntityWithNeighborsResponse(
            entity=EntityResponse.from_orm(entity),
            outgoing=outgoing,
            incoming=incoming,
        )

    def query_subgraph(
        self,
        db: Session,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        relation_type: Optional[str] = None,
        max_hops: int = 1,
    ) -> List[GraphTripleItem]:
        """Query knowledge graph triples based on filters and traversal depth."""
        # Ensure graph is in sync
        if len(self._nx_graph.nodes) == 0:
            self.sync_from_database(db)

        triples: List[GraphTripleItem] = []
        seen_triplets: Set[Tuple[str, str, str]] = set()

        if entity_id:
            if not self._nx_graph.has_node(entity_id):
                # Try reloading from DB
                self.sync_from_database(db)
            
            if not self._nx_graph.has_node(entity_id):
                return []

            visited_nodes: Set[str] = {entity_id}
            current_level: Set[str] = {entity_id}

            for _ in range(max_hops):
                next_level: Set[str] = set()
                for node in current_level:
                    # Outgoing edges
                    for _, target, data in self._nx_graph.out_edges(node, data=True):
                        rel = data.get("relation_type", "related_to")
                        if relation_type and rel != relation_type:
                            continue
                        t_type = self._nx_graph.nodes[target].get("entity_type", "")
                        if entity_type and t_type != entity_type:
                            continue

                        triple_key = (node, rel, target)
                        if triple_key not in seen_triplets:
                            seen_triplets.add(triple_key)
                            triples.append(
                                GraphTripleItem(
                                    source_id=node,
                                    source_name=self._nx_graph.nodes[node].get("name", node),
                                    source_type=self._nx_graph.nodes[node].get("entity_type", "Unknown"),
                                    relation=rel,
                                    target_id=target,
                                    target_name=self._nx_graph.nodes[target].get("name", target),
                                    target_type=self._nx_graph.nodes[target].get("entity_type", "Unknown"),
                                )
                            )
                        if target not in visited_nodes:
                            visited_nodes.add(target)
                            next_level.add(target)

                    # Incoming edges
                    for source, _, data in self._nx_graph.in_edges(node, data=True):
                        rel = data.get("relation_type", "related_to")
                        if relation_type and rel != relation_type:
                            continue
                        s_type = self._nx_graph.nodes[source].get("entity_type", "")
                        if entity_type and s_type != entity_type:
                            continue

                        triple_key = (source, rel, node)
                        if triple_key not in seen_triplets:
                            seen_triplets.add(triple_key)
                            triples.append(
                                GraphTripleItem(
                                    source_id=source,
                                    source_name=self._nx_graph.nodes[source].get("name", source),
                                    source_type=self._nx_graph.nodes[source].get("entity_type", "Unknown"),
                                    relation=rel,
                                    target_id=node,
                                    target_name=self._nx_graph.nodes[node].get("name", node),
                                    target_type=self._nx_graph.nodes[node].get("entity_type", "Unknown"),
                                )
                            )
                        if source not in visited_nodes:
                            visited_nodes.add(source)
                            next_level.add(source)
                current_level = next_level

        else:
            # Query all relationships matching filter
            query = db.query(RelationshipModel).join(
                EntityModel, RelationshipModel.source_id == EntityModel.id
            )
            if relation_type:
                query = query.filter(RelationshipModel.relation_type == relation_type)
            if entity_type:
                query = query.filter(EntityModel.entity_type == entity_type)

            results = query.all()
            for r in results:
                s_name = r.source_entity.name if r.source_entity else r.source_id
                s_type = r.source_entity.entity_type if r.source_entity else "Unknown"
                t_name = r.target_entity.name if r.target_entity else r.target_id
                t_type = r.target_entity.entity_type if r.target_entity else "Unknown"

                triples.append(
                    GraphTripleItem(
                        source_id=r.source_id,
                        source_name=s_name,
                        source_type=s_type,
                        relation=r.relation_type,
                        target_id=r.target_id,
                        target_name=t_name,
                        target_type=t_type,
                    )
                )

        return triples

    def extract_subgraph_for_query_text(self, db: Session, query_text: str, max_hops: int = 2) -> List[GraphTripleItem]:
        """
        Identify entity mentions in the natural language text and traverse
        the knowledge graph to retrieve all relevant contextual triples.
        """
        if len(self._nx_graph.nodes) == 0:
            self.sync_from_database(db)

        query_lower = query_text.lower()
        matched_entity_ids: List[str] = []

        # Find matching entities in graph
        for node_id, data in self._nx_graph.nodes(data=True):
            name = data.get("name", "").lower()
            node_id_lower = node_id.lower()
            if (len(name) > 3 and name in query_lower) or (len(node_id_lower) > 3 and node_id_lower in query_lower):
                matched_entity_ids.append(node_id)

        all_triples: List[GraphTripleItem] = []
        seen: Set[Tuple[str, str, str]] = set()

        for ent_id in matched_entity_ids:
            ent_triples = self.query_subgraph(db, entity_id=ent_id, max_hops=max_hops)
            for t in ent_triples:
                key = (t.source_id, t.relation, t.target_id)
                if key not in seen:
                    seen.add(key)
                    all_triples.append(t)

        return all_triples


kg_engine = KnowledgeGraphEngine()
