"""Release title parsing tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_parse_title(title: str, instance: str | None = None) -> dict:
    """Parse a release title and return what Sonarr/Radarr identifies it as.

    Useful for understanding how a release title will be matched against your
    library before grabbing it.

    Args:
        title: Release title to parse (e.g., "The.Show.S01E05.1080p.BluRay.x264")
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/parse", params={"title": title})
    return result if isinstance(result, dict) else {"title": title, "result": result}
