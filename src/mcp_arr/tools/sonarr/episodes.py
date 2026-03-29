"""Sonarr episode management tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_get_episodes(
    series_id: int,
    instance: str | None = None,
    season_number: int | None = None,
) -> dict:
    """Get all episodes for a series, optionally filtered by season.

    Args:
        series_id: Sonarr series ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        season_number: Filter to a specific season number (optional)
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {"seriesId": series_id}
    if season_number is not None:
        params["seasonNumber"] = season_number
    result = await client.get("/api/v3/episode", params=params)
    return {"episodes": result if isinstance(result, list) else []}


@mcp.tool()
async def sonarr_get_episode(id: int, instance: str | None = None) -> dict:
    """Get a specific episode by its Sonarr ID.

    Args:
        id: Sonarr episode ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/episode/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def sonarr_update_episode(
    id: int,
    monitored: bool,
    instance: str | None = None,
) -> dict:
    """Update the monitored status of a single episode.

    Args:
        id: Sonarr episode ID to update
        monitored: New monitored state
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/episode/{id}")
    current["monitored"] = monitored
    result = await client.put(f"/api/v3/episode/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def sonarr_update_episodes_bulk(
    episode_ids: list[int],
    monitored: bool,
    instance: str | None = None,
) -> dict:
    """Update the monitored status of multiple episodes at once.

    Args:
        episode_ids: List of Sonarr episode IDs to update
        monitored: New monitored state for all specified episodes
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data = {"episodeIds": episode_ids, "monitored": monitored}
    result = await client.put("/api/v3/episode/monitor", data=data)
    return result if isinstance(result, dict) else {"success": True, "ids": episode_ids}


@mcp.tool()
async def sonarr_get_episode_files(series_id: int, instance: str | None = None) -> dict:
    """Get all episode files for a series.

    Args:
        series_id: Sonarr series ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/episodefile", params={"seriesId": series_id})
    return {"episode_files": result if isinstance(result, list) else []}


@mcp.tool()
async def sonarr_get_episode_file(id: int, instance: str | None = None) -> dict:
    """Get a specific episode file by ID.

    Args:
        id: Episode file ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/episodefile/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def sonarr_delete_episode_file(id: int, instance: str | None = None) -> dict:
    """Delete a specific episode file from disk.

    Args:
        id: Episode file ID to delete
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/episodefile/{id}")
    return {"success": True, "id": id, "message": f"Episode file {id} deleted"}


@mcp.tool()
async def sonarr_delete_episode_files_bulk(
    ids: list[int],
    instance: str | None = None,
) -> dict:
    """Delete multiple episode files from disk at once.

    Args:
        ids: List of episode file IDs to delete
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete("/api/v3/episodefile/bulk", params={"ids": ids})
    return {"success": True, "ids": ids, "message": f"Deleted {len(ids)} episode files"}


@mcp.tool()
async def sonarr_update_episode_file_quality(
    id: int,
    quality: dict,
    instance: str | None = None,
) -> dict:
    """Update the quality metadata of an episode file.

    Args:
        id: Episode file ID to update
        quality: Quality object dict (e.g., {"quality": {"id": 7, "name": "Bluray-1080p"},
            "revision": {"version": 1, "real": 0}})
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/episodefile/{id}")
    current["quality"] = quality
    result = await client.put(f"/api/v3/episodefile/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}
