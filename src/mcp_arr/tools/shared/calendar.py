"""Calendar tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_calendar(
    instance: str | None = None,
    start: str | None = None,
    end: str | None = None,
    unmonitored: bool = False,
) -> dict:
    """Get calendar entries (upcoming episodes or movies) for a date range.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        start: Start date in ISO 8601 format (e.g., "2024-01-01"). When None,
            the instance uses its default look-ahead window.
        end: End date in ISO 8601 format (e.g., "2024-01-07"). When None,
            the instance uses its default look-ahead window.
        unmonitored: Include unmonitored items in results (default False)
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {"unmonitored": unmonitored}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    result = await client.get("/api/v3/calendar", params=params)
    return {"calendar": result if isinstance(result, list) else []}
