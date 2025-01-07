# Use official ChromaDB image as base
FROM ghcr.io/chroma-core/chroma:latest

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV CHROMA_DB_IMPL=duckdb+parquet
ENV CHROMA_SERVER_HOST=0.0.0.0
ENV CHROMA_SERVER_HTTP_PORT=8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/heartbeat || exit 1

# Create data directory with proper permissions
RUN mkdir -p /chroma/chroma && \
    chown -R chroma:chroma /chroma/chroma

# Switch to non-root user
USER chroma

# Expose port
EXPOSE 8000

# Use the default entrypoint and command from the base image
