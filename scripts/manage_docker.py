#!/usr/bin/env python3
"""
Docker management script for Local RAG V2.
Handles ChromaDB container lifecycle.
"""

import argparse
import subprocess
import sys
import time
import logging
from pathlib import Path
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s'
)
logger = logging.getLogger(__name__)

def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def check_compose_installed() -> bool:
    """Check if Docker Compose is installed"""
    try:
        subprocess.run(
            ["docker-compose", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def is_container_running(service_name: str = "chromadb") -> bool:
    """Check if a container is running
    
    Args:
        service_name: Name of the service to check
        
    Returns:
        True if running, False otherwise
    """
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "-q", service_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def wait_for_service(url: str, timeout: int = 60) -> bool:
    """Wait for a service to become available
    
    Args:
        url: URL to check
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if service is available, False otherwise
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False

def start_services():
    """Start Docker services"""
    logger.info("Starting Docker services...")
    
    # Check Docker installation
    if not check_docker_installed():
        logger.error("Docker is not installed or not running")
        sys.exit(1)
    
    if not check_compose_installed():
        logger.error("Docker Compose is not installed")
        sys.exit(1)
    
    # Start services
    try:
        subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True
        )
        
        # Wait for ChromaDB to be ready
        logger.info("Waiting for ChromaDB to start...")
        if wait_for_service("http://localhost:8000/api/v1/heartbeat"):
            logger.info("ChromaDB is ready")
        else:
            logger.error("ChromaDB failed to start")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start services: {e}")
        sys.exit(1)

def stop_services():
    """Stop Docker services"""
    logger.info("Stopping Docker services...")
    try:
        subprocess.run(
            ["docker-compose", "down"],
            check=True
        )
        logger.info("Services stopped")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop services: {e}")
        sys.exit(1)

def restart_services():
    """Restart Docker services"""
    stop_services()
    start_services()

def check_status():
    """Check status of services"""
    if is_container_running():
        logger.info("ChromaDB is running")
        try:
            response = requests.get("http://localhost:8000/api/v1/heartbeat")
            if response.status_code == 200:
                logger.info("ChromaDB is healthy")
            else:
                logger.warning("ChromaDB is running but may not be healthy")
        except requests.RequestException:
            logger.warning("ChromaDB is running but not responding")
    else:
        logger.info("ChromaDB is not running")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage Docker services for Local RAG V2"
    )
    
    parser.add_argument(
        "action",
        choices=["start", "stop", "restart", "status"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    # Change to directory containing docker-compose.yml
    os.chdir(Path(__file__).parent.parent)
    
    if args.action == "start":
        start_services()
    elif args.action == "stop":
        stop_services()
    elif args.action == "restart":
        restart_services()
    elif args.action == "status":
        check_status()

if __name__ == "__main__":
    main()
