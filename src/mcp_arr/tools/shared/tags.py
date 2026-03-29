"""Tag management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_tags(instance: str | None = None) -> dict:
    """Get all tags.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/tag")
    return {"tags": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_tag(id: int, instance: str | None = None) -> dict:
    """Get a specific tag by ID.

    Args:
        id: Tag ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/tag/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_tag(label: str, instance: str | None = None) -> dict:
    """Create a new tag.

    Args:
        label: Tag label text
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/tag", data={"label": label})
    return result if isinstance(result, dict) else {"success": True, "label": label}


@mcp.tool()
async def arr_update_tag(id: int, label: str, instance: str | None = None) -> dict:
    """Update a tag's label.

    Args:
        id: Tag ID to update
        label: New label text
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.put(f"/api/v3/tag/{id}", data={"id": id, "label": label})
    return result if isinstance(result, dict) else {"success": True, "id": id, "label": label}


@mcp.tool()
async def arr_delete_tag(id: int, instance: str | None = None) -> dict:
    """Delete a tag by ID.

    Args:
        id: Tag ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/tag/{id}")
    return {"success": True, "id": id, "message": f"Tag {id} deleted"}


@mcp.tool()
async def arr_get_tag_details(instance: str | None = None) -> dict:
    """Get all tags with their linked resources (series/movies, indexers, download clients, etc.).

    Uses the /api/v3/tag/detail endpoint which returns tags with associated resource IDs.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/tag/detail")
    return {"tag_details": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_tag_detail(id: int, instance: str | None = None) -> dict:
    """Get a specific tag with its linked resources by ID.

    Args:
        id: Tag ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/tag/detail/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}
