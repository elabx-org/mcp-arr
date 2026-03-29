"""Root folder management tools — works for both Sonarr and Radarr instances."""

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_get_root_folders(instance: str | None = None) -> dict:
    """Get all configured root folders with free space information.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/rootfolder")
    return {"root_folders": result if isinstance(result, list) else []}


@mcp.tool()
async def arr_get_root_folder(id: int, instance: str | None = None) -> dict:
    """Get a specific root folder by ID.

    Args:
        id: Root folder ID
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/rootfolder/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def arr_create_root_folder(path: str, instance: str | None = None) -> dict:
    """Add a new root folder.

    Args:
        path: Absolute filesystem path for the root folder
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.post("/api/v3/rootfolder", data={"path": path})
    return result if isinstance(result, dict) else {"success": True, "path": path}


@mcp.tool()
async def arr_delete_root_folder(id: int, instance: str | None = None) -> dict:
    """Delete a root folder by ID.

    Args:
        id: Root folder ID to delete
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/rootfolder/{id}")
    return {"success": True, "id": id, "message": f"Root folder {id} deleted"}
