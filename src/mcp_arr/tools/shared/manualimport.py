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
