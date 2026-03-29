"""Blocklist management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_blocklist(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_key: str = "date",
    sort_dir: str = "descending",
) -> dict:
    """Get paginated blocklist entries (releases that were grabbed but failed).

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        sort_key: Field to sort by (default "date")
        sort_dir: Sort direction: "ascending" or "descending" (default "descending")
    """
    client = resolve_instance(instance, "sonarr")
    params = {
        "page": page,
        "pageSize": page_size,
        "sortKey": sort_key,
        "sortDirection": sort_dir,
    }
    result = await client.get("/api/v3/blocklist", params=params)
    return result if isinstance(result, dict) else {"records": result}


@mcp.tool()
async def arr_delete_blocklist(id: int, instance: str | None = None) -> dict:
    """Remove a specific entry from the blocklist.

    Args:
        id: Blocklist entry ID to remove
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/blocklist/{id}")
    return {"success": True, "id": id, "message": f"Blocklist entry {id} removed"}


@mcp.tool()
async def arr_delete_blocklist_bulk(ids: list[int], instance: str | None = None) -> dict:
    """Remove multiple entries from the blocklist at once.

    Args:
        ids: List of blocklist entry IDs to remove
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete("/api/v3/blocklist/bulk", params={"ids": ids})
    return {"success": True, "ids": ids, "message": f"Removed {len(ids)} blocklist entries"}
