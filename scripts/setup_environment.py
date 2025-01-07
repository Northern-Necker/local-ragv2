#!/usr/bin/env python3
"""
Setup script for Local RAG V2 environment.
This script:
1. Verifies Python environment
2. Installs dependencies
3. Sets up Azure Document Intelligence
4. Downloads required models
5. Creates necessary directories
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s'
)
logger = logging.getLogger(__name__)

def verify_python_version():
    """Verify Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def install_dependencies(dev_mode: bool = False):
    """Install required packages"""
    logger.info("Installing dependencies...")
    
    try:
        # Install base requirements
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        
        if dev_mode:
            # Install development dependencies
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
                check=True
            )
        
        logger.info("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {e}")
        sys.exit(1)

def setup_azure_config(
    endpoint: Optional[str] = None,
    key: Optional[str] = None,
    env_file: str = ".env"
):
    """Set up Azure Document Intelligence configuration"""
    logger.info("Setting up Azure Document Intelligence...")
    
    if not endpoint:
        endpoint = input("Enter Azure Document Intelligence endpoint: ").strip()
    if not key:
        key = input("Enter Azure Document Intelligence key: ").strip()
    
    # Write configuration to .env file
    env_path = Path(env_file)
    env_content = [
        "# Azure Document Intelligence Configuration",
        f"AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT={endpoint}",
        f"AZURE_DOCUMENT_INTELLIGENCE_KEY={key}",
        "",
        "# Vector Store Configuration",
        "VECTOR_STORE_DIR=vector_store",
        "",
        "# Model Configuration",
        "GRAPHRAG_MODEL=microsoft/graphrag-base",
        ""
    ]
    
    env_path.write_text("\n".join(env_content))
    logger.info(f"Configuration written to {env_file}")

def create_directories():
    """Create necessary directories"""
    logger.info("Creating directories...")
    
    directories = [
        "vector_store",  # For ChromaDB storage
        "models",        # For downloaded models
        "logs",         # For application logs
        "test_docs"     # For test documents
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def verify_installation():
    """Verify installation by running basic tests"""
    logger.info("Verifying installation...")
    
    try:
        # Run basic tests
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_pipeline.py", "-v"],
            check=True
        )
        logger.info("Installation verified successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error verifying installation: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(
        description="Set up Local RAG V2 environment"
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Install development dependencies"
    )
    
    parser.add_argument(
        "--azure-endpoint",
        type=str,
        help="Azure Document Intelligence endpoint"
    )
    
    parser.add_argument(
        "--azure-key",
        type=str,
        help="Azure Document Intelligence key"
    )
    
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Environment file path"
    )
    
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip installation verification"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Run setup steps
        verify_python_version()
        install_dependencies(args.dev)
        setup_azure_config(args.azure_endpoint, args.azure_key, args.env_file)
        create_directories()
        
        if not args.skip_verify:
            verify_installation()
        
        logger.info("Setup completed successfully!")
        logger.info("\nQuick start:")
        logger.info("1. Process a document:")
        logger.info("   ragv2-process path/to/document.pdf")
        logger.info("\n2. Query the document:")
        logger.info("   ragv2-query \"What are the main requirements?\"")
        
    except KeyboardInterrupt:
        logger.info("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
