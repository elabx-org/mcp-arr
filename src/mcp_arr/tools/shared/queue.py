"""Queue management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_stalled_downloads(
    instance: str | None = None,
    stall_threshold_minutes: int = 30,
) -> dict:
    """Find downloads that are stuck or stalled in the queue.

    Fetches all queue items and classifies each as stalled based on its
    trackedDownloadStatus, trackedDownloadState, and statusMessages.

    Stall categories returned:
    - warning: Sonarr/Radarr has flagged the item with a warning
      (e.g. "no files found", "import blocked by existing file")
    - error: Item is in an error state (download failed, unpack error, etc.)
    - import_pending_long: Download completed but stuck in importPending
      longer than stall_threshold_minutes (may need force import)
    - stalled: Download client reports no peers/sources (torrent) or
      the item has no estimated completion and zero download speed

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
        stall_threshold_minutes: How long (minutes) an importPending item must
            sit before being flagged as stalled (default 30).

    Returns:
        Dict with categorised stalled items and a summary count per category.
    """
    import datetime

    client = get_client(instance) if instance else resolve_instance(None, "sonarr")

    # Fetch all pages
    all_records: list[dict] = []
    page = 1
    while True:
        result = await client.get(
            "/api/v3/queue",
            params={
                "page": page,
                "pageSize": 100,
                "includeUnknownSeriesItems": True,
            },
        )
        records = result.get("records", []) if isinstance(result, dict) else []
        all_records.extend(records)
        total = result.get("totalRecords", 0) if isinstance(result, dict) else 0
        if len(all_records) >= total or not records:
            break
        page += 1

    stalled: dict[str, list[dict]] = {
        "warning": [],
        "error": [],
        "import_pending_long": [],
        "stalled": [],
    }

    now = datetime.datetime.now(datetime.timezone.utc)

    for item in all_records:
        status = (item.get("trackedDownloadStatus") or "").lower()
        state = (item.get("trackedDownloadState") or "").lower()
        messages = item.get("statusMessages") or []
        title = item.get("title", "")
        item_id = item.get("id")
        download_id = item.get("downloadId", "")

        summary = {
            "id": item_id,
            "title": title,
            "download_id": download_id,
            "status": status,
            "state": state,
            "protocol": item.get("protocol", ""),
            "indexer": item.get("indexer", ""),
            "messages": [
                msg.get("title", "") + ": " + ", ".join(msg.get("messages", []))
                for msg in messages
                if msg.get("title") or msg.get("messages")
            ],
        }

        if status == "warning":
            stalled["warning"].append(summary)
        elif status == "error":
            stalled["error"].append(summary)
        elif state == "importpending":
            # Check how long it's been sitting in importPending
            added_str = item.get("added") or item.get("estimatedCompletionTime")
            flagged = False
            if added_str:
                try:
                    added = datetime.datetime.fromisoformat(
                        added_str.replace("Z", "+00:00")
                    )
                    minutes_waiting = (now - added).total_seconds() / 60
                    if minutes_waiting > stall_threshold_minutes:
                        summary["minutes_in_import_pending"] = round(minutes_waiting)
                        stalled["import_pending_long"].append(summary)
                        flagged = True
                except ValueError:
                    pass
            if not flagged and messages:
                stalled["import_pending_long"].append(summary)
        elif state in ("downloading", "queued"):
            # Stalled if no speed and no ETA (torrent: no peers)
            sizeleft = item.get("sizeleft", -1)
            timeleft = item.get("timeleft")  # "HH:MM:SS" or null
            if sizeleft == 0:
                continue  # completed, not stalled
            if timeleft is None and sizeleft > 0:
                stalled["stalled"].append(summary)

    return {
        "summary": {cat: len(items) for cat, items in stalled.items()},
        "total_stalled": sum(len(v) for v in stalled.values()),
        "items": stalled,
    }


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
