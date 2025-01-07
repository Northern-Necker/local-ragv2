import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional

from ..pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
)
logger = logging.getLogger(__name__)

async def process_document(
    document_path: str,
    persist_dir: Optional[str] = None,
    document_id: Optional[str] = None,
    model_name: str = "microsoft/graphrag-base",
    min_macro_length: int = 100,
    max_micro_length: int = 50,
    overlap_tokens: int = 20
) -> str:
    """Process a document through the pipeline
    
    Args:
        document_path: Path to document file
        persist_dir: Directory for vector store persistence
        document_id: Optional document ID
        model_name: Name of GraphRAG model to use
        min_macro_length: Minimum length for macro chunks
        max_micro_length: Maximum length for micro chunks
        overlap_tokens: Token overlap between chunks
        
    Returns:
        Document ID
    """
    # Initialize pipeline
    pipeline = Pipeline(
        persist_directory=persist_dir or "vector_store",
        model_name=model_name,
        min_macro_length=min_macro_length,
        max_micro_length=max_micro_length,
        overlap_tokens=overlap_tokens
    )
    
    # Process document
    logger.info(f"Processing document: {document_path}")
    doc_id = await pipeline.process_document(
        document_path=document_path,
        document_id=document_id
    )
    
    # Get and log document structure
    doc_structure = pipeline.get_document_structure(doc_id)
    logger.info(f"\nDocument sections:")
    for element in doc_structure.elements:
        if element.type == "heading":
            logger.info(f"- {element.content} (confidence: {element.confidence:.2f})")
    
    logger.info(f"\nDocument processed successfully. ID: {doc_id}")
    return doc_id

def main():
    """Main entry point for document processing CLI"""
    parser = argparse.ArgumentParser(
        description="Process documents with ADI and KAG"
    )
    
    parser.add_argument(
        "document_path",
        type=str,
        help="Path to document file"
    )
    
    parser.add_argument(
        "--persist-dir",
        type=str,
        help="Directory for vector store persistence",
        default="vector_store"
    )
    
    parser.add_argument(
        "--document-id",
        type=str,
        help="Optional document ID"
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        help="Name of GraphRAG model to use",
        default="microsoft/graphrag-base"
    )
    
    parser.add_argument(
        "--min-macro-length",
        type=int,
        help="Minimum length for macro chunks",
        default=100
    )
    
    parser.add_argument(
        "--max-micro-length",
        type=int,
        help="Maximum length for micro chunks",
        default=50
    )
    
    parser.add_argument(
        "--overlap-tokens",
        type=int,
        help="Token overlap between chunks",
        default=20
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verify document path
    document_path = Path(args.document_path)
    if not document_path.exists():
        logger.error(f"Document not found: {document_path}")
        return 1
    
    # Process document
    try:
        asyncio.run(process_document(
            document_path=str(document_path),
            persist_dir=args.persist_dir,
            document_id=args.document_id,
            model_name=args.model_name,
            min_macro_length=args.min_macro_length,
            max_micro_length=args.max_micro_length,
            overlap_tokens=args.overlap_tokens
        ))
        return 0
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
