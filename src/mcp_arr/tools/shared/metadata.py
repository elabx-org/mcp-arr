"""Metadata provider tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_metadata_providers(instance: str | None = None) -> dict:
    """Get all configured metadata providers.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/metadata")
    return {"metadata_providers": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_metadata_provider(id: int, instance: str | None = None) -> dict:
    """Get a specific metadata provider by ID.

    Args:
        id: Metadata provider ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/metadata/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_update_metadata_provider(
    id: int,
    instance: str | None = None,
    **fields,
) -> dict:
    """Update a metadata provider configuration.

    Fetches the current provider configuration and merges the provided fields.
    Use camelCase field names as returned by the API.

    Args:
        id: Metadata provider ID to update
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        **fields: Fields to update (e.g., enable=True, fields=[...])
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/metadata/{id}")
    current.update(fields)
    result = await client.put(f"/api/v3/metadata/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}
