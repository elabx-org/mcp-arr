"""Queue management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_queue(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    include_unknown_series_items: bool = False,
    include_blocklisted: bool = False,
) -> dict:
    """Get the download queue for a Sonarr or Radarr instance.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
        page: Page number (1-based)
        page_size: Number of items per page
        include_unknown_series_items: Include items with unknown series/movie
        include_blocklisted: Include blocklisted items
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    params: dict = {
        "page": page,
        "pageSize": page_size,
        "includeUnknownSeriesItems": include_unknown_series_items,
        "includeBlocklisted": include_blocklisted,
    }
    result = await client.get("/api/v3/queue", params=params)
    records = result.get("records", []) if isinstance(result, dict) else result
    return {
        "page": result.get("page", page) if isinstance(result, dict) else page,
        "page_size": result.get("pageSize", page_size) if isinstance(result, dict) else page_size,
        "total_records": result.get("totalRecords", len(records)) if isinstance(result, dict) else len(records),
        "records": records,
    }


@mcp.tool()
async def arr_get_queue_status(instance: str | None = None) -> dict:
    """Get queue status summary (total count, pending, downloading, etc.).

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    result = await client.get("/api/v3/queue/status")
    return result if isinstance(result, dict) else {"status": result}


@mcp.tool()
async def arr_delete_queue_item(
    id: int,
    instance: str | None = None,
    blocklist: bool = True,
    remove_from_client: bool = True,
    change_category: bool = False,
) -> dict:
    """Delete a single queue item.

    Args:
        id: Queue item ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
        blocklist: Add to blocklist to prevent re-grabbing the same release (default True)
        remove_from_client: Remove from the download client as well (default True)
        change_category: Change the download client category instead of removing (default False)
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    params = {
        "blocklist": blocklist,
        "removeFromClient": remove_from_client,
        "changeCategory": change_category,
    }
    await client.delete(f"/api/v3/queue/{id}", params=params)
    return {"success": True, "id": id, "message": f"Queue item {id} deleted"}


@mcp.tool()
async def arr_delete_queue_bulk(
    ids: list[int],
    instance: str | None = None,
    blocklist: bool = True,
    remove_from_client: bool = True,
) -> dict:
    """Delete multiple queue items at once.

    Args:
        ids: List of queue item IDs to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
        blocklist: Add items to blocklist to prevent re-grabbing (default True)
        remove_from_client: Remove from download client as well (default True)
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    data = {
        "ids": ids,
        "blocklist": blocklist,
        "removeFromClient": remove_from_client,
    }
    await client.delete("/api/v3/queue/bulk", params=data)
    return {"success": True, "ids": ids, "message": f"Deleted {len(ids)} queue items"}


@mcp.tool()
async def arr_grab_queue_item(id: int, instance: str | None = None) -> dict:
    """Re-grab / retry a pending queue item.

    Args:
        id: Queue item ID to re-grab
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    result = await client.post(f"/api/v3/queue/grab/{id}")
    return result if isinstance(result, dict) else {"success": True, "id": id}
