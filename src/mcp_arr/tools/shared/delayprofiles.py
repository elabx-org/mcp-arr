"""Delay profile management tools for Sonarr and Radarr."""

from typing import Any

from ...server import mcp, resolve_instance


@mcp.tool()
async def arr_list_delay_profiles(instance: str | None = None) -> list[dict[str, Any]]:
    """List all delay profiles configured in an arr instance.

    Delay profiles control how long Sonarr/Radarr waits after a release becomes
    available before grabbing it. This allows preferred protocols or release groups
    to be grabbed first, with fallback after a configurable delay.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr4k"). Uses default if not specified.

    Returns:
        List of delay profiles ordered by priority (lower order = higher priority).
        Each profile includes usenet/torrent delays, preferred protocol, and tags.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/delayprofile")


@mcp.tool()
async def arr_get_delay_profile(profile_id: int, instance: str | None = None) -> dict[str, Any]:
    """Get a specific delay profile by ID.

    Args:
        profile_id: Delay profile ID.
        instance: Instance name. Uses default if not specified.

    Returns:
        Delay profile configuration including protocol delays and tag assignments.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get(f"/api/v3/delayprofile/{profile_id}")


@mcp.tool()
async def arr_create_delay_profile(
    usenet_delay: int = 0,
    torrent_delay: int = 0,
    preferred_protocol: str = "usenet",
    usenet_enabled: bool = True,
    torrent_enabled: bool = True,
    bypass_if_highest_quality: bool = False,
    tags: list[int] | None = None,
    instance: str | None = None,
) -> dict[str, Any]:
    """Create a new delay profile.

    Delay profiles let you define different grab timing strategies for different
    content (via tags). For example: grab usenet immediately, wait 2 hours for
    torrents. The default profile (no tags) applies to everything untagged.

    Args:
        usenet_delay: Minutes to wait before grabbing a usenet release. 0 = immediate.
        torrent_delay: Minutes to wait before grabbing a torrent release. 0 = immediate.
        preferred_protocol: Preferred download protocol: "usenet" or "torrent".
            Releases from the preferred protocol are grabbed immediately.
            Other protocol releases wait the full delay period.
        usenet_enabled: Whether usenet releases are allowed. Default True.
        torrent_enabled: Whether torrent releases are allowed. Default True.
        bypass_if_highest_quality: Skip delay if the release is the highest quality
            available. Default False.
        tags: Tag IDs to apply this profile to. Empty list / None = default profile
            that applies to all untagged series/movies.
        instance: Instance name. Uses default if not specified.

    Returns:
        Created delay profile with assigned ID.
    """
    client = resolve_instance(instance, "sonarr")
    body: dict[str, Any] = {
        "usenetDelay": usenet_delay,
        "torrentDelay": torrent_delay,
        "preferredProtocol": preferred_protocol,
        "enableUsenet": usenet_enabled,
        "enableTorrent": torrent_enabled,
        "bypassIfHighestQuality": bypass_if_highest_quality,
        "tags": tags or [],
    }
    return await client.post("/api/v3/delayprofile", body)


@mcp.tool()
async def arr_update_delay_profile(
    profile_id: int,
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update an existing delay profile.

    Args:
        profile_id: Delay profile ID to update.
        updates: Fields to update. Common fields:
            - usenetDelay: int (minutes)
            - torrentDelay: int (minutes)
            - preferredProtocol: "usenet" | "torrent"
            - enableUsenet: bool
            - enableTorrent: bool
            - bypassIfHighestQuality: bool
            - tags: list[int]
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated delay profile configuration.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/delayprofile/{profile_id}")
    current.update(updates)
    return await client.put(f"/api/v3/delayprofile/{profile_id}", current)


@mcp.tool()
async def arr_delete_delay_profile(
    profile_id: int,
    instance: str | None = None,
) -> dict[str, Any]:
    """Delete a delay profile.

    Note: The default delay profile (order=2147483647) cannot be deleted.

    Args:
        profile_id: Delay profile ID to delete.
        instance: Instance name. Uses default if not specified.

    Returns:
        Empty dict on success.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.delete(f"/api/v3/delayprofile/{profile_id}")


@mcp.tool()
async def arr_reorder_delay_profile(
    profile_id: int,
    after_id: int | None = None,
    instance: str | None = None,
) -> dict[str, Any]:
    """Reorder a delay profile (change its priority).

    Lower order number = higher priority. Profiles are evaluated in order;
    the first matching profile (by tag) is used.

    Args:
        profile_id: Delay profile ID to move.
        after_id: Move this profile after the profile with this ID.
            Use None to move to the top (highest priority).
        instance: Instance name. Uses default if not specified.

    Returns:
        Updated delay profile list showing new order.
    """
    client = resolve_instance(instance, "sonarr")
    if after_id is not None:
        return await client.put(f"/api/v3/delayprofile/reorder/{profile_id}?after={after_id}", {})
    return await client.put(f"/api/v3/delayprofile/reorder/{profile_id}", {})
