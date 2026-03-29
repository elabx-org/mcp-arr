"""Radarr movie credits tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_credits(movie_id: int, instance: str | None = None) -> dict:
    """Get cast and crew credits for a movie.

    Args:
        movie_id: Radarr movie ID
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/credit", params={"movieId": movie_id})
    credits = result if isinstance(result, list) else []
    return {
        "credits": credits,
        "cast": [c for c in credits if c.get("type") == "cast"],
        "crew": [c for c in credits if c.get("type") == "crew"],
    }
