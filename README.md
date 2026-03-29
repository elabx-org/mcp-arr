# mcp-arr

MCP server for managing Sonarr and Radarr arr stack instances.

## Features

- Full Sonarr v3 API coverage: series, episodes, releases, wanted, language profiles, history
- Full Radarr v3 API coverage: movies, movie files, releases, wanted, collections, credits, exclusions
- Shared tools for both: queue, calendar, health, system, tags, notifications, blocklist, commands, indexers, download clients, profiles, custom formats, root folders, history, metadata, parse, manual import
- Multi-instance support — configure multiple Sonarr/Radarr instances, target any by name
- TRaSH Guides custom format sync
- Pure planning tool for optimal release grab strategies

## Configuration

Instances are configured via environment variables using the pattern `ARR_{NAME}_URL`, `ARR_{NAME}_KEY`, and optionally `ARR_{NAME}_TYPE` (defaults to `sonarr`).

```bash
# Sonarr instance named "SONARR"
ARR_SONARR_URL=http://sonarr:8989
ARR_SONARR_KEY=your_api_key_here
ARR_SONARR_TYPE=sonarr  # optional, defaults to sonarr

# Second Sonarr instance named "SONARRANI"
ARR_SONARRANI_URL=http://sonarrani:8989
ARR_SONARRANI_KEY=your_api_key_here

# 4K Sonarr instance
ARR_SONARR4K_URL=http://sonarr4k:8989
ARR_SONARR4K_KEY=your_api_key_here

# Radarr instance named "RADARR"
ARR_RADARR_URL=http://radarr:7878
ARR_RADARR_KEY=your_api_key_here
ARR_RADARR_TYPE=radarr

# 4K Radarr instance
ARR_RADARR4K_URL=http://radarr4k:7878
ARR_RADARR4K_KEY=your_api_key_here
ARR_RADARR4K_TYPE=radarr
```

## Transport

- `MCP_TRANSPORT=sse` — HTTP SSE transport (default for Docker, port 8000)
- `MCP_TRANSPORT=stdio` — stdio transport (for local MCP client use)

## Docker

```bash
docker-compose up -d
```

The server will be available at `http://localhost:8000/sse`.

## Development

```bash
pip install -e .
ARR_SONARR_URL=http://localhost:8989 ARR_SONARR_KEY=your_key mcp-arr
```
