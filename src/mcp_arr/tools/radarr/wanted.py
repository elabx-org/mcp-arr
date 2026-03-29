"""Radarr wanted (missing/cutoff unmet) tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def radarr_get_missing(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    monitored: bool = True,
) -> dict:
    """Get movies that are missing (not yet downloaded).

    Args:
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        monitored: Only return monitored movies (default True)
    """
    client = resolve_instance(instance, "radarr")
    params = {
        "page": page,
        "pageSize": page_size,
        "monitored": monitored,
    }
    result = await client.get("/api/v3/wanted/missing", params=params)
    return result if isinstance(result, dict) else {"records": result}


@mcp.tool()
async def radarr_get_cutoff_unmet(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    monitored: bool = True,
) -> dict:
    """Get movies that have a file but don't meet the quality profile cutoff.

    Args:
        instance: Radarr instance name (e.g., "radarr", "radarr4k"). When None, uses
            the first configured radarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        monitored: Only return monitored movies (default True)
    """
    client = resolve_instance(instance, "radarr")
    params = {
        "page": page,
        "pageSize": page_size,
        "monitored": monitored,
    }
    result = await client.get("/api/v3/wanted/cutoff", params=params)
    return result if isinstance(result, dict) else {"records": result}
