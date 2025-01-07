from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

@dataclass
class DocumentElement:
    """Base class for document elements detected by Azure Document Intelligence"""
    id: str
    content: str
    confidence: float
    bounding_box: List[float]
    page_number: int
    type: str  # 'title', 'paragraph', 'table', etc.
    metadata: Dict[str, Any]

@dataclass
class DocumentStructure:
    """Represents the hierarchical structure of a document"""
    elements: List[DocumentElement]
    relationships: List[Dict[str, Any]]  # parent-child, next-prev relationships
    metadata: Dict[str, Any]

class ADIProcessor:
    """Azure Document Intelligence Processor"""
    
    def __init__(self, endpoint: str, key: str):
        """Initialize the ADI processor
        
        Args:
            endpoint: Azure Document Intelligence endpoint
            key: Azure Document Intelligence key
        """
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    async def analyze_document(self, document_path: str) -> DocumentStructure:
        """Analyze document using Azure Document Intelligence
        
        Args:
            document_path: Path to the document file
            
        Returns:
            DocumentStructure containing the analyzed elements and relationships
        """
        # Open document file
        with open(document_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout",  # Using the layout model
                document=f
            )
        result = poller.result()
        
        # Process elements
        elements = []
        for page in result.pages:
            # Process tables
            for table in page.tables:
                elements.append(DocumentElement(
                    id=f"table_{len(elements)}",
                    content=self._extract_table_content(table),
                    confidence=table.confidence,
                    bounding_box=table.bounding_box,
                    page_number=page.page_number,
                    type="table",
                    metadata={
                        "row_count": table.row_count,
                        "column_count": table.column_count
                    }
                ))
            
            # Process paragraphs
            for paragraph in page.paragraphs:
                elements.append(DocumentElement(
                    id=f"paragraph_{len(elements)}",
                    content=paragraph.content,
                    confidence=paragraph.confidence,
                    bounding_box=paragraph.bounding_box,
                    page_number=page.page_number,
                    type="paragraph",
                    metadata={}
                ))
        
        # Build relationships
        relationships = self._build_relationships(elements)
        
        return DocumentStructure(
            elements=elements,
            relationships=relationships,
            metadata={
                "page_count": len(result.pages),
                "language": result.languages,
                "styles": self._extract_styles(result)
            }
        )
    
    def _extract_table_content(self, table: Any) -> str:
        """Extract formatted content from a table"""
        content = []
        for cell in table.cells:
            content.append(cell.content)
        return "\n".join(content)
    
    def _build_relationships(self, elements: List[DocumentElement]) -> List[Dict[str, Any]]:
        """Build relationships between document elements based on layout and content"""
        relationships = []
        
        # Sort elements by page and position
        sorted_elements = sorted(
            elements,
            key=lambda e: (e.page_number, e.bounding_box[1])  # Sort by page then y-coordinate
        )
        
        # Build reading order relationships
        for i in range(len(sorted_elements) - 1):
            relationships.append({
                "type": "next",
                "source": sorted_elements[i].id,
                "target": sorted_elements[i + 1].id
            })
        
        # Build hierarchical relationships (e.g., section titles with their content)
        for i, elem in enumerate(sorted_elements):
            if elem.type == "title":
                # Find content that belongs to this title
                j = i + 1
                while j < len(sorted_elements) and not sorted_elements[j].type == "title":
                    relationships.append({
                        "type": "contains",
                        "source": elem.id,
                        "target": sorted_elements[j].id
                    })
                    j += 1
        
        return relationships
    
    def _extract_styles(self, result: Any) -> Dict[str, Any]:
        """Extract document style information"""
        styles = {}
        for style in result.styles:
            styles[style.name] = {
                "font": style.font_family,
                "size": style.font_size,
                "color": style.color,
                "is_bold": style.is_bold,
                "is_italic": style.is_italic
            }
        return styles
