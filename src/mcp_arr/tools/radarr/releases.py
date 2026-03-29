"""Radarr release search tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_search_movie_releases(movie_id: int, instance: str | None = None) -> dict:
    """Search indexers for all available releases for a movie.

    Returns all release candidates from configured indexers. Use arr_plan_grab
    to select the best grab strategy, then arr_grab_release to execute grabs.

    Args:
        movie_id: Radarr movie ID to search releases for
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/release", params={"movieId": movie_id})
    releases = result if isinstance(result, list) else []
    return {
        "releases": releases,
        "total": len(releases),
        "movie_id": movie_id,
        "usenet": [r for r in releases if r.get("protocol") == "usenet"],
        "torrent": [r for r in releases if r.get("protocol") == "torrent"],
    }
