# Changelog

All notable changes to Local RAG V2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-07

### Added
- Azure Document Intelligence integration for superior layout analysis
- Knowledge-Augmented Graph RAG implementation
- Enhanced dual chunking strategy with section tracking
- Graph-based document relationships
- CLI tools for document processing and querying
- Comprehensive test suite
- Installation scripts for Windows and Unix systems

### Changed
- Complete rewrite of document processing pipeline
- Replaced YOLO with Azure Document Intelligence
- Enhanced vector storage with graph context
- Improved chunking strategy
- Updated configuration system

### Removed
- YOLO-based layout detection
- Legacy chunking system
- Old document structure analyzer

### Dependencies
- Added azure-ai-formrecognizer>=3.2.0
- Added graphrag>=0.1.0
- Updated chromadb>=0.4.0

### Migration
See README.md for migration instructions from V1 to V2.

## [1.0.0] - 2024-12-01

Initial release of Local RAG V1 (for reference).

### Features
- YOLO-based layout detection
- Basic chunking system
- Vector storage with ChromaDB
- Document structure analysis
- Basic CLI tools

[2.0.0]: https://github.com/yourusername/local-ragv2/releases/tag/v2.0.0
[1.0.0]: https://github.com/yourusername/local-ragv1/releases/tag/v1.0.0
