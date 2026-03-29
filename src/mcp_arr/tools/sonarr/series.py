"""Sonarr series management tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_get_series(instance: str | None = None) -> dict:
    """Get all series in the Sonarr library.

    Args:
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/series")
    series = result if isinstance(result, list) else []
    return {
        "series": [
            {
                "id": s.get("id"),
                "title": s.get("title"),
                "tvdb_id": s.get("tvdbId"),
                "status": s.get("status"),
                "monitored": s.get("monitored"),
                "season_count": len(s.get("seasons", [])),
                "path": s.get("path"),
                "quality_profile_id": s.get("qualityProfileId"),
                "network": s.get("network"),
                "statistics": s.get("statistics"),
            }
            for s in series
        ]
    }


@mcp.tool()
async def sonarr_get_series_by_id(id: int, instance: str | None = None) -> dict:
    """Get detailed information about a specific series.

    Args:
        id: Sonarr series ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/series/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def sonarr_lookup_series(term: str, instance: str | None = None) -> dict:
    """Search TVDB for series by title or URL.

    Args:
        term: Search term (title) or TVDB URL
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/series/lookup", params={"term": term})
    series = result if isinstance(result, list) else []
    return {
        "results": [
            {
                "title": s.get("title"),
                "tvdb_id": s.get("tvdbId"),
                "year": s.get("year"),
                "status": s.get("status"),
                "overview": s.get("overview"),
                "network": s.get("network"),
                "genres": s.get("genres", []),
            }
            for s in series
        ]
    }


@mcp.tool()
async def sonarr_lookup_series_by_tvdb(tvdb_id: int, instance: str | None = None) -> dict:
    """Look up a series by its TVDB ID.

    Args:
        tvdb_id: The TVDB ID to look up
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/series/lookup", params={"term": f"tvdb:{tvdb_id}"})
    series = result if isinstance(result, list) else []
    return {
        "results": series,
        "tvdb_id": tvdb_id,
    }


@mcp.tool()
async def sonarr_add_series(
    tvdb_id: int,
    title: str,
    quality_profile_id: int,
    root_folder_path: str,
    monitored: bool = True,
    season_folder: bool = True,
    add_options: dict | None = None,
    instance: str | None = None,
) -> dict:
    """Add a new series to Sonarr.

    Args:
        tvdb_id: TVDB ID for the series
        title: Series title
        quality_profile_id: ID of the quality profile to assign
        root_folder_path: Root folder path where the series will be stored
        monitored: Whether to monitor the series for new episodes (default True)
        season_folder: Use individual season folders (default True)
        add_options: Additional add options dict (e.g., {"searchForMissingEpisodes": True,
            "monitor": "all"})
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data: dict = {
        "tvdbId": tvdb_id,
        "title": title,
        "qualityProfileId": quality_profile_id,
        "rootFolderPath": root_folder_path,
        "monitored": monitored,
        "seasonFolder": season_folder,
        "addOptions": add_options or {},
    }
    result = await client.post("/api/v3/series", data=data)
    return result if isinstance(result, dict) else {"success": True, "tvdb_id": tvdb_id}


@mcp.tool()
async def sonarr_update_series(
    id: int,
    instance: str | None = None,
    **fields,
) -> dict:
    """Update a series. Fetches current data and merges the provided fields.

    Common fields to update: monitored, qualityProfileId, seasonFolder, path,
    seriesType, useSceneNumbering, tags.

    Args:
        id: Sonarr series ID to update
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        **fields: Series fields to update (camelCase API field names)
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/series/{id}")
    current.update(fields)
    result = await client.put(f"/api/v3/series/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def sonarr_delete_series(
    id: int,
    instance: str | None = None,
    delete_files: bool = False,
    add_import_exclusion: bool = False,
) -> dict:
    """Remove a series from Sonarr.

    Args:
        id: Sonarr series ID to delete
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        delete_files: Also delete the series files from disk (default False)
        add_import_exclusion: Add to import exclusion list to prevent re-adding (default False)
    """
    client = resolve_instance(instance, "sonarr")
    params = {
        "deleteFiles": delete_files,
        "addImportExclusion": add_import_exclusion,
    }
    await client.delete(f"/api/v3/series/{id}", params=params)
    return {"success": True, "id": id, "message": f"Series {id} deleted"}


@mcp.tool()
async def sonarr_bulk_edit_series(
    series_ids: list[int],
    instance: str | None = None,
    **fields,
) -> dict:
    """Bulk edit multiple series at once.

    Applies the same field updates to all specified series. Useful for changing
    monitored status, quality profile, or path pattern for a batch of series.

    Common fields: monitored, qualityProfileId, seriesType, seasonFolder, tags.

    Args:
        series_ids: List of Sonarr series IDs to update
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        **fields: Fields to apply to all series (camelCase API field names)
    """
    client = resolve_instance(instance, "sonarr")
    data = {"seriesIds": series_ids, **fields}
    result = await client.put("/api/v3/series/editor", data=data)
    return result if isinstance(result, dict) else {"success": True, "ids": series_ids}
