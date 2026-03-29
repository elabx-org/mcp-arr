"""Sonarr wanted (missing/cutoff unmet) tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_get_missing(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    monitored: bool = True,
) -> dict:
    """Get episodes that are missing (not yet downloaded).

    Args:
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        monitored: Only return monitored episodes (default True)
    """
    client = resolve_instance(instance, "sonarr")
    params = {
        "page": page,
        "pageSize": page_size,
        "monitored": monitored,
    }
    result = await client.get("/api/v3/wanted/missing", params=params)
    return result if isinstance(result, dict) else {"records": result}


@mcp.tool()
async def sonarr_get_cutoff_unmet(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    monitored: bool = True,
) -> dict:
    """Get episodes that have a file but don't meet the quality profile cutoff.

    Args:
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        monitored: Only return monitored episodes (default True)
    """
    client = resolve_instance(instance, "sonarr")
    params = {
        "page": page,
        "pageSize": page_size,
        "monitored": monitored,
    }
    result = await client.get("/api/v3/wanted/cutoff", params=params)
    return result if isinstance(result, dict) else {"records": result}
