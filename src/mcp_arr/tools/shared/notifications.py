"""Notification management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_notifications(instance: str | None = None) -> dict:
    """Get all configured notifications.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/notification")
    return {"notifications": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_notification(id: int, instance: str | None = None) -> dict:
    """Get a specific notification by ID.

    Args:
        id: Notification ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/notification/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_notification(
    name: str,
    on_grab: bool,
    on_download: bool,
    on_upgrade: bool,
    on_health_issue: bool,
    fields: list[dict],
    implementation: str,
    config_contract: str,
    instance: str | None = None,
) -> dict:
    """Create a new notification.

    Args:
        name: Notification display name
        on_grab: Trigger on grab events
        on_download: Trigger on download completion
        on_upgrade: Trigger on quality upgrade
        on_health_issue: Trigger on health check failures
        fields: Configuration fields (list of dicts with name + value)
        implementation: Implementation class name (e.g., "Discord", "Slack", "Webhook")
        config_contract: Configuration contract name
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data = {
        "name": name,
        "onGrab": on_grab,
        "onDownload": on_download,
        "onUpgrade": on_upgrade,
        "onHealthIssue": on_health_issue,
        "fields": fields,
        "implementation": implementation,
        "configContract": config_contract,
    }
    result = await client.post("/api/v3/notification", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def arr_update_notification(
    id: int,
    name: str | None = None,
    on_grab: bool | None = None,
    on_download: bool | None = None,
    on_upgrade: bool | None = None,
    on_health_issue: bool | None = None,
    fields: list[dict] | None = None,
    instance: str | None = None,
) -> dict:
    """Update an existing notification.

    Args:
        id: Notification ID to update
        name: New display name (optional)
        on_grab: Update grab trigger (optional)
        on_download: Update download trigger (optional)
        on_upgrade: Update upgrade trigger (optional)
        on_health_issue: Update health issue trigger (optional)
        fields: Updated configuration fields (optional)
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/notification/{id}")
    if name is not None:
        current["name"] = name
    if on_grab is not None:
        current["onGrab"] = on_grab
    if on_download is not None:
        current["onDownload"] = on_download
    if on_upgrade is not None:
        current["onUpgrade"] = on_upgrade
    if on_health_issue is not None:
        current["onHealthIssue"] = on_health_issue
    if fields is not None:
        current["fields"] = fields
    result = await client.put(f"/api/v3/notification/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_delete_notification(id: int, instance: str | None = None) -> dict:
    """Delete a notification by ID.

    Args:
        id: Notification ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/notification/{id}")
    return {"success": True, "id": id, "message": f"Notification {id} deleted"}


@mcp.tool()
async def arr_test_notification(id: int, instance: str | None = None) -> dict:
    """Test a notification by sending a test event.

    Args:
        id: Notification ID to test
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/notification/test", data={"id": id})
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_get_notification_schema(instance: str | None = None) -> dict:
    """Get available notification implementations and their schemas.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/notification/schema")
    return {"schema": result if isinstance(result, list) else []}
