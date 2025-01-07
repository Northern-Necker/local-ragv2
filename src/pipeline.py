from typing import Optional, Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv

from .document_processors.adi_processor import ADIProcessor, DocumentStructure
from .document_processors.chunking_strategy import ChunkingStrategy
from .graph_rag.graph_processor import GraphProcessor
from .graph_rag.kag_processor import KAGProcessor
from .storage.vector_store import VectorStore

class Pipeline:
    """Main pipeline combining ADI, KAG, and vector storage"""
    
    def __init__(
        self,
        persist_directory: str = "vector_store",
        model_name: str = "microsoft/graphrag-base",
        min_macro_length: int = 100,
        max_micro_length: int = 50,
        overlap_tokens: int = 20
    ):
        """Initialize the pipeline
        
        Args:
            persist_directory: Directory for vector store persistence
            model_name: Name of the GraphRAG model to use
            min_macro_length: Minimum length for macro chunks
            max_micro_length: Maximum length for micro chunks
            overlap_tokens: Token overlap between chunks
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize ADI processor
        self.adi_processor = ADIProcessor(
            endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
            key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        )
        
        # Initialize chunking strategy
        self.chunking_strategy = ChunkingStrategy(
            min_macro_length=min_macro_length,
            max_micro_length=max_micro_length,
            overlap_tokens=overlap_tokens
        )
        
        # Initialize graph components
        self.graph_processor = GraphProcessor(model_name=model_name)
        self.kag_processor = KAGProcessor(graph_processor=self.graph_processor)
        
        # Initialize vector store
        self.vector_store = VectorStore(persist_directory=persist_directory)
        
        # Store processed documents
        self.documents: Dict[str, DocumentStructure] = {}
    
    async def process_document(
        self,
        document_path: str,
        document_id: Optional[str] = None
    ) -> str:
        """Process a document through the pipeline
        
        Args:
            document_path: Path to the document file
            document_id: Optional ID for the document
            
        Returns:
            Document ID
        """
        # Generate document ID if not provided
        if document_id is None:
            document_id = Path(document_path).stem
        
        # 1. Document Analysis with ADI
        doc_structure = await self.adi_processor.analyze_document(document_path)
        self.documents[document_id] = doc_structure
        
        # 2. Create chunks
        macro_chunks, micro_chunks = self.chunking_strategy.create_chunks(doc_structure)
        
        # 3. Build KAG graph
        self.kag_processor.build_graph(
            macro_chunks=macro_chunks,
            micro_chunks=micro_chunks
        )
        
        # 4. Store chunks in vector store
        self.vector_store.add_elements(
            elements=doc_structure.elements,
            graph_contexts=await self.kag_processor.query(
                "Get all document sections",
                max_results=len(doc_structure.elements)
            )
        )
        
        return document_id
    
    async def query(
        self,
        query_text: str,
        document_id: Optional[str] = None,
        max_results: int = 5,
        include_graph_context: bool = True
    ) -> Dict[str, Any]:
        """Query the processed documents
        
        Args:
            query_text: Natural language query
            document_id: Optional document ID to restrict search
            max_results: Maximum number of results to return
            include_graph_context: Whether to include graph context
            
        Returns:
            Dictionary containing vector and graph results
        """
        # Get vector store results
        vector_results = self.vector_store.query(
            query_text=query_text,
            n_results=max_results,
            include_graph=include_graph_context
        )
        
        # Get graph context if requested
        graph_results = None
        if include_graph_context:
            graph_results = await self.kag_processor.query(
                query_text=query_text,
                max_results=max_results
            )
        
        return {
            "vector_results": vector_results,
            "graph_results": graph_results
        }
    
    def get_document_structure(self, document_id: str) -> Optional[DocumentStructure]:
        """Get the structure of a processed document
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document structure if found, None otherwise
        """
        return self.documents.get(document_id)
    
    def get_node_context(
        self,
        node_id: str,
        depth: int = 2,
        include_sections: bool = True
    ) -> Dict[str, Any]:
        """Get context around a specific node
        
        Args:
            node_id: ID of the node
            depth: How many hops to traverse
            include_sections: Whether to include section nodes
            
        Returns:
            Dictionary containing node context
        """
        graph_context = self.kag_processor.get_node_context(
            node_id=node_id,
            depth=depth,
            include_sections=include_sections
        )
        
        vector_context = self.vector_store.query(
            query_text=graph_context.nodes[0].content,  # Use node content as query
            n_results=5,
            include_graph=False
        )
        
        return {
            "graph_context": graph_context,
            "vector_context": vector_context
        }
