@echo off
setlocal enabledelayedexpansion

echo Setting up Local RAG V2 environment...

:: Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

:: Check Docker installation
docker --version > nul 2>&1
if errorlevel 1 (
    echo Docker not found. Please install Docker Desktop for Windows.
    echo Visit: https://www.docker.com/products/docker-desktop
    exit /b 1
)

:: Check Docker is running
docker info > nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker Desktop.
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    exit /b 1
)

:: Install development dependencies by default
echo Installing dependencies...
python -m pip install -e .[dev]
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

:: Start Docker services
echo Starting Docker services...
python scripts\manage_docker.py start
if errorlevel 1 (
    echo Failed to start Docker services.
    exit /b 1
)

:: Run setup script
echo Running setup script...
python scripts\setup_environment.py --dev
if errorlevel 1 (
    echo Setup script failed.
    python scripts\manage_docker.py stop
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Quick start:
echo 1. Activate the virtual environment:
echo    .venv\Scripts\activate
echo.
echo 2. Start ChromaDB (if not running):
echo    python scripts\manage_docker.py start
echo.
echo 3. Process a document:
echo    ragv2-process path/to/document.pdf
echo.
echo 4. Query the document:
echo    ragv2-query "What are the main requirements?"
echo.
echo 5. Stop ChromaDB when done:
echo    python scripts\manage_docker.py stop
echo.

:: Keep terminal open
pause
