"""Sonarr series-level history tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_get_series_history(
    series_id: int,
    instance: str | None = None,
    season_number: int | None = None,
    event_type: int | None = None,
) -> dict:
    """Get history records for a specific series, optionally filtered by season.

    Args:
        series_id: Sonarr series ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        season_number: Filter to a specific season (optional)
        event_type: Filter by event type integer (e.g., 1=grabbed, 3=downloadFailed) (optional)
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {"seriesId": series_id}
    if season_number is not None:
        params["seasonNumber"] = season_number
    if event_type is not None:
        params["eventType"] = event_type
    result = await client.get("/api/v3/history/series", params=params)
    return {"records": result if isinstance(result, list) else []}
