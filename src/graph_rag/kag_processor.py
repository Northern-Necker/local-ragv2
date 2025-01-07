from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from .graph_processor import GraphProcessor, GraphContext
from ..document_processors.chunking_strategy import DocumentChunk, ChunkMetadata

@dataclass
class KAGNode:
    """Node in the Knowledge-Augmented Graph"""
    id: str
    content: str
    node_type: str  # 'chunk', 'section', 'concept', etc.
    metadata: Dict[str, Any]
    relationships: Set[str]  # IDs of related nodes

@dataclass
class KAGEdge:
    """Edge in the Knowledge-Augmented Graph"""
    source_id: str
    target_id: str
    edge_type: str  # 'contains', 'references', 'similar_to', etc.
    weight: float
    metadata: Dict[str, Any]

class KAGProcessor:
    """Handles Knowledge-Augmented Graph construction and querying"""
    
    def __init__(self, graph_processor: GraphProcessor):
        """Initialize KAG processor
        
        Args:
            graph_processor: GraphRAG processor instance
        """
        self.graph_processor = graph_processor
        self.nodes: Dict[str, KAGNode] = {}
        self.edges: List[KAGEdge] = []
    
    def build_graph(
        self,
        macro_chunks: List[DocumentChunk],
        micro_chunks: List[DocumentChunk]
    ) -> None:
        """Build Knowledge-Augmented Graph from chunks
        
        Args:
            macro_chunks: List of macro-level chunks
            micro_chunks: List of micro-level chunks
        """
        # Create nodes for all chunks
        self._create_chunk_nodes(macro_chunks, "macro")
        self._create_chunk_nodes(micro_chunks, "micro")
        
        # Create section nodes from chunk metadata
        self._create_section_nodes(macro_chunks + micro_chunks)
        
        # Create hierarchical relationships
        self._create_hierarchical_edges()
        
        # Create semantic relationships
        self._create_semantic_edges()
        
        # Build GraphRAG graph
        self._build_graph_rag()
    
    def _create_chunk_nodes(
        self,
        chunks: List[DocumentChunk],
        chunk_type: str
    ) -> None:
        """Create nodes for document chunks"""
        for chunk in chunks:
            node = KAGNode(
                id=chunk.id,
                content=chunk.content,
                node_type=f"{chunk_type}_chunk",
                metadata={
                    "source_id": chunk.metadata.source_element_id,
                    "page_range": chunk.metadata.page_range,
                    "confidence": chunk.metadata.confidence,
                    **chunk.metadata.additional_metadata
                },
                relationships=set()
            )
            self.nodes[node.id] = node
    
    def _create_section_nodes(self, chunks: List[DocumentChunk]) -> None:
        """Create nodes for document sections"""
        section_contents: Dict[str, List[str]] = {}
        
        # Collect content for each section
        for chunk in chunks:
            for section_id in chunk.metadata.section_path:
                if section_id not in section_contents:
                    section_contents[section_id] = []
                section_contents[section_id].append(chunk.content)
        
        # Create section nodes
        for section_id, contents in section_contents.items():
            node = KAGNode(
                id=f"section_{section_id}",
                content="\n".join(contents),  # Combine all section content
                node_type="section",
                metadata={
                    "section_id": section_id
                },
                relationships=set()
            )
            self.nodes[node.id] = node
    
    def _create_hierarchical_edges(self) -> None:
        """Create edges representing document hierarchy"""
        # Create section containment edges
        for node_id, node in self.nodes.items():
            if node.node_type in ("macro_chunk", "micro_chunk"):
                # Connect chunks to their sections
                for section_id in node.metadata.get("section_path", []):
                    section_node_id = f"section_{section_id}"
                    if section_node_id in self.nodes:
                        edge = KAGEdge(
                            source_id=section_node_id,
                            target_id=node_id,
                            edge_type="contains",
                            weight=1.0,
                            metadata={}
                        )
                        self.edges.append(edge)
                        
                        # Update relationships sets
                        self.nodes[section_node_id].relationships.add(node_id)
                        node.relationships.add(section_node_id)
    
    def _create_semantic_edges(self) -> None:
        """Create edges representing semantic relationships"""
        # Use GraphRAG to find semantic relationships
        for node_id, node in self.nodes.items():
            if node.node_type in ("macro_chunk", "micro_chunk"):
                # Get related nodes from GraphRAG
                context = self.graph_processor.get_node_context(node_id)
                
                # Create edges for semantic relationships
                for related in context.nodes:
                    if related.id != node_id and related.id in self.nodes:
                        edge = KAGEdge(
                            source_id=node_id,
                            target_id=related.id,
                            edge_type="similar_to",
                            weight=related.metadata.get("similarity", 0.0),
                            metadata={}
                        )
                        self.edges.append(edge)
                        
                        # Update relationships sets
                        node.relationships.add(related.id)
                        self.nodes[related.id].relationships.add(node_id)
    
    def _build_graph_rag(self) -> None:
        """Build GraphRAG graph from KAG nodes and edges"""
        # Convert KAG nodes and edges to GraphRAG format
        graph_nodes = []
        for node in self.nodes.values():
            graph_node = {
                "id": node.id,
                "content": node.content,
                "type": node.node_type,
                "metadata": {
                    **node.metadata,
                    "relationships": list(node.relationships)
                }
            }
            graph_nodes.append(graph_node)
        
        graph_edges = []
        for edge in self.edges:
            graph_edge = {
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.edge_type,
                "weight": edge.weight,
                "metadata": edge.metadata
            }
            graph_edges.append(graph_edge)
        
        # Build the graph
        self.graph_processor.build_graph(graph_nodes, graph_edges)
    
    async def query(
        self,
        query_text: str,
        max_results: int = 5
    ) -> List[GraphContext]:
        """Query the Knowledge-Augmented Graph
        
        Args:
            query_text: Natural language query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant graph contexts
        """
        return await self.graph_processor.query(
            query_text=query_text,
            max_context=max_results
        )
    
    def get_node_context(
        self,
        node_id: str,
        depth: int = 2,
        include_sections: bool = True
    ) -> GraphContext:
        """Get context around a specific node
        
        Args:
            node_id: ID of the node to get context for
            depth: How many hops to traverse for context
            include_sections: Whether to include section nodes
            
        Returns:
            Graph context around the node
        """
        context = self.graph_processor.get_node_context(
            node_id=node_id,
            depth=depth
        )
        
        if not include_sections:
            # Filter out section nodes from context
            context.nodes = [
                n for n in context.nodes
                if not n.type.startswith("section")
            ]
            context.edges = [
                e for e in context.edges
                if not (e.source.startswith("section") or e.target.startswith("section"))
            ]
        
        return context
