from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from graphrag import GraphRAG, GraphNode, GraphEdge, GraphQuery
from ..document_processors.adi_processor import DocumentElement, DocumentStructure

@dataclass
class GraphContext:
    """Context information from the knowledge graph"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    relevance_score: float
    metadata: Dict[str, Any]

class GraphProcessor:
    """Handles knowledge graph construction and querying using Microsoft's GraphRAG"""
    
    def __init__(self, model_name: str = "microsoft/graphrag-base"):
        """Initialize the GraphRAG processor
        
        Args:
            model_name: Name of the GraphRAG model to use
        """
        self.graph_rag = GraphRAG.from_pretrained(model_name)
        self.graph = None
    
    def build_graph(self, doc_structure: DocumentStructure) -> None:
        """Build knowledge graph from document structure
        
        Args:
            doc_structure: Document structure from ADI processor
        """
        # Create nodes for each document element
        nodes = []
        for element in doc_structure.elements:
            node = GraphNode(
                id=element.id,
                content=element.content,
                type=element.type,
                metadata={
                    "confidence": element.confidence,
                    "page_number": element.page_number,
                    **element.metadata
                }
            )
            nodes.append(node)
        
        # Create edges from relationships
        edges = []
        for rel in doc_structure.relationships:
            edge = GraphEdge(
                source=rel["source"],
                target=rel["target"],
                type=rel["type"]
            )
            edges.append(edge)
        
        # Build the graph
        self.graph = self.graph_rag.build_graph(
            nodes=nodes,
            edges=edges,
            metadata=doc_structure.metadata
        )
    
    async def query(self, query_text: str, max_context: int = 5) -> List[GraphContext]:
        """Query the knowledge graph
        
        Args:
            query_text: Natural language query
            max_context: Maximum number of context elements to return
            
        Returns:
            List of relevant graph contexts
        """
        if not self.graph:
            raise ValueError("Graph not built. Call build_graph first.")
        
        # Convert query to GraphRAG query format
        graph_query = GraphQuery(
            text=query_text,
            metadata={
                "max_context": max_context
            }
        )
        
        # Get query results
        results = await self.graph_rag.query(
            query=graph_query,
            graph=self.graph
        )
        
        # Convert results to GraphContext objects
        contexts = []
        for result in results:
            context = GraphContext(
                nodes=result.nodes,
                edges=result.edges,
                relevance_score=result.score,
                metadata=result.metadata
            )
            contexts.append(context)
        
        return contexts
    
    def get_node_context(self, node_id: str, depth: int = 2) -> GraphContext:
        """Get context around a specific node
        
        Args:
            node_id: ID of the node to get context for
            depth: How many hops to traverse for context
            
        Returns:
            Graph context around the node
        """
        if not self.graph:
            raise ValueError("Graph not built. Call build_graph first.")
        
        # Get subgraph around node
        subgraph = self.graph_rag.get_subgraph(
            node_id=node_id,
            depth=depth
        )
        
        return GraphContext(
            nodes=subgraph.nodes,
            edges=subgraph.edges,
            relevance_score=1.0,  # Direct context has full relevance
            metadata={
                "center_node": node_id,
                "depth": depth
            }
        )
    
    def merge_graphs(self, other_graph: 'GraphProcessor') -> None:
        """Merge another graph into this one
        
        Args:
            other_graph: Another GraphProcessor instance to merge from
        """
        if not self.graph or not other_graph.graph:
            raise ValueError("Both graphs must be built before merging")
        
        # Merge the graphs
        self.graph = self.graph_rag.merge_graphs(
            graph1=self.graph,
            graph2=other_graph.graph
        )
