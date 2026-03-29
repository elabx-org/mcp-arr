"""History tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_history(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_key: str = "date",
    sort_dir: str = "descending",
    event_type: int | None = None,
    download_id: str | None = None,
) -> dict:
    """Get paginated history records.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        sort_key: Field to sort by (default "date")
        sort_dir: Sort direction: "ascending" or "descending" (default "descending")
        event_type: Filter by event type integer (e.g., 1=grabbed, 3=downloadFailed)
        download_id: Filter by download client ID string
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {
        "page": page,
        "pageSize": page_size,
        "sortKey": sort_key,
        "sortDirection": sort_dir,
    }
    if event_type is not None:
        params["eventType"] = event_type
    if download_id is not None:
        params["downloadId"] = download_id
    result = await client.get("/api/v3/history", params=params)
    return result if isinstance(result, dict) else {"records": result}


@mcp.tool()
async def arr_get_history_since(
    instance: str | None = None,
    date: str | None = None,
    event_type: int | None = None,
) -> dict:
    """Get history records since a given date.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        date: ISO 8601 date string (e.g., "2024-01-01T00:00:00Z"). When None,
            returns the most recent records.
        event_type: Filter by event type integer (optional)
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {}
    if date:
        params["date"] = date
    if event_type is not None:
        params["eventType"] = event_type
    result = await client.get("/api/v3/history/since", params=params)
    return {"records": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_mark_history_failed(id: int, instance: str | None = None) -> dict:
    """Mark a history record as failed, triggering a search for a replacement.

    Args:
        id: History record ID to mark as failed
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.post(f"/api/v3/history/failed/{id}")
    return {"success": True, "id": id, "message": f"History record {id} marked as failed"}
