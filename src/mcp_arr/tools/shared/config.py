"""Configuration management tools for Sonarr and Radarr."""

from typing import Any

from ...server import mcp, resolve_instance


# ─── Host Configuration ──────────────────────────────────────────────────────

@mcp.tool()
async def arr_get_host_config(instance: str | None = None) -> dict[str, Any]:
    """Get host configuration for an arr instance.

    Returns settings like URL base, SSL, authentication, update mechanism,
    proxy settings, and logging configuration.

    Args:
        instance: Instance name. Uses default if not specified.

    Returns:
        Host configuration including network, auth, proxy, and logging settings.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/config/host")


@mcp.tool()
async def arr_update_host_config(
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update host configuration for an arr instance.

    Args:
        updates: Fields to update. Common fields:
            - urlBase: string (URL base path, e.g., "/sonarr")
            - bindAddress: string (IP to bind to, "*" for all)
            - port: int
            - sslPort: int
            - enableSsl: bool
            - launchBrowser: bool
            - authenticationMethod: "none" | "basic" | "forms"
            - username: string
            - password: string
            - analyticsEnabled: bool
            - logLevel: "info" | "debug" | "trace"
            - branch: string (update branch)
            - updateAutomatically: bool
            - proxyEnabled: bool
            - proxyType: "http" | "socks4" | "socks5"
            - proxyHostname: string
            - proxyPort: int
            - proxyUsername: string
            - proxyPassword: string
            - proxyBypassFilter: string
            - proxyBypassLocalAddresses: bool
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated host configuration.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get("/api/v3/config/host")
    current.update(updates)
    return await client.put("/api/v3/config/host", current)


# ─── Naming Configuration ─────────────────────────────────────────────────────

@mcp.tool()
async def arr_get_naming_config(instance: str | None = None) -> dict[str, Any]:
    """Get file and folder naming configuration.

    Returns the naming patterns used when renaming downloaded files,
    including series/movie folder formats and episode/movie file name formats.

    Args:
        instance: Instance name. Uses default if not specified.

    Returns:
        Naming configuration with format strings for folders and files.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/config/naming")


@mcp.tool()
async def arr_update_naming_config(
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update file and folder naming configuration.

    Args:
        updates: Fields to update. Common Sonarr fields:
            - renameEpisodes: bool (enable/disable renaming)
            - replaceIllegalCharacters: bool
            - standardEpisodeFormat: string (e.g., "{Series Title} - S{season:00}E{episode:00}")
            - dailyEpisodeFormat: string
            - animeEpisodeFormat: string
            - seriesFolderFormat: string (e.g., "{Series Title} ({Series Year})")
            - seasonFolderFormat: string (e.g., "Season {season}")
            Common Radarr fields:
            - renameMovies: bool
            - movieFolderFormat: string (e.g., "{Movie Title} ({Release Year})")
            - standardMovieFormat: string
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated naming configuration.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get("/api/v3/config/naming")
    current.update(updates)
    return await client.put("/api/v3/config/naming", current)


@mcp.tool()
async def arr_get_naming_examples(instance: str | None = None) -> dict[str, Any]:
    """Get example filenames using current naming configuration.

    Returns sample formatted filenames to preview how the current naming
    settings will affect actual downloaded files.

    Args:
        instance: Instance name. Uses default if not specified.

    Returns:
        Example formatted filenames for series/movies with current settings.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/config/naming/examples")


# ─── Media Management Configuration ──────────────────────────────────────────

@mcp.tool()
async def arr_get_media_management_config(instance: str | None = None) -> dict[str, Any]:
    """Get media management configuration.

    Returns settings for file handling, hardlinks, permissions, recycling,
    and download path management.

    Args:
        instance: Instance name. Uses default if not specified.

    Returns:
        Media management configuration including file handling and permissions.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/config/mediamanagement")


@mcp.tool()
async def arr_update_media_management_config(
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update media management configuration.

    Args:
        updates: Fields to update. Common fields:
            - autoUnmonitorPreviouslyDownloadedEpisodes: bool (Sonarr)
            - autoUnmonitorPreviouslyDownloadedMovies: bool (Radarr)
            - recycleBin: string (recycle bin path, empty to disable)
            - recycleBinCleanupDays: int (0 to never auto-clean)
            - downloadPropersAndRepacks: "doNotUpgrade" | "preferAndUpgrade" | "doNotPrefer"
            - createEmptySeriesFolders: bool
            - deleteEmptyFolders: bool
            - fileDate: "none" | "localAirDate" | "utcAirDate"
            - rescanAfterRefresh: "always" | "afterManual" | "never"
            - setPermissionsLinux: bool
            - chmodFolder: string (e.g., "755")
            - chownGroup: string
            - skipFreeSpaceCheckWhenImporting: bool
            - minimumFreeSpaceWhenImporting: int (MB)
            - copyUsingHardlinks: bool
            - importExtraFiles: bool
            - extraFileExtensions: string (comma-separated)
            - enableMediaInfo: bool
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated media management configuration.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get("/api/v3/config/mediamanagement")
    current.update(updates)
    return await client.put("/api/v3/config/mediamanagement", current)


# ─── UI Configuration ─────────────────────────────────────────────────────────

@mcp.tool()
async def arr_get_ui_config(instance: str | None = None) -> dict[str, Any]:
    """Get UI configuration for an arr instance.

    Returns display preferences like date format, time format, calendar settings,
    and theme preferences.

    Args:
        instance: Instance name. Uses default if not specified.

    Returns:
        UI configuration including display and theme settings.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/config/ui")


@mcp.tool()
async def arr_update_ui_config(
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update UI configuration for an arr instance.

    Args:
        updates: Fields to update. Common fields:
            - firstDayOfWeek: int (0=Sunday, 1=Monday)
            - calendarWeekColumnHeader: "ddd M/D" | "ddd MM/DD" etc.
            - shortDateFormat: string (e.g., "MMM D YYYY")
            - longDateFormat: string (e.g., "dddd, MMMM D YYYY")
            - timeFormat: string (e.g., "h(:mm)a" or "HH:mm")
            - showRelativeDates: bool
            - enableColorImpairedMode: bool
            - theme: "auto" | "dark" | "light"
            - movieInfoLanguage: int (language ID, Radarr)
            - uiLanguage: int (language ID)
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated UI configuration.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get("/api/v3/config/ui")
    current.update(updates)
    return await client.put("/api/v3/config/ui", current)
