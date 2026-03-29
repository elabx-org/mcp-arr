"""Radarr movie management tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_movies(instance: str | None = None) -> dict:
    """Get all movies in the Radarr library.

    Args:
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/movie")
    movies = result if isinstance(result, list) else []
    return {
        "movies": [
            {
                "id": m.get("id"),
                "title": m.get("title"),
                "tmdb_id": m.get("tmdbId"),
                "imdb_id": m.get("imdbId"),
                "year": m.get("year"),
                "status": m.get("status"),
                "monitored": m.get("monitored"),
                "has_file": m.get("hasFile"),
                "path": m.get("path"),
                "quality_profile_id": m.get("qualityProfileId"),
            }
            for m in movies
        ]
    }


@mcp.tool()
async def radarr_get_movie(id: int, instance: str | None = None) -> dict:
    """Get detailed information about a specific movie.

    Args:
        id: Radarr movie ID
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get(f"/api/v3/movie/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def radarr_lookup_movie(term: str, instance: str | None = None) -> dict:
    """Search TMDB for movies by title.

    Args:
        term: Search term (title) to look up
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/movie/lookup", params={"term": term})
    movies = result if isinstance(result, list) else []
    return {
        "results": [
            {
                "title": m.get("title"),
                "tmdb_id": m.get("tmdbId"),
                "imdb_id": m.get("imdbId"),
                "year": m.get("year"),
                "status": m.get("status"),
                "overview": m.get("overview"),
                "genres": m.get("genres", []),
            }
            for m in movies
        ]
    }


@mcp.tool()
async def radarr_lookup_movie_by_tmdb(tmdb_id: int, instance: str | None = None) -> dict:
    """Look up a movie by its TMDB ID.

    Args:
        tmdb_id: The TMDB ID to look up
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/movie/lookup/tmdb", params={"tmdbId": tmdb_id})
    return result if isinstance(result, dict) else {"tmdb_id": tmdb_id, "result": result}


@mcp.tool()
async def radarr_lookup_movie_by_imdb(imdb_id: str, instance: str | None = None) -> dict:
    """Look up a movie by its IMDB ID.

    Args:
        imdb_id: The IMDB ID to look up (e.g., "tt0133093")
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    result = await client.get("/api/v3/movie/lookup/imdb", params={"imdbId": imdb_id})
    return result if isinstance(result, dict) else {"imdb_id": imdb_id, "result": result}


@mcp.tool()
async def radarr_add_movie(
    tmdb_id: int,
    title: str,
    quality_profile_id: int,
    root_folder_path: str,
    monitored: bool = True,
    add_options: dict | None = None,
    instance: str | None = None,
) -> dict:
    """Add a new movie to Radarr.

    Args:
        tmdb_id: TMDB ID for the movie
        title: Movie title
        quality_profile_id: ID of the quality profile to assign
        root_folder_path: Root folder path where the movie will be stored
        monitored: Whether to monitor the movie for releases (default True)
        add_options: Additional add options dict (e.g., {"searchForMovie": True})
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
    """
    client = resolve_instance(instance, "radarr")
    data: dict = {
        "tmdbId": tmdb_id,
        "title": title,
        "qualityProfileId": quality_profile_id,
        "rootFolderPath": root_folder_path,
        "monitored": monitored,
        "addOptions": add_options or {},
    }
    result = await client.post("/api/v3/movie", data=data)
    return result if isinstance(result, dict) else {"success": True, "tmdb_id": tmdb_id}


@mcp.tool()
async def radarr_update_movie(
    id: int,
    instance: str | None = None,
    **fields,
) -> dict:
    """Update a movie. Fetches current data and merges the provided fields.

    Common fields: monitored, qualityProfileId, path, tags, minimumAvailability.

    Args:
        id: Radarr movie ID to update
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        **fields: Movie fields to update (camelCase API field names)
    """
    client = resolve_instance(instance, "radarr")
    current = await client.get(f"/api/v3/movie/{id}")
    current.update(fields)
    result = await client.put(f"/api/v3/movie/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def radarr_delete_movie(
    id: int,
    instance: str | None = None,
    delete_files: bool = False,
    add_import_exclusion: bool = False,
) -> dict:
    """Remove a movie from Radarr.

    Args:
        id: Radarr movie ID to delete
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        delete_files: Also delete the movie files from disk (default False)
        add_import_exclusion: Add to import exclusion list to prevent re-adding (default False)
    """
    client = resolve_instance(instance, "radarr")
    params = {
        "deleteFiles": delete_files,
        "addImportExclusion": add_import_exclusion,
    }
    await client.delete(f"/api/v3/movie/{id}", params=params)
    return {"success": True, "id": id, "message": f"Movie {id} deleted"}


@mcp.tool()
async def radarr_bulk_edit_movies(
    movie_ids: list[int],
    instance: str | None = None,
    **fields,
) -> dict:
    """Bulk edit multiple movies at once.

    Applies the same field updates to all specified movies. Useful for changing
    monitored status, quality profile, or minimum availability for a batch.

    Common fields: monitored, qualityProfileId, minimumAvailability, tags.

    Args:
        movie_ids: List of Radarr movie IDs to update
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        **fields: Fields to apply to all movies (camelCase API field names)
    """
    client = resolve_instance(instance, "radarr")
    data = {"movieIds": movie_ids, **fields}
    result = await client.put("/api/v3/movie/editor", data=data)
    return result if isinstance(result, dict) else {"success": True, "ids": movie_ids}
