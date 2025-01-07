# Local RAG V2

Enhanced document analysis with Azure Document Intelligence and Knowledge-Augmented Graph RAG.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/local-ragv2.git
cd local-ragv2
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Azure Document Intelligence credentials
```

5. Start ChromaDB:
```bash
# Start Docker container
docker-compose up -d chromadb

# Verify status
python scripts/manage_docker.py status
```

## Usage

1. Process a document:
```bash
ragv2-process path/to/document.pdf
```

2. Query the document:
```bash
ragv2-query "What are the main requirements?"
```

3. Stop ChromaDB when done:
```bash
python scripts/manage_docker.py stop
```

## GitHub Setup

### Repository Setup
1. Create a new repository on GitHub
2. Push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/local-ragv2.git
git push -u origin main
```

### GitHub Actions Setup
1. Go to your repository's Settings > Secrets and variables > Actions
2. Add these repository secrets:
   - `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
   - `AZURE_DOCUMENT_INTELLIGENCE_KEY`

### Free GitHub Features Used
1. **GitHub Actions** (CI/CD):
   - Automated testing on Python 3.8, 3.9, 3.10
   - Test coverage reports
   - Docker image builds
   - Runs on every push and pull request

2. **GitHub Container Registry**:
   - Stores Docker images securely
   - Free for public repositories
   - Access via: `ghcr.io/yourusername/local-ragv2`

3. **Security Features**:
   - CodeQL Analysis (Static Application Security Testing)
   - Dependabot security updates
   - Secret scanning
   - Docker image vulnerability scanning
   - Weekly security scans
   - Automated security fixes

4. **Dependabot**:
   - Automated dependency updates
   - Security vulnerability scanning
   - Auto-merges minor/patch updates

### Security Features
1. **CodeQL Analysis**:
   - Automatically scans code for vulnerabilities
   - Supports Python security best practices
   - Results visible in Security tab

2. **Secret Scanning**:
   - Detects accidentally committed secrets
   - Supports Azure credentials
   - Immediate notifications

3. **Docker Security**:
   - Container vulnerability scanning
   - Base image security checks
   - Dependency scanning

4. **Dependency Management**:
   - Automated version updates
   - Known vulnerability alerts
   - Compatibility checking

### Common Git Commands
```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

### GitHub Actions Status
You can monitor CI/CD status:
1. Go to repository's Actions tab
2. View test results and Docker builds
3. Check Dependabot alerts and updates

### Sensitive Data
- Never commit sensitive data (API keys, credentials)
- Use repository secrets for sensitive values
- Use .env for local configuration
- .gitignore is configured to exclude sensitive files

## Architecture

### Document Processing
- Azure Document Intelligence for layout analysis
- Knowledge-Augmented Graph RAG for context
- ChromaDB for vector storage (Dockerized)
- Dual chunking strategy with section tracking

### Key Features
- Superior layout analysis
- Graph-based document relationships
- Cross-platform compatibility
- Easy-to-use CLI tools

## License

MIT License - see [LICENSE](LICENSE) for details.
