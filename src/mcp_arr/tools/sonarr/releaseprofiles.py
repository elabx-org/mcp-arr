"""Sonarr release profile management tools."""

from typing import Any

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_list_release_profiles(instance: str | None = None) -> list[dict[str, Any]]:
    """List all release profiles in a Sonarr instance.

    Release profiles filter which releases Sonarr will grab based on
    required/preferred/ignored terms. They are evaluated before quality profiles.

    Note: Release profiles are a Sonarr-specific feature. Use custom formats
    in Radarr for similar filtering.

    Args:
        instance: Sonarr instance name. Uses default Sonarr instance if not specified.

    Returns:
        List of release profiles with required, preferred, and ignored terms.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get("/api/v3/releaseprofile")


@mcp.tool()
async def sonarr_get_release_profile(
    profile_id: int,
    instance: str | None = None,
) -> dict[str, Any]:
    """Get a specific Sonarr release profile by ID.

    Args:
        profile_id: Release profile ID.
        instance: Sonarr instance name. Uses default if not specified.

    Returns:
        Release profile with required, preferred, ignored terms and tag assignments.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.get(f"/api/v3/releaseprofile/{profile_id}")


@mcp.tool()
async def sonarr_create_release_profile(
    enabled: bool = True,
    required: list[str] | None = None,
    ignored: list[str] | None = None,
    preferred: list[dict[str, Any]] | None = None,
    include_preferred_when_renaming: bool = False,
    tags: list[int] | None = None,
    instance: str | None = None,
) -> dict[str, Any]:
    """Create a new Sonarr release profile.

    Release profiles allow filtering releases by terms in the release name.
    Useful for blocking certain release groups, requiring specific audio formats,
    or preferring/avoiding specific scene groups.

    Args:
        enabled: Whether the profile is active. Default True.
        required: List of terms that MUST be in the release name (AND logic).
            Example: ["Remux", "BluRay"] — release must have both.
        ignored: List of terms that must NOT be in the release name.
            Example: ["YIFY", "x265"] — releases with these are rejected.
        preferred: List of preferred term entries with scores.
            Format: [{"key": "term", "value": score}]
            Example: [{"key": "AMZN", "value": 10}, {"key": "NF", "value": 5}]
            Higher score = more preferred. These affect quality score tiebreaking.
        include_preferred_when_renaming: Include preferred term in renamed filename.
        tags: Tag IDs to limit this profile to specific series.
            Empty list / None = applies to all series.
        instance: Sonarr instance name. Uses default if not specified.

    Returns:
        Created release profile with assigned ID.
    """
    client = resolve_instance(instance, "sonarr")
    body: dict[str, Any] = {
        "enabled": enabled,
        "required": required or [],
        "ignored": ignored or [],
        "preferred": preferred or [],
        "includePreferredWhenRenaming": include_preferred_when_renaming,
        "tags": tags or [],
    }
    return await client.post("/api/v3/releaseprofile", body)


@mcp.tool()
async def sonarr_update_release_profile(
    profile_id: int,
    updates: dict[str, Any],
    instance: str | None = None,
) -> dict[str, Any]:
    """Update an existing Sonarr release profile.

    Args:
        profile_id: Release profile ID to update.
        updates: Fields to update. Mergeable fields:
            - enabled: bool
            - required: list[str]
            - ignored: list[str]
            - preferred: list[{"key": str, "value": int}]
            - includePreferredWhenRenaming: bool
            - tags: list[int]
        instance: Sonarr instance name. Uses default if not specified.

    Returns:
        Updated release profile.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/releaseprofile/{profile_id}")
    current.update(updates)
    return await client.put(f"/api/v3/releaseprofile/{profile_id}", current)


@mcp.tool()
async def sonarr_delete_release_profile(
    profile_id: int,
    instance: str | None = None,
) -> dict[str, Any]:
    """Delete a Sonarr release profile.

    Args:
        profile_id: Release profile ID to delete.
        instance: Sonarr instance name. Uses default if not specified.

    Returns:
        Empty dict on success.
    """
    client = resolve_instance(instance, "sonarr")
    return await client.delete(f"/api/v3/releaseprofile/{profile_id}")
