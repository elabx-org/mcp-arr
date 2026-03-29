"""Radarr movie-level history tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_movie_history(
    movie_id: int,
    instance: str | None = None,
    event_type: int | None = None,
) -> dict:
    """Get history records for a specific movie.

    Args:
        movie_id: Radarr movie ID
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        event_type: Filter by event type integer (e.g., 1=grabbed, 3=downloadFailed) (optional)
    """
    client = resolve_instance(instance, "radarr")
    params: dict = {"movieId": movie_id}
    if event_type is not None:
        params["eventType"] = event_type
    result = await client.get("/api/v3/history/movie", params=params)
    return {"records": result if isinstance(result, list) else []}
