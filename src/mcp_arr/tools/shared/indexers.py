"""Indexer management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, get_clients_by_type, mcp, resolve_instance


@mcp.tool()
async def arr_get_indexers(instance: str | None = None) -> dict:
    """Get all configured indexers.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/indexer")
    return {"indexers": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_indexer(id: int, instance: str | None = None) -> dict:
    """Get a specific indexer by ID.

    Args:
        id: Indexer ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/indexer/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_indexer(
    name: str,
    enable_rss: bool,
    enable_automatic_search: bool,
    enable_interactive_search: bool,
    priority: int,
    fields: list[dict],
    implementation: str,
    config_contract: str,
    instance: str | None = None,
) -> dict:
    """Create a new indexer.

    Args:
        name: Indexer display name
        enable_rss: Enable RSS feed polling
        enable_automatic_search: Enable automatic search
        enable_interactive_search: Enable interactive search
        priority: Indexer priority (lower = higher priority)
        fields: List of field dicts (name + value) for the indexer configuration
        implementation: Indexer implementation class name (e.g., "Newznab", "Torznab")
        config_contract: Configuration contract name (e.g., "NewznabSettings")
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data = {
        "name": name,
        "enableRss": enable_rss,
        "enableAutomaticSearch": enable_automatic_search,
        "enableInteractiveSearch": enable_interactive_search,
        "priority": priority,
        "fields": fields,
        "implementation": implementation,
        "configContract": config_contract,
    }
    result = await client.post("/api/v3/indexer", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def arr_update_indexer(
    id: int,
    name: str | None = None,
    enable_rss: bool | None = None,
    enable_automatic_search: bool | None = None,
    enable_interactive_search: bool | None = None,
    priority: int | None = None,
    fields: list[dict] | None = None,
    instance: str | None = None,
) -> dict:
    """Update an existing indexer. Fetches current config and merges changes.

    Args:
        id: Indexer ID to update
        name: New display name (optional)
        enable_rss: Enable RSS feed (optional)
        enable_automatic_search: Enable automatic search (optional)
        enable_interactive_search: Enable interactive search (optional)
        priority: New priority (optional)
        fields: Updated fields list (optional)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/indexer/{id}")
    if name is not None:
        current["name"] = name
    if enable_rss is not None:
        current["enableRss"] = enable_rss
    if enable_automatic_search is not None:
        current["enableAutomaticSearch"] = enable_automatic_search
    if enable_interactive_search is not None:
        current["enableInteractiveSearch"] = enable_interactive_search
    if priority is not None:
        current["priority"] = priority
    if fields is not None:
        current["fields"] = fields
    result = await client.put(f"/api/v3/indexer/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_delete_indexer(id: int, instance: str | None = None) -> dict:
    """Delete an indexer by ID.

    Args:
        id: Indexer ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/indexer/{id}")
    return {"success": True, "id": id, "message": f"Indexer {id} deleted"}


@mcp.tool()
async def arr_test_indexer(id: int, instance: str | None = None) -> dict:
    """Test an indexer connection by ID.

    Args:
        id: Indexer ID to test
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post(f"/api/v3/indexer/test", data={"id": id})
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_test_all_indexers(instance: str | None = None) -> dict:
    """Test all indexer connections.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/indexer/testall")
    return result if isinstance(result, dict) else {"results": result}


@mcp.tool()
async def arr_get_indexer_schema(instance: str | None = None) -> dict:
    """Get indexer schema (available indexer implementations).

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/indexer/schema")
    return {"schema": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_add_indexer_to_instances(
    base_config: dict,
    instances: list[str],
    overrides: dict[str, dict] | None = None,
) -> dict:
    """Add an indexer to multiple instances at once.

    Sends the base_config to each instance in the list, applying per-instance
    field overrides if provided. Useful for setting up the same indexer across
    all your Sonarr/Radarr instances simultaneously.

    Args:
        base_config: Base indexer configuration dict (same structure as arr_create_indexer
            parameters, using camelCase API field names: name, enableRss, fields, etc.)
        instances: List of instance names to add the indexer to
        overrides: Optional per-instance overrides. Keys are instance names, values are
            dicts that are merged into base_config before sending to that instance.
            Example: {"sonarr4k": {"fields": [{"name": "categories", "value": "5040"}]}}
    """
    results: dict[str, dict] = {}
    for inst_name in instances:
        try:
            client = get_client(inst_name)
            config = {**base_config}
            if overrides and inst_name in overrides:
                config.update(overrides[inst_name])
            result = await client.post("/api/v3/indexer", data=config)
            results[inst_name] = {
                "success": True,
                "id": result.get("id") if isinstance(result, dict) else None,
            }
        except Exception as e:
            results[inst_name] = {"success": False, "error": str(e)}
    return {"results": results}


@mcp.tool()
async def arr_update_indexer_across_instances(
    name: str,
    changes: dict,
    instances: list[str],
) -> dict:
    """Update an indexer by name across multiple instances.

    Finds the indexer by name on each instance and applies the changes dict.

    Args:
        name: Indexer name to find and update (case-insensitive)
        changes: Dict of fields to update (camelCase API field names)
        instances: List of instance names to update the indexer on
    """
    results: dict[str, dict] = {}
    for inst_name in instances:
        try:
            client = get_client(inst_name)
            all_indexers = await client.get("/api/v3/indexer")
            found = next(
                (idx for idx in all_indexers if idx.get("name", "").lower() == name.lower()),
                None,
            )
            if not found:
                results[inst_name] = {"success": False, "error": f"Indexer '{name}' not found"}
                continue
            updated = {**found, **changes}
            result = await client.put(f"/api/v3/indexer/{found['id']}", data=updated)
            results[inst_name] = {
                "success": True,
                "id": found["id"],
                "result": result,
            }
        except Exception as e:
            results[inst_name] = {"success": False, "error": str(e)}
    return {"results": results}
