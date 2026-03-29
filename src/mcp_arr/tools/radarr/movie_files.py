"""Radarr movie file management tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_movie_files(movie_id: int, instance: str | None = None) -> dict:
    """Get all files for a specific movie.

    Args:
        movie_id: Radarr movie ID
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/moviefile", params={"movieId": movie_id})
    return {"movie_files": result if isinstance(result, list) else []}


@mcp.tool()
async def radarr_get_movie_file(id: int, instance: str | None = None) -> dict:
    """Get a specific movie file by its ID.

    Args:
        id: Movie file ID
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get(f"/api/v3/moviefile/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def radarr_delete_movie_file(id: int, instance: str | None = None) -> dict:
    """Delete a specific movie file from disk.

    Args:
        id: Movie file ID to delete
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    await client.delete(f"/api/v3/moviefile/{id}")
    return {"success": True, "id": id, "message": f"Movie file {id} deleted"}


@mcp.tool()
async def radarr_delete_movie_files_bulk(ids: list[int], instance: str | None = None) -> dict:
    """Delete multiple movie files from disk at once.

    Args:
        ids: List of movie file IDs to delete
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    await client.delete("/api/v3/moviefile/bulk", params={"ids": ids})
    return {"success": True, "ids": ids, "message": f"Deleted {len(ids)} movie files"}


@mcp.tool()
async def radarr_update_movie_file_quality(
    id: int,
    quality: dict,
    instance: str | None = None,
) -> dict:
    """Update the quality metadata of a movie file.

    Args:
        id: Movie file ID to update
        quality: Quality object dict (e.g., {"quality": {"id": 7, "name": "Bluray-1080p"},
            "revision": {"version": 1, "real": 0}})
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    current = await client.get(f"/api/v3/moviefile/{id}")
    current["quality"] = quality
    result = await client.put(f"/api/v3/moviefile/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}
