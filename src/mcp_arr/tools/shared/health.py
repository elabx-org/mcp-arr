"""Health check tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_health(instance: str | None = None) -> dict:
    """Get health check results for a Sonarr or Radarr instance.

    Returns a list of any health warnings or errors, useful for diagnosing
    configuration problems or connectivity issues.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/health")
    items = result if isinstance(result, list) else []
    return {
        "health": items,
        "ok": all(item.get("type", "").lower() != "error" for item in items),
        "warnings": [i for i in items if i.get("type", "").lower() == "warning"],
        "errors": [i for i in items if i.get("type", "").lower() == "error"],
    }
