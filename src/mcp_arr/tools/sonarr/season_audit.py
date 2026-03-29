"""Season-level download audit tools for Sonarr."""

from typing import Any

from ...server import mcp, resolve_instance


@mcp.tool()
async def sonarr_season_download_protocols(
    season_number: int,
    series_id: int | None = None,
    series_title: str | None = None,
    instance: str | None = None,
) -> dict[str, Any]:
    """Check whether each episode in a season was downloaded via usenet or torrent.

    Cross-references episode files with download history to show the protocol
    used for each episode's most recent successful import. Useful for identifying
    episodes that came from torrents when you'd prefer everything via usenet,
    or for auditing a season before upgrading.

    Either series_id or series_title must be provided. If series_title is given,
    a case-insensitive search is performed against the library.

    Args:
        season_number: Season number to audit (e.g., 2 for Season 2).
        series_id: Sonarr series ID (preferred — unambiguous).
        series_title: Series title to search for (partial match supported).
        instance: Sonarr instance name. Uses default Sonarr instance if not specified.

    Returns:
        Per-episode breakdown with protocol (usenet/torrent/unknown), download
        client name, quality, and file status. Also includes a summary count.
    """
    client = resolve_instance(instance, "sonarr")

    # ── Resolve series ────────────────────────────────────────────────────────
    if series_id is None:
        if series_title is None:
            return {"error": "Either series_id or series_title must be provided."}
        all_series: list = await client.get("/api/v3/series")
        needle = series_title.lower()
        matches = [
            s for s in all_series
            if needle in s.get("title", "").lower()
        ]
        if not matches:
            return {"error": f"No series found matching '{series_title}'."}
        if len(matches) > 1:
            return {
                "error": f"Multiple series match '{series_title}'. Use series_id instead.",
                "matches": [{"id": s["id"], "title": s["title"]} for s in matches],
            }
        series_id = matches[0]["id"]
        series_name = matches[0]["title"]
    else:
        series_data = await client.get(f"/api/v3/series/{series_id}")
        series_name = series_data.get("title", f"Series {series_id}")

    # ── Fetch episodes for the season ─────────────────────────────────────────
    episodes: list = await client.get(
        "/api/v3/episode",
        params={"seriesId": series_id, "seasonNumber": season_number},
    )
    if not episodes:
        return {
            "series": series_name,
            "season": season_number,
            "error": f"No episodes found for Season {season_number}.",
        }

    # ── Fetch download history for the series/season ──────────────────────────
    # eventType 4 = downloadFolderImported (successful import, has protocol info)
    # eventType 1 = grabbed (also has protocol, fallback if no import record)
    history_imported: list = await client.get(
        "/api/v3/history/series",
        params={"seriesId": series_id, "seasonNumber": season_number, "eventType": 4},
    )
    history_grabbed: list = await client.get(
        "/api/v3/history/series",
        params={"seriesId": series_id, "seasonNumber": season_number, "eventType": 1},
    )

    # Sonarr stores protocol as "1" (usenet) or "2" (torrent) integer strings
    _PROTOCOL_MAP = {"1": "usenet", "2": "torrent", "usenet": "usenet", "torrent": "torrent"}

    def _parse_record(record: dict, event: str) -> dict:
        data = record.get("data", {})
        raw_proto = str(data.get("protocol", "")).lower()
        return {
            "protocol": _PROTOCOL_MAP.get(raw_proto, "unknown"),
            "download_client": data.get("downloadClientName") or data.get("downloadClient", ""),
            "release_title": record.get("sourceTitle", ""),
            "event": event,
            "date": record.get("date", ""),
        }

    # Build lookup: episodeId → most recent imported record, then grabbed as fallback
    # History is returned newest-first so first match per episodeId is the latest.
    ep_protocol: dict[int, dict] = {}

    for record in history_imported:
        ep_id = record.get("episodeId")
        if ep_id and ep_id not in ep_protocol:
            ep_protocol[ep_id] = _parse_record(record, "imported")

    for record in history_grabbed:
        ep_id = record.get("episodeId")
        if ep_id and ep_id not in ep_protocol:
            ep_protocol[ep_id] = _parse_record(record, "grabbed_only")

    # ── Build per-episode result ───────────────────────────────────────────────
    episode_results = []
    counts: dict[str, int] = {"usenet": 0, "torrent": 0, "unknown": 0, "missing": 0}

    for ep in sorted(episodes, key=lambda e: e.get("episodeNumber", 0)):
        ep_id = ep.get("id")
        ep_num = ep.get("episodeNumber", 0)
        ep_title = ep.get("title", "")
        has_file = ep.get("hasFile", False)
        monitored = ep.get("monitored", True)

        if not has_file:
            counts["missing"] += 1
            episode_results.append({
                "episode": ep_num,
                "title": ep_title,
                "has_file": False,
                "monitored": monitored,
                "protocol": None,
                "download_client": None,
                "release_title": None,
            })
            continue

        info = ep_protocol.get(ep_id)
        if info:
            protocol = info["protocol"].lower()
            counts[protocol] = counts.get(protocol, 0) + 1
            episode_results.append({
                "episode": ep_num,
                "title": ep_title,
                "has_file": True,
                "monitored": monitored,
                "protocol": protocol,
                "download_client": info["download_client"],
                "release_title": info["release_title"],
                "history_event": info["event"],
                "download_date": info["date"],
            })
        else:
            # Has a file but no history record (manually imported, or history pruned)
            counts["unknown"] += 1
            episode_results.append({
                "episode": ep_num,
                "title": ep_title,
                "has_file": True,
                "monitored": monitored,
                "protocol": "unknown",
                "download_client": None,
                "release_title": None,
                "history_event": "no_history",
            })

    return {
        "series": series_name,
        "series_id": series_id,
        "season": season_number,
        "summary": {
            "total_episodes": len(episodes),
            "usenet": counts["usenet"],
            "torrent": counts["torrent"],
            "unknown": counts["unknown"],
            "missing_file": counts["missing"],
        },
        "episodes": episode_results,
    }
