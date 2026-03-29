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
    """Reprocess/validate manual import file mappings (does not trigger import).

    Sends updated file mappings to Sonarr/Radarr for re-evaluation and returns
    the files with updated rejection status. Use this to verify mappings before
    triggering the actual import via arr_force_import_download.

    Args:
        files: List of file import dicts with updated series/episode/movie ID
            mappings. Use the structure returned by arr_get_manual_import.
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/manualimport", data=files)
    return {"files": result if isinstance(result, list) else [], "reprocessed": len(files)}


@mcp.tool()
async def arr_force_import_download(
    download_id: str,
    instance: str | None = None,
    import_mode: str = "Move",
    strategy: str = "force",
) -> dict:
    """Handle completed downloads blocked by Sonarr/Radarr's upgrade check.

    When a download completes but sits in importPending because Sonarr/Radarr
    rejects it as "not an upgrade", use this tool to push it through.

    Three strategies:

    **force** (Option B — default): Issue a ManualImport command with
    replaceExistingFiles=True. The new file atomically replaces the existing one.
    Best when you want an immediate swap with no gap in availability.

    **delete_existing** (Option A.1): Delete the existing episode/movie files first,
    then return. Sonarr/Radarr will auto-import on its next queue check cycle since
    the episode now has no file. Best when you prefer Sonarr to handle import
    naturally without a force command.

    Workflow for both strategies:
    1. Use arr_grab_release to grab the new release.
    2. Wait for it to complete (arr_get_queue shows status="completed",
       trackedDownloadState="importPending").
    3. Call this tool with the downloadId from the queue item.

    Args:
        download_id: Download client task ID from arr_get_queue ("downloadId" field).
        import_mode: "Move" (default) or "Copy". Move deletes source after import.
            Only applies to strategy="force".
        strategy: "force" (default) or "delete_existing".
        instance: Instance name (e.g., "sonarr", "radarr"). Uses default if not specified.

    Returns:
        For strategy="force": command result — check arr_get_queue to confirm import.
        For strategy="delete_existing": list of deleted file IDs — Sonarr auto-imports.
    """
    client = resolve_instance(instance, "sonarr")

    # Step 1: Get importable files, bypassing existing-file filter
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

    # Step 2: Skip files with sample-related rejections — only bypass upgrade rejections.
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
        import_files.append(f)

    if skipped and not import_files:
        return {
            "success": False,
            "download_id": download_id,
            "error": "All files blocked by sample rejection — not force importing.",
            "skipped": skipped,
        }

    # --- Strategy: delete_existing (Option A.1) ---
    if strategy == "delete_existing":
        deleted = []
        for f in import_files:
            # Sonarr: delete existing episode files referenced in the mapped episodes
            for ep in f.get("episodes", []):
                file_id = ep.get("episodeFileId")
                if file_id:
                    await client.delete(f"/api/v3/episodefile/{file_id}")
                    deleted.append({"episodeFileId": file_id})
            # Radarr: delete existing movie file
            movie = f.get("movie") or {}
            movie_file_id = f.get("movieFileId") or movie.get("movieFileId")
            if movie_file_id:
                await client.delete(f"/api/v3/moviefile/{movie_file_id}")
                deleted.append({"movieFileId": movie_file_id})
        return {
            "success": True,
            "strategy": "delete_existing",
            "download_id": download_id,
            "deleted_files": deleted,
            "skipped_sample": skipped,
            "note": "Existing files deleted. Sonarr/Radarr will auto-import on next queue check.",
        }

    # --- Strategy: force (Option B) ---
    command_files = []
    for f in import_files:
        entry: dict = {
            "path": f.get("path"),
            "importMode": import_mode,
            "releaseGroup": f.get("releaseGroup", ""),
            "quality": f.get("quality"),
            "languages": f.get("languages", []),
            "downloadId": f.get("downloadId", ""),
            "indexerFlags": f.get("indexerFlags", 0),
            "releaseType": f.get("releaseType", "unknown"),
        }
        # Sonarr fields — seriesId may be top-level or nested under "series"
        series_id = f.get("seriesId") or (f.get("series") or {}).get("id", 0)
        if series_id:
            entry["seriesId"] = series_id
            entry["episodeIds"] = [e["id"] for e in f.get("episodes", [])]
            entry["seasonNumber"] = f.get("seasonNumber")
        # Radarr fields — movieId may be top-level or nested under "movie"
        movie_id = f.get("movieId") or (f.get("movie") or {}).get("id", 0)
        if movie_id:
            entry["movieId"] = movie_id
        command_files.append(entry)

    result = None
    if command_files:
        command = {
            "name": "ManualImport",
            "files": command_files,
            "importMode": import_mode,
            "replaceExistingFiles": True,
        }
        result = await client.post("/api/v3/command", data=command)

    return {
        "success": True,
        "strategy": "force",
        "download_id": download_id,
        "files_queued": len(command_files),
        "files": [f.get("path") for f in import_files],
        "skipped_sample": skipped,
        "command": result,
    }
