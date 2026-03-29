"""FastMCP server for Sonarr/Radarr arr stack management."""

import logging
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .client import ArrClient, ArrError, RadarrClient, SonarrClient
from .config import Config

# Configure logging - use stderr, never stdout (STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create MCP server with transport security allowing Docker hostnames
mcp = FastMCP(
    "arr",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["localhost:*", "127.0.0.1:*", "mcp-arr:*", "0.0.0.0:*"],
    ),
)

# Client registry — populated lazily on first tool call
_clients: dict[str, ArrClient] = {}


def _ensure_clients() -> None:
    """Populate the client registry from configuration if not already done."""
    global _clients
    if _clients:
        return

    Config.validate()
    instances = Config.get_instances()

    for name, cfg in instances.items():
        if cfg.instance_type == "radarr":
            client: ArrClient = RadarrClient(cfg.url, cfg.api_key, name)
        else:
            client = SonarrClient(cfg.url, cfg.api_key, name)
        _clients[name] = client
        logger.info(
            "Registered %s instance '%s' at %s",
            cfg.instance_type,
            name,
            cfg.url,
        )


def get_client(instance: str) -> ArrClient:
    """Get a client for a named instance.

    Args:
        instance: Instance name as configured (e.g., "sonarr", "radarr4k")

    Returns:
        ArrClient for the named instance

    Raises:
        ArrError: If the instance is not configured
    """
    _ensure_clients()
    key = instance.lower()
    if key not in _clients:
        available = list(_clients.keys())
        raise ArrError(
            f"Instance '{instance}' not found. "
            f"Available instances: {available}"
        )
    return _clients[key]


def get_clients_by_type(instance_type: str) -> dict[str, ArrClient]:
    """Get all clients of a given type.

    Args:
        instance_type: "sonarr" or "radarr"

    Returns:
        Dict of instance_name -> ArrClient for all instances of that type
    """
    _ensure_clients()
    return {
        name: client
        for name, client in _clients.items()
        if client.instance_type == instance_type
    }


def get_default_client(instance_type: str) -> ArrClient:
    """Get the first configured instance of a given type.

    Args:
        instance_type: "sonarr" or "radarr"

    Returns:
        First ArrClient of the given type

    Raises:
        ArrError: If no instance of that type is configured
    """
    typed = get_clients_by_type(instance_type)
    if not typed:
        configured = list(_clients.keys())
        raise ArrError(
            f"No {instance_type} instance configured. "
            f"Configured instances: {configured}"
        )
    return next(iter(typed.values()))


def resolve_instance(instance: str | None, instance_type: str) -> ArrClient:
    """Resolve an optional instance name to a client.

    When instance is None, returns the first configured instance of instance_type.
    When instance is provided, returns that specific instance (any type).

    Args:
        instance: Instance name, or None to use the default
        instance_type: Fallback type for default resolution ("sonarr" or "radarr")

    Returns:
        ArrClient for the resolved instance
    """
    if instance is None:
        return get_default_client(instance_type)
    return get_client(instance)


def main() -> None:
    """Run the MCP server."""
    # Validate configuration at startup
    Config.validate()

    # Import all tool modules to register them with the server
    from .tools.shared import (  # noqa: F401
        blocklist,
        calendar,
        commands,
        config,
        delayprofiles,
        download_clients,
        health,
        history,
        importlists,
        indexers,
        manualimport,
        metadata,
        notifications,
        parse,
        profiles,
        queue,
        releases,
        rootfolders,
        system,
        tags,
    )
    from .tools.sonarr import (  # noqa: F401
        episodes,
        history as sonarr_history,
        language,
        releaseprofiles,
        releases as sonarr_releases,
        series,
        wanted as sonarr_wanted,
    )
    from .tools.radarr import (  # noqa: F401
        alternatenames,
        collections,
        credits,
        exclusions,
        genres,
        history as radarr_history,
        movie_files,
        movies,
        releases as radarr_releases,
        wanted as radarr_wanted,
    )

    # Support configurable transport: sse (default) or stdio
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))

    logger.info(
        "Starting arr MCP server (transport=%s, host=%s, port=%s)",
        transport,
        host,
        port,
    )

    if transport == "sse":
        import uvicorn
        app = mcp.sse_app()
        uvicorn.run(app, host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
