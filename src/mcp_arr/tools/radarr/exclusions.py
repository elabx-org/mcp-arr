"""Radarr import exclusion tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_exclusions(instance: str | None = None) -> dict:
    """Get all import exclusions (movies that should never be automatically added).

    Args:
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/exclusions")
    return {"exclusions": result if isinstance(result, list) else []}


@mcp.tool()
async def radarr_add_exclusion(
    tmdb_id: int,
    movie_title: str,
    movie_year: int,
    instance: str | None = None,
) -> dict:
    """Add a movie to the import exclusion list.

    Args:
        tmdb_id: TMDB ID of the movie to exclude
        movie_title: Movie title (for display purposes)
        movie_year: Movie release year
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    data = {
        "tmdbId": tmdb_id,
        "movieTitle": movie_title,
        "movieYear": movie_year,
    }
    result = await client.post("/api/v3/exclusions", data=data)
    return result if isinstance(result, dict) else {"success": True, "tmdb_id": tmdb_id}


@mcp.tool()
async def radarr_delete_exclusion(id: int, instance: str | None = None) -> dict:
    """Remove a movie from the import exclusion list.

    Args:
        id: Exclusion record ID to remove
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    await client.delete(f"/api/v3/exclusions/{id}")
    return {"success": True, "id": id, "message": f"Exclusion {id} removed"}


@mcp.tool()
async def radarr_delete_exclusions_bulk(ids: list[int], instance: str | None = None) -> dict:
    """Remove multiple movies from the import exclusion list at once.

    Args:
        ids: List of exclusion record IDs to remove
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    await client.delete("/api/v3/exclusions/bulk", params={"ids": ids})
    return {"success": True, "ids": ids, "message": f"Removed {len(ids)} exclusions"}
