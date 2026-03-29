"""Quality profile, quality definition, and custom format tools."""

import httpx

from ...server import get_client, mcp, resolve_instance


# ---------------------------------------------------------------------------
# Quality Profiles
# ---------------------------------------------------------------------------

@mcp.tool()
async def arr_get_quality_profiles(instance: str | None = None) -> dict:
    """Get all quality profiles from a Sonarr or Radarr instance.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/qualityprofile")
    return {"profiles": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_quality_profile(id: int, instance: str | None = None) -> dict:
    """Get a specific quality profile by ID.

    Args:
        id: Quality profile ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/qualityprofile/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_quality_profile(
    name: str,
    cutoff: int,
    items: list[dict],
    format_items: list[dict] | None = None,
    min_format_score: int = 0,
    cutoff_format_score: int = 0,
    upgrade_allowed: bool = True,
    instance: str | None = None,
) -> dict:
    """Create a new quality profile.

    Args:
        name: Profile name
        cutoff: Quality ID to use as the cutoff
        items: List of quality items (each with qualityId and allowed fields)
        format_items: List of custom format score items
        min_format_score: Minimum custom format score required
        cutoff_format_score: Format score cutoff for upgrades
        upgrade_allowed: Whether upgrades are allowed (default True)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data: dict = {
        "name": name,
        "cutoff": cutoff,
        "items": items,
        "minFormatScore": min_format_score,
        "cutoffFormatScore": cutoff_format_score,
        "upgradeAllowed": upgrade_allowed,
        "formatItems": format_items or [],
    }
    result = await client.post("/api/v3/qualityprofile", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def arr_update_quality_profile(
    id: int,
    name: str | None = None,
    cutoff: int | None = None,
    items: list[dict] | None = None,
    format_items: list[dict] | None = None,
    min_format_score: int | None = None,
    cutoff_format_score: int | None = None,
    upgrade_allowed: bool | None = None,
    instance: str | None = None,
) -> dict:
    """Update an existing quality profile. Fetches current values and merges changes.

    Args:
        id: Quality profile ID to update
        name: New profile name (optional)
        cutoff: New cutoff quality ID (optional)
        items: New quality items list (optional)
        format_items: New custom format items (optional)
        min_format_score: New minimum format score (optional)
        cutoff_format_score: New cutoff format score (optional)
        upgrade_allowed: Whether upgrades are allowed (optional)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/qualityprofile/{id}")
    if name is not None:
        current["name"] = name
    if cutoff is not None:
        current["cutoff"] = cutoff
    if items is not None:
        current["items"] = items
    if format_items is not None:
        current["formatItems"] = format_items
    if min_format_score is not None:
        current["minFormatScore"] = min_format_score
    if cutoff_format_score is not None:
        current["cutoffFormatScore"] = cutoff_format_score
    if upgrade_allowed is not None:
        current["upgradeAllowed"] = upgrade_allowed
    result = await client.put(f"/api/v3/qualityprofile/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_delete_quality_profile(id: int, instance: str | None = None) -> dict:
    """Delete a quality profile by ID.

    Args:
        id: Quality profile ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/qualityprofile/{id}")
    return {"success": True, "id": id, "message": f"Quality profile {id} deleted"}


# ---------------------------------------------------------------------------
# Quality Definitions
# ---------------------------------------------------------------------------

@mcp.tool()
async def arr_get_quality_definitions(instance: str | None = None) -> dict:
    """Get all quality definitions (min/max size settings per quality).

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/qualitydefinition")
    return {"definitions": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_update_quality_definition(
    id: int,
    title: str | None = None,
    min_size: float | None = None,
    max_size: float | None = None,
    preferred_size: float | None = None,
    instance: str | None = None,
) -> dict:
    """Update a quality definition size limits.

    Args:
        id: Quality definition ID
        title: New title (optional)
        min_size: Minimum size in MB per minute (optional)
        max_size: Maximum size in MB per minute (optional, 0 = unlimited)
        preferred_size: Preferred size in MB per minute (optional)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    # Fetch all definitions to find the one we want
    all_defs = await client.get("/api/v3/qualitydefinition")
    current = next((d for d in all_defs if d.get("id") == id), None)
    if current is None:
        return {"error": f"Quality definition {id} not found"}
    if title is not None:
        current["title"] = title
    if min_size is not None:
        current["minSize"] = min_size
    if max_size is not None:
        current["maxSize"] = max_size
    if preferred_size is not None:
        current["preferredSize"] = preferred_size
    result = await client.put(f"/api/v3/qualitydefinition/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


# ---------------------------------------------------------------------------
# Custom Formats
# ---------------------------------------------------------------------------

@mcp.tool()
async def arr_get_custom_formats(instance: str | None = None) -> dict:
    """Get all custom formats from a Sonarr or Radarr instance.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/customformat")
    return {"custom_formats": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_custom_format(id: int, instance: str | None = None) -> dict:
    """Get a specific custom format by ID.

    Args:
        id: Custom format ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/customformat/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_custom_format(
    name: str,
    include_custom_format_when_renaming: bool = False,
    specifications: list[dict] | None = None,
    instance: str | None = None,
) -> dict:
    """Create a new custom format.

    Args:
        name: Custom format name
        include_custom_format_when_renaming: Include in rename tokens (default False)
        specifications: List of specification conditions (each with name, implementation,
            fields, negate, required)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data = {
        "name": name,
        "includeCustomFormatWhenRenaming": include_custom_format_when_renaming,
        "specifications": specifications or [],
    }
    result = await client.post("/api/v3/customformat", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def arr_update_custom_format(
    id: int,
    name: str | None = None,
    include_custom_format_when_renaming: bool | None = None,
    specifications: list[dict] | None = None,
    instance: str | None = None,
) -> dict:
    """Update an existing custom format.

    Args:
        id: Custom format ID to update
        name: New name (optional)
        include_custom_format_when_renaming: Update rename inclusion (optional)
        specifications: New specifications list (optional)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/customformat/{id}")
    if name is not None:
        current["name"] = name
    if include_custom_format_when_renaming is not None:
        current["includeCustomFormatWhenRenaming"] = include_custom_format_when_renaming
    if specifications is not None:
        current["specifications"] = specifications
    result = await client.put(f"/api/v3/customformat/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_delete_custom_format(id: int, instance: str | None = None) -> dict:
    """Delete a custom format by ID.

    Args:
        id: Custom format ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/customformat/{id}")
    return {"success": True, "id": id, "message": f"Custom format {id} deleted"}


@mcp.tool()
async def arr_delete_custom_formats_bulk(
    ids: list[int],
    instance: str | None = None,
) -> dict:
    """Delete multiple custom formats at once.

    Args:
        ids: List of custom format IDs to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete("/api/v3/customformat/bulk", params={"ids": ids})
    return {"success": True, "ids": ids, "message": f"Deleted {len(ids)} custom formats"}


# ---------------------------------------------------------------------------
# TRaSH Guides Custom Format Sync
# ---------------------------------------------------------------------------

@mcp.tool()
async def arr_sync_trash_custom_formats(
    instance: str | None = None,
    profile_names: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Fetch custom format definitions from TRaSH Guides and sync to instance.

    Fetches CF JSON files from the TRaSH Guides GitHub repository, compares
    with existing custom formats on the instance, creates missing ones, and
    updates changed ones.

    TRaSH Guide URLs used:
    - Sonarr CFs: https://raw.githubusercontent.com/TRaSH-Guides/Guides/master/docs/json/sonarr/cf/
    - Radarr CFs: https://raw.githubusercontent.com/TRaSH-Guides/Guides/master/docs/json/radarr/cf/

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        profile_names: If provided, only sync CFs whose names match any entry in
            this list (case-insensitive). When None, syncs all available CFs.
        dry_run: If True, preview changes without applying them (default False)
    """
    client = resolve_instance(instance, "sonarr")
    instance_type = client.instance_type  # "sonarr" or "radarr"

    base_raw = "https://raw.githubusercontent.com/TRaSH-Guides/Guides/master/docs/json"
    api_base = "https://api.github.com/repos/TRaSH-Guides/Guides/contents/docs/json"
    cf_path = f"{instance_type}/cf"

    # 1. Fetch directory listing from GitHub API
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as http:
        dir_resp = await http.get(f"{api_base}/{cf_path}")
        if not dir_resp.is_success:
            return {"error": f"Failed to fetch TRaSH directory listing: {dir_resp.status_code}"}
        dir_listing = dir_resp.json()

    json_files = [
        f["name"] for f in dir_listing
        if isinstance(f, dict) and f.get("name", "").endswith(".json")
    ]

    if not json_files:
        return {"error": "No custom format JSON files found in TRaSH Guides repository"}

    # 2. Fetch each CF JSON
    trash_cfs: list[dict] = []
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as http:
        for filename in json_files:
            url = f"{base_raw}/{cf_path}/{filename}"
            resp = await http.get(url)
            if resp.is_success:
                try:
                    cf_data = resp.json()
                    if isinstance(cf_data, dict) and "name" in cf_data:
                        trash_cfs.append(cf_data)
                except Exception:
                    pass

    # 3. Filter by profile_names if provided
    if profile_names:
        names_lower = {n.lower() for n in profile_names}
        trash_cfs = [cf for cf in trash_cfs if cf["name"].lower() in names_lower]

    # 4. GET existing custom formats from instance
    existing_raw = await client.get("/api/v3/customformat")
    existing: list[dict] = existing_raw if isinstance(existing_raw, list) else []
    existing_by_name = {cf["name"].lower(): cf for cf in existing}

    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    errors: list[str] = []

    for trash_cf in trash_cfs:
        cf_name = trash_cf.get("name", "")
        existing_cf = existing_by_name.get(cf_name.lower())

        # Build the payload (strip TRaSH-specific fields not in arr API)
        payload = {
            "name": cf_name,
            "includeCustomFormatWhenRenaming": trash_cf.get(
                "includeCustomFormatWhenRenaming", False
            ),
            "specifications": trash_cf.get("specifications", []),
        }

        if existing_cf is None:
            # Create
            if not dry_run:
                try:
                    await client.post("/api/v3/customformat", data=payload)
                    created.append(cf_name)
                except Exception as e:
                    errors.append(f"{cf_name}: {e}")
            else:
                created.append(cf_name)
        else:
            # Check if anything changed (compare specs count + names as a simple heuristic)
            existing_spec_names = sorted(
                s.get("name", "") for s in existing_cf.get("specifications", [])
            )
            trash_spec_names = sorted(
                s.get("name", "") for s in payload["specifications"]
            )
            if existing_spec_names != trash_spec_names:
                if not dry_run:
                    try:
                        update_payload = {**existing_cf, **payload}
                        await client.put(
                            f"/api/v3/customformat/{existing_cf['id']}", data=update_payload
                        )
                        updated.append(cf_name)
                    except Exception as e:
                        errors.append(f"{cf_name}: {e}")
                else:
                    updated.append(cf_name)
            else:
                unchanged.append(cf_name)

    return {
        "dry_run": dry_run,
        "instance_type": instance_type,
        "trash_cfs_found": len(trash_cfs),
        "created": created,
        "updated": updated,
        "unchanged_count": len(unchanged),
        "errors": errors,
    }
