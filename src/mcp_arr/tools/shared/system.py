"""System management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_system_status(instance: str | None = None) -> dict:
    """Get system status information (version, OS, runtime, database, etc.).

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/system/status")
    return result if isinstance(result, dict) else {"status": result}


@mcp.tool()
async def arr_get_disk_space(instance: str | None = None) -> dict:
    """Get disk space information for all root folders and the app data directory.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/diskspace")
    return {"disk_space": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_updates(instance: str | None = None) -> dict:
    """Get available application updates.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/update")
    return {"updates": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_tasks(instance: str | None = None) -> dict:
    """Get all scheduled tasks and their next run times.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/scheduledtask")
    return {"tasks": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_task(id: int, instance: str | None = None) -> dict:
    """Get a specific scheduled task by ID.

    Args:
        id: Scheduled task ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/scheduledtask/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_get_logs(
    instance: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_key: str = "time",
    sort_dir: str = "descending",
    level: str | None = None,
) -> dict:
    """Get application log entries.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
        page: Page number (1-based, default 1)
        page_size: Records per page (default 20)
        sort_key: Field to sort by (default "time")
        sort_dir: Sort direction: "ascending" or "descending" (default "descending")
        level: Log level filter: "trace", "debug", "info", "warn", "error", "fatal"
    """
    client = resolve_instance(instance, "sonarr")
    params: dict = {
        "page": page,
        "pageSize": page_size,
        "sortKey": sort_key,
        "sortDirection": sort_dir,
    }
    if level:
        params["level"] = level
    result = await client.get("/api/v3/log", params=params)
    return result if isinstance(result, dict) else {"records": result}


@mcp.tool()
async def arr_get_log_files(instance: str | None = None) -> dict:
    """Get list of available log files.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/log/file")
    return {"log_files": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_backups(instance: str | None = None) -> dict:
    """Get list of available database backups.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/system/backup")
    return {"backups": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_create_backup(instance: str | None = None) -> dict:
    """Trigger an immediate database backup.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/system/backup")
    return result if isinstance(result, dict) else {"success": True, "message": "Backup initiated"}


@mcp.tool()
async def arr_restore_backup(id: int, instance: str | None = None) -> dict:
    """Restore the instance from a specific backup.

    Args:
        id: Backup ID to restore from
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post(f"/api/v3/system/backup/restore/{id}")
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def arr_delete_backup(id: int, instance: str | None = None) -> dict:
    """Delete a specific backup file.

    Args:
        id: Backup ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/system/backup/{id}")
    return {"success": True, "id": id, "message": f"Backup {id} deleted"}
