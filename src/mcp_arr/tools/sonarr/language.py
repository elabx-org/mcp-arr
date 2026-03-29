"""Sonarr language profile tools."""

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_get_language_profiles(instance: str | None = None) -> dict:
    """Get all language profiles configured in Sonarr.

    Args:
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/languageprofile")
    return {"language_profiles": result if isinstance(result, list) else []}


@mcp.tool()
async def sonarr_get_language_profile(id: int, instance: str | None = None) -> dict:
    """Get a specific language profile by ID.

    Args:
        id: Language profile ID
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get(f"/api/v3/languageprofile/{id}")
    return result if isinstance(result, dict) else {"id": id, "result": result}


@mcp.tool()
async def sonarr_create_language_profile(
    name: str,
    upgrade_allowed: bool,
    cutoff: dict,
    languages: list[dict],
    instance: str | None = None,
) -> dict:
    """Create a new language profile.

    Args:
        name: Profile name
        upgrade_allowed: Whether language upgrades are allowed
        cutoff: Language dict to use as the upgrade cutoff (e.g., {"id": 1, "name": "English"})
        languages: List of language dicts with allowed status
            (e.g., [{"language": {"id": 1, "name": "English"}, "allowed": True}])
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    data = {
        "name": name,
        "upgradeAllowed": upgrade_allowed,
        "cutoff": cutoff,
        "languages": languages,
    }
    result = await client.post("/api/v3/languageprofile", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def sonarr_update_language_profile(
    id: int,
    instance: str | None = None,
    **fields,
) -> dict:
    """Update an existing language profile.

    Args:
        id: Language profile ID to update
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
        **fields: Fields to update (name, upgradeAllowed, cutoff, languages)
    """
    client = resolve_instance(instance, "sonarr")
    current = await client.get(f"/api/v3/languageprofile/{id}")
    current.update(fields)
    result = await client.put(f"/api/v3/languageprofile/{id}", data=current)
    return result if isinstance(result, dict) else {"success": True, "id": id}


@mcp.tool()
async def sonarr_delete_language_profile(id: int, instance: str | None = None) -> dict:
    """Delete a language profile by ID.

    Args:
        id: Language profile ID to delete
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    await client.delete(f"/api/v3/languageprofile/{id}")
    return {"success": True, "id": id, "message": f"Language profile {id} deleted"}


@mcp.tool()
async def sonarr_get_languages(instance: str | None = None) -> dict:
    """Get all available languages supported by Sonarr.

    Args:
        instance: Sonarr instance name (e.g., "sonarr", "sonarr4k"). When None, uses
            the first configured sonarr instance.
    """
    client = resolve_instance(instance, "sonarr")
    result = await client.get("/api/v3/language")
    return {"languages": result if isinstance(result, list) else []}
