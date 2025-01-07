# Contributing to Local RAG V2

Thank you for your interest in contributing to Local RAG V2! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/local-ragv2.git
cd local-ragv2
```

2. Install development dependencies:
```bash
# Windows
scripts\install_windows.bat

# Unix/macOS
./scripts/install_unix.sh
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure Document Intelligence credentials
```

## Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following our coding standards:
- Use type hints
- Follow PEP 8 style guide
- Add docstrings for new functions/classes
- Update tests as needed

3. Run tests:
```bash
pytest
```

4. Format code:
```bash
black src tests
isort src tests
```

5. Submit a pull request:
- Write a clear PR description
- Link related issues
- Include test results

## Project Structure

```
local-ragv2/
├── src/
│   ├── document_processors/  # Document analysis components
│   ├── graph_rag/           # Graph RAG implementation
│   ├── storage/             # Vector storage
│   └── cli/                 # Command-line interface
├── tests/                   # Test suite
├── scripts/                 # Installation and utility scripts
└── docs/                    # Documentation
```

## Testing

- Write tests for new features
- Update existing tests when modifying code
- Ensure all tests pass before submitting PR
- Maintain test coverage above 80%

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_pipeline.py

# Run with coverage
pytest --cov=src

# Run specific test category
pytest -m "not slow"
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new code
- Update example scripts if needed
- Keep architecture documentation current

## Code Style

We use:
- Black for code formatting
- isort for import sorting
- mypy for type checking
- pylint for linting

### Style Guide

1. Type Hints:
```python
def process_document(
    document_path: str,
    options: Optional[Dict[str, Any]] = None
) -> str:
    """Process a document with optional configuration.
    
    Args:
        document_path: Path to document file
        options: Optional processing configuration
        
    Returns:
        Document ID
    """
    ...
```

2. Error Handling:
```python
try:
    result = await process_document(path)
except DocumentProcessingError as e:
    logger.error(f"Failed to process document: {e}")
    raise
```

3. Async/Await:
- Use async/await consistently
- Handle cancellation properly
- Use asyncio primitives appropriately

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Run full test suite
4. Format code
5. Update CHANGELOG.md
6. Submit PR with clear description

## Release Process

1. Version Bump:
- Update version in setup.py
- Update CHANGELOG.md
- Create release commit

2. Testing:
- Run full test suite
- Test installation process
- Verify documentation

3. Release:
- Create GitHub release
- Tag version
- Upload to PyPI

## Getting Help

- Open an issue for bugs
- Use discussions for questions
- Join our community chat

## Code of Conduct

Please follow our code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Maintain professional discourse

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
