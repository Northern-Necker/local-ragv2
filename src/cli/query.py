import asyncio
import argparse
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from ..pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
)
logger = logging.getLogger(__name__)

async def query_document(
    query_text: str,
    persist_dir: str,
    document_id: Optional[str] = None,
    max_results: int = 5,
    include_graph_context: bool = True,
    output_format: str = "text"
) -> Dict[str, Any]:
    """Query a processed document
    
    Args:
        query_text: Query text
        persist_dir: Directory with vector store
        document_id: Optional document ID to restrict search
        max_results: Maximum number of results to return
        include_graph_context: Whether to include graph context
        output_format: Output format ('text' or 'json')
        
    Returns:
        Query results
    """
    # Initialize pipeline
    pipeline = Pipeline(
        persist_directory=persist_dir
    )
    
    # Execute query
    logger.info(f"Executing query: {query_text}")
    results = await pipeline.query(
        query_text=query_text,
        document_id=document_id,
        max_results=max_results,
        include_graph_context=include_graph_context
    )
    
    # Format and display results
    if output_format == "json":
        # Return raw results for JSON output
        return results
    else:
        # Display results in text format
        logger.info("\nVector Results:")
        for i, result in enumerate(results["vector_results"]["macro"], 1):
            logger.info(f"\n{i}. Relevance: {1 - result['distance']:.2f}")
            logger.info(f"Content: {result['content'][:200]}...")
        
        if results["graph_results"]:
            logger.info("\nGraph Context:")
            for context in results["graph_results"]:
                logger.info(f"\nRelevance: {context.relevance_score:.2f}")
                logger.info(f"Connected nodes: {len(context.nodes)}")
                logger.info(f"First node content: {context.nodes[0].content[:200]}...")
        
        return results

def main():
    """Main entry point for document querying CLI"""
    parser = argparse.ArgumentParser(
        description="Query processed documents with ADI and KAG"
    )
    
    parser.add_argument(
        "query_text",
        type=str,
        help="Query text"
    )
    
    parser.add_argument(
        "--persist-dir",
        type=str,
        help="Directory with vector store",
        default="vector_store"
    )
    
    parser.add_argument(
        "--document-id",
        type=str,
        help="Optional document ID to restrict search"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        help="Maximum number of results to return",
        default=5
    )
    
    parser.add_argument(
        "--no-graph-context",
        action="store_true",
        help="Disable graph context in results"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json)"
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        help="Optional file to write results to"
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
    
    # Verify vector store exists
    persist_dir = Path(args.persist_dir)
    if not persist_dir.exists():
        logger.error(f"Vector store not found: {persist_dir}")
        return 1
    
    # Execute query
    try:
        results = asyncio.run(query_document(
            query_text=args.query_text,
            persist_dir=str(persist_dir),
            document_id=args.document_id,
            max_results=args.max_results,
            include_graph_context=not args.no_graph_context,
            output_format=args.output
        ))
        
        # Write results if output file specified
        if args.output_file:
            output_path = Path(args.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.output == "json":
                # Convert results to JSON-serializable format
                json_results = {
                    "vector_results": results["vector_results"],
                    "graph_results": [
                        {
                            "relevance_score": ctx.relevance_score,
                            "nodes": [
                                {
                                    "content": node.content,
                                    "type": node.type,
                                    "metadata": node.metadata
                                }
                                for node in ctx.nodes
                            ],
                            "edges": [
                                {
                                    "source": edge.source,
                                    "target": edge.target,
                                    "type": edge.type,
                                    "weight": edge.weight
                                }
                                for edge in ctx.edges
                            ]
                        }
                        for ctx in results["graph_results"]
                    ] if results["graph_results"] else None
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_results, f, indent=2, ensure_ascii=False)
            else:
                # Write text output
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Query: {args.query_text}\n\n")
                    
                    f.write("Vector Results:\n")
                    for i, result in enumerate(results["vector_results"]["macro"], 1):
                        f.write(f"\n{i}. Relevance: {1 - result['distance']:.2f}\n")
                        f.write(f"Content: {result['content'][:200]}...\n")
                    
                    if results["graph_results"]:
                        f.write("\nGraph Context:\n")
                        for context in results["graph_results"]:
                            f.write(f"\nRelevance: {context.relevance_score:.2f}\n")
                            f.write(f"Connected nodes: {len(context.nodes)}\n")
                            f.write(f"First node content: {context.nodes[0].content[:200]}...\n")
            
            logger.info(f"\nResults written to: {output_path}")
        
        return 0
    except Exception as e:
        logger.error(f"Error executing query: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
