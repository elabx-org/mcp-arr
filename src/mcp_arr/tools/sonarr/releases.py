"""Sonarr release search tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_search_season_releases(
    series_id: int,
    season_number: int,
    instance: str | None = None,
) -> dict:
    """Search indexers for all releases for a season.

    Returns both season packs and individual episode releases in one query.
    This is more efficient than searching per-episode when you want to find
    the best coverage for an entire season.

    Use arr_plan_grab to determine the optimal grab strategy from these results,
    then arr_grab_release to execute each grab.

    Args:
        series_id: Sonarr series ID
        season_number: Season number to search for
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    params = {"seriesId": series_id, "seasonNumber": season_number}
    result = await client.search_get("/api/v3/release", params=params)
    releases = result if isinstance(result, list) else []
    return {
        "releases": releases,
        "total": len(releases),
        "season_packs": [r for r in releases if r.get("fullSeason", False)],
        "episodes": [r for r in releases if not r.get("fullSeason", False)],
    }


@mcp.tool()
async def sonarr_search_episode_releases(
    episode_id: int,
    instance: str | None = None,
) -> dict:
    """Search indexers for releases for a specific episode.

    Args:
        episode_id: Sonarr episode ID to search releases for
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.search_get("/api/v3/release", params={"episodeId": episode_id})
    releases = result if isinstance(result, list) else []
    return {
        "releases": releases,
        "total": len(releases),
        "episode_id": episode_id,
    }
