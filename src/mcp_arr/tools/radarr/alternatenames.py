"""Radarr alternate movie title management tools."""

from typing import Any

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_list_alternate_names(
    movie_metadata_id: int | None = None,
    instance: str | None = None,
) -> list[dict[str, Any]]:
    """List alternate movie titles (AKAs) known to Radarr.

    Radarr tracks alternate titles sourced from TMDb for use in release matching.
    A movie like "Avengers: Infinity War" may have alternate titles like
    "Avengers 3" that appear in release names.

    Args:
        movie_metadata_id: Filter by specific movie metadata ID.
            If not provided, returns alternate titles for all movies.
        instance: Radarr instance name. Uses default Radarr instance if not specified.

    Returns:
        List of alternate title entries with sourceType, movieMetadataId,
        title, cleanTitle, and language info.
    """
    client = resolve_instance(instance, "radarr")
    params = {}
    if movie_metadata_id is not None:
        params["movieMetadataId"] = movie_metadata_id
    return await client.get("/api/v3/alttitle", params=params)


@mcp.tool()
async def radarr_get_alternate_name(
    alt_title_id: int,
    instance: str | None = None,
) -> dict[str, Any]:
    """Get a specific alternate title by ID.

    Args:
        alt_title_id: Alternate title ID.
        instance: Radarr instance name. Uses default if not specified.

    Returns:
        Alternate title entry with source, movie reference, title, and language.
    """
    client = resolve_instance(instance, "radarr")
    return await client.get(f"/api/v3/alttitle/{alt_title_id}")
