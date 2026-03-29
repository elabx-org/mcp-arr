FROM python:3.12-slim

WORKDIR /app

# Copy all source files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir .

# Environment variables (set at runtime)
ENV ARR_SONARR_URL=""
ENV ARR_SONARR_KEY=""
ENV ARR_SONARR_TYPE="sonarr"
ENV ARR_RADARR_URL=""
ENV ARR_RADARR_KEY=""
ENV ARR_RADARR_TYPE="radarr"
ENV MCP_TRANSPORT="sse"
ENV MCP_PORT="8000"

# Expose port for SSE transport
EXPOSE 8000

# Run server
ENTRYPOINT ["python", "-m", "mcp_arr"]
