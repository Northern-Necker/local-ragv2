import asyncio
import os
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv

# Add parent directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline import Pipeline

async def main():
    """Example of processing a document with the new pipeline"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize pipeline
    pipeline = Pipeline(
        persist_directory="vector_store",
        model_name="microsoft/graphrag-base",
        min_macro_length=100,  # Words
        max_micro_length=50,   # Words
        overlap_tokens=20
    )
    
    # Process a document
    document_path = "test_docs/sample.pdf"  # Replace with your document
    document_id = await pipeline.process_document(document_path)
    print(f"\nProcessed document: {document_id}")
    
    # Get document structure
    doc_structure = pipeline.get_document_structure(document_id)
    print("\nDocument sections:")
    for element in doc_structure.elements:
        if element.type == "heading":
            print(f"- {element.content} (confidence: {element.confidence:.2f})")
    
    # Example queries
    queries = [
        "What are the main requirements?",
        "Find sections about technical specifications",
        "Summarize the project scope"
    ]
    
    print("\nExecuting queries:")
    for query in queries:
        print(f"\nQuery: {query}")
        results = await pipeline.query(
            query_text=query,
            document_id=document_id,
            max_results=3,
            include_graph_context=True
        )
        
        # Print vector results
        print("\nVector results:")
        for i, result in enumerate(results["vector_results"]["macro"], 1):
            print(f"{i}. {result['content'][:200]}...")
        
        # Print graph context
        if results["graph_results"]:
            print("\nGraph context:")
            for context in results["graph_results"]:
                print(f"- Relevance: {context.relevance_score:.2f}")
                print(f"- Connected nodes: {len(context.nodes)}")
                print(f"- First node content: {context.nodes[0].content[:200]}...")
    
    # Example of getting node context
    if doc_structure.elements:
        first_node = doc_structure.elements[0]
        print(f"\nContext for node {first_node.id}:")
        context = pipeline.get_node_context(
            node_id=first_node.id,
            depth=2,
            include_sections=True
        )
        
        print("\nGraph neighbors:")
        for node in context["graph_context"].nodes:
            print(f"- {node.type}: {node.content[:100]}...")
        
        print("\nSimilar vectors:")
        for result in context["vector_context"]["micro"]:
            print(f"- {result['content'][:100]}...")

if __name__ == "__main__":
    # Set up environment
    os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"] = "your_endpoint_here"
    os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"] = "your_key_here"
    
    # Run example
    asyncio.run(main())
