import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.pipeline import Pipeline
from src.document_processors.adi_processor import DocumentElement, DocumentStructure

# Test data
SAMPLE_DOCUMENT = """
# Project Requirements

## Overview
This document outlines the main requirements for the project.

## Technical Specifications
1. Must support PDF processing
2. Should handle complex layouts
3. Requires high accuracy

## Implementation Details
The system should be implemented using Python 3.8+.
"""

@pytest.fixture
def mock_adi_response():
    """Mock ADI response with sample document structure"""
    return DocumentStructure(
        elements=[
            DocumentElement(
                id="h1_1",
                content="Project Requirements",
                confidence=0.98,
                bounding_box=[10, 10, 200, 30],
                page_number=1,
                type="heading",
                metadata={"heading_level": 1}
            ),
            DocumentElement(
                id="h2_1",
                content="Overview",
                confidence=0.97,
                bounding_box=[10, 40, 150, 60],
                page_number=1,
                type="heading",
                metadata={"heading_level": 2}
            ),
            DocumentElement(
                id="p1",
                content="This document outlines the main requirements for the project.",
                confidence=0.95,
                bounding_box=[10, 70, 400, 90],
                page_number=1,
                type="paragraph",
                metadata={}
            ),
            DocumentElement(
                id="h2_2",
                content="Technical Specifications",
                confidence=0.96,
                bounding_box=[10, 100, 200, 120],
                page_number=1,
                type="heading",
                metadata={"heading_level": 2}
            ),
            DocumentElement(
                id="list1",
                content="1. Must support PDF processing\n2. Should handle complex layouts\n3. Requires high accuracy",
                confidence=0.94,
                bounding_box=[10, 130, 400, 180],
                page_number=1,
                type="list",
                metadata={"list_type": "ordered"}
            )
        ],
        relationships=[
            {"source": "h1_1", "target": "h2_1", "type": "contains"},
            {"source": "h2_1", "target": "p1", "type": "contains"},
            {"source": "h1_1", "target": "h2_2", "type": "contains"},
            {"source": "h2_2", "target": "list1", "type": "contains"}
        ],
        metadata={
            "page_count": 1,
            "language": "en"
        }
    )

@pytest.fixture
async def pipeline():
    """Initialize pipeline with mocked components"""
    with patch.dict(os.environ, {
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "mock_endpoint",
        "AZURE_DOCUMENT_INTELLIGENCE_KEY": "mock_key"
    }):
        return Pipeline(
            persist_directory=":memory:",  # Use in-memory storage for tests
            model_name="test/model"
        )

@pytest.mark.asyncio
async def test_document_processing(pipeline, mock_adi_response, tmp_path):
    """Test full document processing pipeline"""
    # Create test document
    doc_path = tmp_path / "test.txt"
    doc_path.write_text(SAMPLE_DOCUMENT)
    
    # Mock ADI response
    pipeline.adi_processor.analyze_document = Mock(
        return_value=mock_adi_response
    )
    
    # Process document
    doc_id = await pipeline.process_document(str(doc_path))
    
    # Verify document structure was captured
    doc_structure = pipeline.get_document_structure(doc_id)
    assert doc_structure is not None
    assert len(doc_structure.elements) == 5
    assert doc_structure.elements[0].type == "heading"
    assert doc_structure.elements[0].content == "Project Requirements"

@pytest.mark.asyncio
async def test_query_execution(pipeline, mock_adi_response, tmp_path):
    """Test query execution with graph context"""
    # Set up test document
    doc_path = tmp_path / "test.txt"
    doc_path.write_text(SAMPLE_DOCUMENT)
    pipeline.adi_processor.analyze_document = Mock(
        return_value=mock_adi_response
    )
    doc_id = await pipeline.process_document(str(doc_path))
    
    # Execute query
    results = await pipeline.query(
        query_text="What are the technical specifications?",
        document_id=doc_id
    )
    
    # Verify results structure
    assert "vector_results" in results
    assert "graph_results" in results
    
    # Check vector results
    assert "macro" in results["vector_results"]
    assert "micro" in results["vector_results"]
    
    # Verify graph context is included
    if results["graph_results"]:
        assert len(results["graph_results"]) > 0
        first_context = results["graph_results"][0]
        assert hasattr(first_context, "nodes")
        assert hasattr(first_context, "edges")

@pytest.mark.asyncio
async def test_node_context_retrieval(pipeline, mock_adi_response, tmp_path):
    """Test retrieving context around a specific node"""
    # Set up test document
    doc_path = tmp_path / "test.txt"
    doc_path.write_text(SAMPLE_DOCUMENT)
    pipeline.adi_processor.analyze_document = Mock(
        return_value=mock_adi_response
    )
    doc_id = await pipeline.process_document(str(doc_path))
    
    # Get context for first heading
    node_id = mock_adi_response.elements[0].id
    context = pipeline.get_node_context(
        node_id=node_id,
        depth=2,
        include_sections=True
    )
    
    # Verify context structure
    assert "graph_context" in context
    assert "vector_context" in context
    
    # Check graph context
    graph_context = context["graph_context"]
    assert hasattr(graph_context, "nodes")
    assert len(graph_context.nodes) > 0
    
    # Verify vector context includes both chunk types
    vector_context = context["vector_context"]
    assert "macro" in vector_context
    assert "micro" in vector_context

def test_chunking_strategy(pipeline, mock_adi_response):
    """Test dual chunking strategy"""
    # Create chunks
    macro_chunks, micro_chunks = pipeline.chunking_strategy.create_chunks(
        mock_adi_response
    )
    
    # Verify macro chunks
    assert len(macro_chunks) > 0
    for chunk in macro_chunks:
        assert chunk.metadata.chunk_type == "macro"
        assert len(chunk.content.split()) >= pipeline.chunking_strategy.min_macro_length
    
    # Verify micro chunks
    assert len(micro_chunks) > 0
    for chunk in micro_chunks:
        assert chunk.metadata.chunk_type == "micro"
        assert len(chunk.content.split()) <= pipeline.chunking_strategy.max_micro_length
