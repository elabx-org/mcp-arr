"""Command execution tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_run_command(
    name: str,
    instance: str | None = None,
    **kwargs,
) -> dict:
    """Run a command on a Sonarr or Radarr instance.

    Common commands:
    - Sonarr: RescanSeries (seriesId), RefreshSeries (seriesId), EpisodeSearch (episodeIds),
      SeasonSearch (seriesId, seasonNumber), SeriesSearch (seriesId),
      DownloadedEpisodesScan (path), RenameFiles (seriesId, files), RenameSeries (seriesIds)
    - Radarr: RescanMovie (movieId), RefreshMovie (movieId), MoviesSearch (movieIds),
      DownloadedMoviesScan (path), RenameFiles (movieId, files), RenameMovie (movieIds)
    - Both: Backup, CheckHealth, ClearBlocklist, MessagingCleanup

    Args:
        name: Command name (see above for options)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        **kwargs: Command-specific parameters (e.g., seriesId=1, seasonNumber=2)
    """
    client = resolve_instance(instance, "sonarr")
    data = {"name": name, **kwargs}
    result = await client.post("/api/v3/command", data=data)
    return result if isinstance(result, dict) else {"success": True, "name": name}


@mcp.tool()
async def arr_get_command(id: int, instance: str | None = None) -> dict:
    """Get the status of a specific command by ID.

    Args:
        id: Command ID returned from arr_run_command
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/command/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_get_commands(instance: str | None = None) -> dict:
    """Get all currently queued or running commands.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/command")
    return {"commands": result if isinstance(result, list) else []}
