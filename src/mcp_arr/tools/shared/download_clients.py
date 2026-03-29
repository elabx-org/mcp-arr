"""Download client management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_download_clients(instance: str | None = None) -> dict:
    """Get all configured download clients.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/downloadclient")
    return {"download_clients": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_download_client(id: int, instance: str | None = None) -> dict:
    """Get a specific download client by ID.

    Args:
        id: Download client ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/downloadclient/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_download_client(
    name: str,
    enable: bool,
    priority: int,
    fields: list[dict],
    implementation: str,
    config_contract: str,
    instance: str | None = None,
) -> dict:
    """Create a new download client.

    Args:
        name: Download client display name
        enable: Whether the download client is enabled
        priority: Client priority (lower = higher priority)
        fields: Configuration fields (list of dicts with name + value)
        implementation: Implementation class name (e.g., "NzbGet", "Sabnzbd", "qBittorrent")
        config_contract: Configuration contract name
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data = {
        "name": name,
        "enable": enable,
        "priority": priority,
        "fields": fields,
        "implementation": implementation,
        "configContract": config_contract,
    }
    result = await client.post("/api/v3/downloadclient", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def arr_update_download_client(
    id: int,
    name: str | None = None,
    enable: bool | None = None,
    priority: int | None = None,
    fields: list[dict] | None = None,
    instance: str | None = None,
) -> dict:
    """Update an existing download client.

    Args:
        id: Download client ID to update
        name: New display name (optional)
        enable: Enable/disable the client (optional)
        priority: New priority (optional)
        fields: Updated configuration fields (optional)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/downloadclient/{id}")
    if name is not None:
        current["name"] = name
    if enable is not None:
        current["enable"] = enable
    if priority is not None:
        current["priority"] = priority
    if fields is not None:
        current["fields"] = fields
    result = await client.put(f"/api/v3/downloadclient/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_delete_download_client(id: int, instance: str | None = None) -> dict:
    """Delete a download client by ID.

    Args:
        id: Download client ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/downloadclient/{id}")
    return {"success": True, "id": id, "message": f"Download client {id} deleted"}


@mcp.tool()
async def arr_test_download_client(id: int, instance: str | None = None) -> dict:
    """Test a download client connection by ID.

    Args:
        id: Download client ID to test
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/downloadclient/test", data={"id": id})
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_test_all_download_clients(instance: str | None = None) -> dict:
    """Test all download client connections.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/downloadclient/testall")
    return result if isinstance(result, dict) else {"results": result}


@mcp.tool()
async def arr_get_download_client_schema(instance: str | None = None) -> dict:
    """Get available download client implementations and their schemas.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/downloadclient/schema")
    return {"schema": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_add_download_client_to_instances(
    base_config: dict,
    instances: list[str],
    overrides: dict[str, dict] | None = None,
) -> dict:
    """Add a download client to multiple instances at once.

    Args:
        base_config: Base download client configuration (camelCase API field names)
        instances: List of instance names to add the download client to
        overrides: Optional per-instance config overrides keyed by instance name
    """
    results: dict[str, dict] = {}
    for inst_name in instances:
        try:
            client = get_client(inst_name)
            config = {**base_config}
            if overrides and inst_name in overrides:
                config.update(overrides[inst_name])
            result = await client.post("/api/v3/downloadclient", data=config)
            results[inst_name] = {
                "success": True,
                "id": result.get("id") if isinstance(result, dict) else None,
            }
        except Exception as e:
            results[inst_name] = {"success": False, "error": str(e)}
    return {"results": results}


@mcp.tool()
async def arr_update_download_client_across_instances(
    name: str,
    changes: dict,
    instances: list[str],
) -> dict:
    """Update a download client by name across multiple instances.

    Args:
        name: Download client name to find and update (case-insensitive)
        changes: Fields to update (camelCase API field names)
        instances: List of instance names to update the download client on
    """
    results: dict[str, dict] = {}
    for inst_name in instances:
        try:
            client = get_client(inst_name)
            all_clients = await client.get("/api/v3/downloadclient")
            found = next(
                (c for c in all_clients if c.get("name", "").lower() == name.lower()),
                None,
            )
            if not found:
                results[inst_name] = {
                    "success": False,
                    "error": f"Download client '{name}' not found",
                }
                continue
            updated = {**found, **changes}
            result = await client.put(f"/api/v3/downloadclient/{found['id']}", data=updated)
            results[inst_name] = {"success": True, "id": found["id"], "result": result}
        except Exception as e:
            results[inst_name] = {"success": False, "error": str(e)}
    return {"results": results}
