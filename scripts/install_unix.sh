#!/bin/bash

# Exit on error
set -e

echo "Setting up Local RAG V2 environment..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker."
    echo "Visit: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check Docker Compose installation
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Docker daemon is not running. Please start Docker service:"
    echo "sudo systemctl start docker"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install development dependencies by default
echo "Installing dependencies..."
python -m pip install -e .[dev]

# Make scripts executable
chmod +x scripts/setup_environment.py
chmod +x scripts/manage_docker.py

# Start Docker services
echo "Starting Docker services..."
python scripts/manage_docker.py start

# Run setup script
echo "Running setup script..."
if ! python scripts/setup_environment.py --dev; then
    echo "Setup script failed."
    python scripts/manage_docker.py stop
    exit 1
fi

echo
echo "Installation completed successfully!"
echo
echo "Quick start:"
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo
echo "2. Start ChromaDB (if not running):"
echo "   python scripts/manage_docker.py start"
echo
echo "3. Process a document:"
echo "   ragv2-process path/to/document.pdf"
echo
echo "4. Query the document:"
echo '   ragv2-query "What are the main requirements?"'
echo
echo "5. Stop ChromaDB when done:"
echo "   python scripts/manage_docker.py stop"
echo

# Keep terminal open
read -p "Press Enter to continue..."
