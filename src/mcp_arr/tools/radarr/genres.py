"""Radarr genre management tools."""

from typing import Any

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_list_genres(instance: str | None = None) -> list[dict[str, Any]]:
    """List all genres known to a Radarr instance.

    Returns the list of genres that have been seen across all movies in the library.
    Genres come from TMDb metadata and are attached to movies automatically.

    Args:
        instance: Radarr instance name. Uses default Radarr instance if not specified.

    Returns:
        List of genre names as strings.
    """
    client = resolve_instance(instance, "radarr")
    return await client.get("/api/v3/genre")
