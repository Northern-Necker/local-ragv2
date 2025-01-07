"""Command-line interface for Local RAG V2"""

from .process import process_document, main as process_main
from .query import query_document, main as query_main

__all__ = [
    'process_document',
    'process_main',
    'query_document',
    'query_main'
]
