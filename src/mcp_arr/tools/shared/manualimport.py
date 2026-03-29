"""Manual import tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_manual_import(
    instance: str | None = None,
    download_id: str | None = None,
    folder: str | None = None,
    filter_existing_files: bool = True,
) -> dict:
    """Get files available for manual import.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        download_id: Filter by download client task ID (optional)
        folder: Filesystem folder path to scan for importable files (optional)
        filter_existing_files: Exclude files that already exist in the library (default True)
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {"filterExistingFiles": filter_existing_files}
    if download_id:
        params["downloadId"] = download_id
    if folder:
        params["folder"] = folder
    result = await client.get("/api/v3/manualimport", params=params)
    return {"files": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_update_manual_import(
    files: list[dict],
    instance: str | None = None,
) -> dict:
    """Update manual import file mappings and trigger the import.

    Args:
        files: List of file import dicts. Each dict should contain the fields
            returned by arr_get_manual_import, updated with correct series/episode/movie
            IDs and quality information. At minimum: path, seriesId/movieId, quality.
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.put("/api/v3/manualimport", data=files)
    return result if isinstance(result, dict) else {"success": True, "files_processed": len(files)}


@mcp.tool()
async def arr_force_import_download(
    download_id: str,
    instance: str | None = None,
    import_mode: str = "Move",
) -> dict:
    """Force import a completed download, replacing any existing file at the same quality.

    Use this for Option B replacements — when you've grabbed a new release but Sonarr
    would normally reject the import because a file at the same quality already exists
    (e.g., replacing a torrent Remux with a usenet Remux from a better release group).

    Workflow:
    1. Use arr_grab_release to grab the new release — it downloads via usenet/torrent.
    2. Wait for the download to complete (check activity queue with arr_get_queue).
    3. Call this tool with the download_id from the queue item to force the import,
       bypassing Sonarr's "already have this quality" rejection.

    Args:
        download_id: Download client task ID — get this from arr_get_queue after the
            download completes. It's the "downloadId" field on the queue item.
        import_mode: "Move" (default) or "Copy". Move removes the source file after
            import; Copy keeps it in the download client's folder.
        instance: Instance name (e.g., "sonarr", "radarr"). Uses default if not specified.

    Returns:
        Command result with status. The import runs asynchronously — check Sonarr's
        Activity > Queue to confirm the file was replaced.
    """
    client = resolve_instance(instance, "sonarr")

    # Step 1: Get the importable files for this download, ignoring existing file filter
    files = await client.get(
        "/api/v3/manualimport",
        params={"downloadId": download_id, "filterExistingFiles": False},
    )
    if not files:
        return {
            "success": False,
            "download_id": download_id,
            "error": "No importable files found for this download ID. "
                     "Check that the download is complete and the ID is correct.",
        }

    # Step 2: Check rejections — skip any file blocked for sample-related reasons.
    # We only want to bypass quality-upgrade rejections, not legitimate content warnings.
    _SAMPLE_PHRASES = [
        "sample",
        "unable to determine if file is a sample",
    ]

    import_files = []
    skipped = []

    for f in files:
        rejections = f.get("rejections", [])
        sample_rejections = [
            r.get("reason", "") for r in rejections
            if any(phrase in r.get("reason", "").lower() for phrase in _SAMPLE_PHRASES)
        ]
        if sample_rejections:
            skipped.append({
                "path": f.get("path"),
                "reason": "sample_rejection",
                "rejection_messages": sample_rejections,
            })
            continue

        entry: dict = {
            "path": f.get("path"),
            "importMode": import_mode,
            "releaseGroup": f.get("releaseGroup", ""),
            "quality": f.get("quality"),
        }
        # Sonarr fields
        if "seriesId" in f:
            entry["seriesId"] = f["seriesId"]
            entry["episodeIds"] = [e["id"] for e in f.get("episodes", [])]
            entry["seasonNumber"] = f.get("seasonNumber")
        # Radarr fields
        if "movieId" in f:
            entry["movieId"] = f["movieId"]
        import_files.append(entry)

    if skipped and not import_files:
        return {
            "success": False,
            "download_id": download_id,
            "error": "All files blocked by sample rejection — not force importing.",
            "skipped": skipped,
        }

    result = None
    if import_files:
        command = {
            "name": "ManualImport",
            "files": import_files,
            "importMode": import_mode,
            "replaceExistingFiles": True,
        }
        result = await client.post("/api/v3/command", data=command)

    return {
        "success": True,
        "download_id": download_id,
        "files_queued": len(import_files),
        "files": [f.get("path") for f in import_files],
        "skipped_sample": skipped,
        "command": result,
    }
