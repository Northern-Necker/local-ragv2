from typing import List, Dict, Any, Optional
import os
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from ..document_processors.adi_processor import DocumentElement
from ..graph_rag.graph_processor import GraphContext

class VectorStore:
    """Vector storage using ChromaDB with enhanced graph context"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        persist_directory: Optional[str] = None
    ):
        """Initialize the vector store
        
        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            persist_directory: Optional local directory for persistence (fallback)
        """
        try:
            # Try to connect to ChromaDB server
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
        except Exception as e:
            if persist_directory:
                # Fall back to local persistence if server unavailable
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False
                    )
                )
            else:
                raise ConnectionError(
                    f"Failed to connect to ChromaDB server and no fallback directory provided: {e}"
                )
        
        # Create collections for different types of embeddings
        self.macro_collection = self.client.get_or_create_collection(
            name="macro_chunks",
            metadata={"description": "Large document sections"}
        )
        self.micro_collection = self.client.get_or_create_collection(
            name="micro_chunks",
            metadata={"description": "Fine-grained document elements"}
        )
        self.graph_collection = self.client.get_or_create_collection(
            name="graph_contexts",
            metadata={"description": "Graph-based contextual embeddings"}
        )
    
    def add_elements(
        self,
        elements: List[DocumentElement],
        graph_contexts: Optional[List[GraphContext]] = None
    ) -> None:
        """Add document elements to vector store
        
        Args:
            elements: List of document elements to add
            graph_contexts: Optional list of graph contexts for enhanced embeddings
        """
        # Separate elements into macro and micro chunks
        macro_elements = [e for e in elements if self._is_macro_element(e)]
        micro_elements = [e for e in elements if not self._is_macro_element(e)]
        
        # Add macro chunks
        if macro_elements:
            self._add_to_collection(
                collection=self.macro_collection,
                elements=macro_elements,
                prefix="macro"
            )
        
        # Add micro chunks
        if micro_elements:
            self._add_to_collection(
                collection=self.micro_collection,
                elements=micro_elements,
                prefix="micro"
            )
        
        # Add graph contexts if provided
        if graph_contexts:
            self._add_graph_contexts(graph_contexts)
    
    def _add_to_collection(
        self,
        collection: Collection,
        elements: List[DocumentElement],
        prefix: str
    ) -> None:
        """Add elements to a collection
        
        Args:
            collection: ChromaDB collection
            elements: Elements to add
            prefix: ID prefix ('macro' or 'micro')
        """
        collection.add(
            documents=[e.content for e in elements],
            metadatas=[{
                "id": e.id,
                "type": e.type,
                "page_number": e.page_number,
                "confidence": e.confidence,
                **e.metadata
            } for e in elements],
            ids=[f"{prefix}_{e.id}" for e in elements]
        )
    
    def _add_graph_contexts(self, contexts: List[GraphContext]) -> None:
        """Add graph contexts to vector store
        
        Args:
            contexts: List of graph contexts to add
        """
        self.graph_collection.add(
            documents=[
                self._serialize_graph_context(ctx) 
                for ctx in contexts
            ],
            metadatas=[{
                "relevance_score": ctx.relevance_score,
                **ctx.metadata
            } for ctx in contexts],
            ids=[f"graph_{i}" for i in range(len(contexts))]
        )
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        include_graph: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Query the vector store
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            include_graph: Whether to include graph contexts
            
        Returns:
            Dictionary containing macro, micro, and graph results
        """
        results = {}
        
        # Query macro chunks
        macro_results = self.macro_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        results["macro"] = self._format_results(macro_results)
        
        # Query micro chunks
        micro_results = self.micro_collection.query(
            query_texts=[query_text],
            n_results=n_results * 2  # Get more micro chunks for better coverage
        )
        results["micro"] = self._format_results(micro_results)
        
        # Query graph contexts if requested
        if include_graph:
            graph_results = self.graph_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            results["graph"] = self._format_results(graph_results)
        
        return results
    
    def _is_macro_element(self, element: DocumentElement) -> bool:
        """Determine if an element should be treated as a macro chunk"""
        macro_types = {"section", "chapter", "table"}
        return (
            element.type in macro_types or
            len(element.content.split()) > 100  # Long content
        )
    
    def _serialize_graph_context(self, context: GraphContext) -> str:
        """Convert graph context to string representation"""
        # Combine node contents with relationship information
        node_texts = []
        for node in context.nodes:
            # Add node content
            node_texts.append(f"{node.type}: {node.content}")
            
            # Add relationship information
            related_edges = [e for e in context.edges if e.source == node.id]
            if related_edges:
                relationships = [
                    f"- {e.type} -> {e.target}"
                    for e in related_edges
                ]
                node_texts.append("Relationships:")
                node_texts.extend(relationships)
        
        return "\n".join(node_texts)
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB results into a standard structure"""
        formatted = []
        for i in range(len(results["ids"])):
            result = {
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
                "distance": results.get("distances", [0])[i]
            }
            formatted.append(result)
        return formatted
