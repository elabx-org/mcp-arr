"""Import list management tools for Sonarr and Radarr."""

from typing import Any

from ...server import mcp, resolve_instance


@mcp.tool()
async def arr_list_import_lists(instance: str | None = None) -> list[dict[str, Any]]:
    """List all import lists configured in an arr instance.

    Import lists automatically add content from sources like Trakt, Plex watchlists,
    IMDb lists, and other external sources.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr4k"). Uses default if not specified.

    Returns:
        List of import list configurations with id, name, type, enabled status, and settings.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/importlist")


@mcp.tool()
async def arr_get_import_list(list_id: int, instance: str | None = None) -> dict[str, Any]:
    """Get a specific import list by ID.

    Args:
        list_id: Import list ID.
        instance: Instance name. Uses default if not specified.

    Returns:
        Import list configuration with all settings.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get(f"/api/v3/importlist/{list_id}")


@mcp.tool()
async def arr_create_import_list(
    name: str,
    list_type: str,
    enabled: bool = True,
    enable_auto: bool = True,
    should_monitor: bool = True,
    quality_profile_id: int | None = None,
    root_folder_path: str | None = None,
    settings: dict[str, Any] | None = None,
    instance: str | None = None,
) -> dict[str, Any]:
    """Create a new import list in an arr instance.

    Args:
        name: Display name for the import list.
        list_type: Type of import list (e.g., "TraktList", "PlexWatchlist", "IMDbList").
        enabled: Whether the list is enabled. Default True.
        enable_auto: Automatically add items from the list. Default True.
        should_monitor: Monitor added items for new releases. Default True.
        quality_profile_id: Quality profile to assign to added items.
        root_folder_path: Root folder path for added items.
        settings: Additional list-type-specific settings (API keys, list IDs, etc.).
        instance: Instance name. Uses default if not specified.

    Returns:
        Created import list configuration with assigned ID.
    """
    client = resolve_instance(instance, "sonarr")

    body: dict[str, Any] = {
        "name": name,
        "enabled": enabled,
        "enableAuto": enable_auto,
        "shouldMonitor": should_monitor,
        "implementation": list_type,
        "configContract": f"{list_type}Settings",
    }

    if quality_profile_id is not None:
        body["qualityProfileId"] = quality_profile_id
    if root_folder_path is not None:
        body["rootFolderPath"] = root_folder_path
    if settings:
        body["fields"] = [
            {"name": k, "value": v} for k, v in settings.items()
        ]

    return await client.post("/api/v3/importlist", body)


@mcp.tool()
async def arr_update_import_list(
    list_id: int,
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update an existing import list.

    Args:
        list_id: Import list ID to update.
        updates: Fields to update (e.g., {"enabled": False, "name": "New Name"}).
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated import list configuration.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/importlist/{list_id}")
    current.update(updates)
    return await client.put(f"/api/v3/importlist/{list_id}", current)


@mcp.tool()
async def arr_delete_import_list(list_id: int, instance: str | None = None) -> dict[str, Any]:
    """Delete an import list.

    Args:
        list_id: Import list ID to delete.
        instance: Instance name. Uses default if not specified.

    Returns:
        Empty dict on success.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.delete(f"/api/v3/importlist/{list_id}")


@mcp.tool()
async def arr_get_import_list_schema(instance: str | None = None) -> list[dict[str, Any]]:
    """Get available import list types and their configuration schemas.

    Use this to discover what import list implementations are available
    and what settings each requires (API keys, list IDs, etc.).

    Args:
        instance: Instance name. Uses default if not specified.

    Returns:
        List of available import list type schemas with configurable fields.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/importlist/schema")


@mcp.tool()
async def arr_test_import_list(list_id: int, instance: str | None = None) -> dict[str, Any]:
    """Test an import list connection.

    Args:
        list_id: Import list ID to test.
        instance: Instance name. Uses default if not specified.

    Returns:
        Test result with success status and any error messages.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/importlist/{list_id}")
    return await client.post("/api/v3/importlist/test", current)


@mcp.tool()
async def arr_list_import_list_exclusions(
    page: int = 1,
    page_size: int = 100,
    instance: str | None = None,
) -> dict[str, Any]:
    """List import list exclusions (items excluded from auto-import).

    Import list exclusions prevent specific titles from being automatically added
    even when they appear on a monitored import list.

    Args:
        page: Page number for pagination. Default 1.
        page_size: Results per page. Default 100.
        instance: Instance name. Uses default if not specified.

    Returns:
        Paginated list of exclusions with title, year, and source list info.
    """
    client = resolve_instance(instance, "sonarr")
    params = {"page": page, "pageSize": page_size}
    return await client.get("/api/v3/importlistexclusion", params=params)


@mcp.tool()
async def arr_create_import_list_exclusion(
    title: str,
    tmdb_id: int | None = None,
    tvdb_id: int | None = None,
    instance: str | None = None,
) -> dict[str, Any]:
    """Add an item to the import list exclusion list.

    Prevents a specific title from being auto-added from import lists.

    Args:
        title: Title of the movie or series to exclude.
        tmdb_id: TMDb ID (for Radarr). Required for Radarr instances.
        tvdb_id: TVDb ID (for Sonarr). Required for Sonarr instances.
        instance: Instance name. Uses default if not specified.

    Returns:
        Created exclusion with assigned ID.
    """
    client = resolve_instance(instance, "sonarr")
    body: dict[str, Any] = {"title": title}
    if tmdb_id is not None:
        body["tmdbId"] = tmdb_id
    if tvdb_id is not None:
        body["tvdbId"] = tvdb_id
    return await client.post("/api/v3/importlistexclusion", body)


@mcp.tool()
async def arr_delete_import_list_exclusion(
    exclusion_id: int,
    instance: str | None = None,
) -> dict[str, Any]:
    """Remove an import list exclusion.

    Args:
        exclusion_id: Exclusion ID to remove.
        instance: Instance name. Uses default if not specified.

    Returns:
        Empty dict on success.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.delete(f"/api/v3/importlistexclusion/{exclusion_id}")
