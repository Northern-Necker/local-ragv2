from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from .adi_processor import DocumentElement, DocumentStructure

@dataclass
class ChunkMetadata:
    """Metadata for a document chunk"""
    source_element_id: str
    chunk_type: str  # 'macro' or 'micro'
    page_range: Tuple[int, int]
    section_path: List[str]  # Hierarchical path in document
    confidence: float
    additional_metadata: Dict[str, Any]

@dataclass
class DocumentChunk:
    """A chunk of document content with metadata"""
    id: str
    content: str
    metadata: ChunkMetadata

class ChunkingStrategy:
    """Handles the creation of macro and micro chunks from document elements"""
    
    def __init__(
        self,
        min_macro_length: int = 100,
        max_micro_length: int = 50,
        overlap_tokens: int = 20
    ):
        """Initialize chunking strategy
        
        Args:
            min_macro_length: Minimum length (in words) for macro chunks
            max_micro_length: Maximum length (in words) for micro chunks
            overlap_tokens: Number of tokens to overlap between chunks
        """
        self.min_macro_length = min_macro_length
        self.max_micro_length = max_micro_length
        self.overlap_tokens = overlap_tokens
    
    def create_chunks(
        self,
        doc_structure: DocumentStructure
    ) -> Tuple[List[DocumentChunk], List[DocumentChunk]]:
        """Create macro and micro chunks from document structure
        
        Args:
            doc_structure: Document structure from ADI processor
            
        Returns:
            Tuple of (macro_chunks, micro_chunks)
        """
        macro_chunks = []
        micro_chunks = []
        
        # Build section hierarchy
        section_hierarchy = self._build_section_hierarchy(doc_structure)
        
        # Process each element
        for element in doc_structure.elements:
            # Get section path for element
            section_path = self._get_section_path(element, section_hierarchy)
            
            # Determine if element should be macro chunk
            if self._should_be_macro(element):
                chunks = self._create_macro_chunks(
                    element=element,
                    section_path=section_path
                )
                macro_chunks.extend(chunks)
            else:
                chunks = self._create_micro_chunks(
                    element=element,
                    section_path=section_path
                )
                micro_chunks.extend(chunks)
        
        return macro_chunks, micro_chunks
    
    def _build_section_hierarchy(
        self,
        doc_structure: DocumentStructure
    ) -> Dict[str, List[str]]:
        """Build hierarchical section structure"""
        hierarchy = {}
        
        # Sort elements by page and position
        sorted_elements = sorted(
            doc_structure.elements,
            key=lambda e: (e.page_number, e.bounding_box[1])
        )
        
        current_path = []
        for element in sorted_elements:
            if element.type == "heading":
                # Update path based on heading level
                level = element.metadata.get("heading_level", 1)
                while len(current_path) >= level:
                    current_path.pop()
                current_path.append(element.id)
            
            # Store current path for element
            hierarchy[element.id] = current_path.copy()
        
        return hierarchy
    
    def _get_section_path(
        self,
        element: DocumentElement,
        hierarchy: Dict[str, List[str]]
    ) -> List[str]:
        """Get section path for an element"""
        return hierarchy.get(element.id, [])
    
    def _should_be_macro(self, element: DocumentElement) -> bool:
        """Determine if element should be treated as macro chunk"""
        # Check element type
        macro_types = {"section", "chapter", "table", "heading"}
        if element.type in macro_types:
            return True
        
        # Check content length
        if len(element.content.split()) >= self.min_macro_length:
            return True
        
        # Check metadata hints
        if element.metadata.get("is_section_start", False):
            return True
        
        return False
    
    def _create_macro_chunks(
        self,
        element: DocumentElement,
        section_path: List[str]
    ) -> List[DocumentChunk]:
        """Create macro chunks from an element"""
        chunks = []
        content = element.content
        words = content.split()
        
        # Create single chunk if content is not too long
        if len(words) <= self.min_macro_length * 2:
            chunk = DocumentChunk(
                id=f"macro_{element.id}",
                content=content,
                metadata=ChunkMetadata(
                    source_element_id=element.id,
                    chunk_type="macro",
                    page_range=(element.page_number, element.page_number),
                    section_path=section_path,
                    confidence=element.confidence,
                    additional_metadata=element.metadata
                )
            )
            chunks.append(chunk)
            return chunks
        
        # Split into overlapping chunks if content is long
        chunk_size = self.min_macro_length
        for i in range(0, len(words), chunk_size - self.overlap_tokens):
            chunk_words = words[i:i + chunk_size]
            if len(chunk_words) < self.min_macro_length // 2:
                # Merge small final chunk with previous
                if chunks:
                    prev_chunk = chunks[-1]
                    prev_words = prev_chunk.content.split()
                    prev_words.extend(chunk_words)
                    prev_chunk.content = " ".join(prev_words)
                continue
                
            chunk = DocumentChunk(
                id=f"macro_{element.id}_{i//chunk_size}",
                content=" ".join(chunk_words),
                metadata=ChunkMetadata(
                    source_element_id=element.id,
                    chunk_type="macro",
                    page_range=(element.page_number, element.page_number),
                    section_path=section_path,
                    confidence=element.confidence,
                    additional_metadata={
                        **element.metadata,
                        "chunk_index": i//chunk_size
                    }
                )
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_micro_chunks(
        self,
        element: DocumentElement,
        section_path: List[str]
    ) -> List[DocumentChunk]:
        """Create micro chunks from an element"""
        chunks = []
        content = element.content
        words = content.split()
        
        # Create chunks of appropriate size
        chunk_size = self.max_micro_length
        for i in range(0, len(words), chunk_size - self.overlap_tokens):
            chunk_words = words[i:i + chunk_size]
            if len(chunk_words) < self.max_micro_length // 2:
                # Merge small final chunk with previous
                if chunks:
                    prev_chunk = chunks[-1]
                    prev_words = prev_chunk.content.split()
                    prev_words.extend(chunk_words)
                    prev_chunk.content = " ".join(prev_words)
                continue
                
            chunk = DocumentChunk(
                id=f"micro_{element.id}_{i//chunk_size}",
                content=" ".join(chunk_words),
                metadata=ChunkMetadata(
                    source_element_id=element.id,
                    chunk_type="micro",
                    page_range=(element.page_number, element.page_number),
                    section_path=section_path,
                    confidence=element.confidence,
                    additional_metadata={
                        **element.metadata,
                        "chunk_index": i//chunk_size
                    }
                )
            )
            chunks.append(chunk)
        
        return chunks
