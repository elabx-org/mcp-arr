"""Radarr collection management tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_collections(
    instance: str | None = None,
    tmdb_id: int | None = None,
) -> dict:
    """Get TMDB collections tracked in Radarr.

    Args:
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        tmdb_id: Filter to a specific TMDB collection ID (optional)
    """
    client = resolve_instance(instance, "radarr")
    params: dict = {}
    if tmdb_id is not None:
        params["tmdbId"] = tmdb_id
    result = await client.get("/api/v3/collection", params=params or None)
    return {"collections": result if isinstance(result, list) else []}


@mcp.tool()
async def radarr_get_collection(id: int, instance: str | None = None) -> dict:
    """Get a specific collection by its Radarr ID.

    Args:
        id: Radarr collection ID
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get(f"/api/v3/collection/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def radarr_update_collection(
    id: int,
    instance: str | None = None,
    **fields,
) -> dict:
    """Update a collection's settings.

    Common fields: monitored, qualityProfileId, rootFolderPath, minimumAvailability.

    Args:
        id: Radarr collection ID to update
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        **fields: Fields to update (camelCase API field names)
    """
    client = resolve_instance(instance, "radarr")
    current = await client.get(f"/api/v3/collection/{id}")
    current.update(fields)
    result = await client.put(f"/api/v3/collection/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}
