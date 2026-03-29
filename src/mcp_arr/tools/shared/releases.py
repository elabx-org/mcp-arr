"""Release management tools — works for both Sonarr and Radarr instances."""

from collections import defaultdict

from ...server import get_client, mcp, resolve_instance


@mcp.tool()
async def arr_grab_release(
    guid: str,
    indexer_id: int,
    instance: str | None = None,
) -> dict:
    """Grab / download a specific release by GUID from a specific indexer.

    Args:
        guid: Release GUID as returned by a search
        indexer_id: ID of the indexer that has the release
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    data = {"guid": guid, "indexerId": indexer_id}
    result = await client.post("/api/v3/release", data=data)
    return result if isinstance(result, dict) else {"success": True, "guid": guid}


@mcp.tool()
async def arr_push_release(
    instance: str | None = None,
    title: str | None = None,
    download_url: str | None = None,
    protocol: str = "usenet",
    publish_date: str | None = None,
    **kwargs,
) -> dict:
    """Push a release notification directly to the instance for processing.

    Args:
        instance: Instance name (e.g., "sonarr", "radarr"). When None, uses the
            first configured instance regardless of type.
        title: Release title (NZB or torrent name)
        download_url: Direct download URL for the release
        protocol: "usenet" or "torrent" (default "usenet")
        publish_date: ISO 8601 publish date string
        **kwargs: Additional release fields passed through to the API
    """
    client = get_client(instance) if instance else resolve_instance(None, "sonarr")
    data: dict = {"protocol": protocol}
    if title:
        data["title"] = title
    if download_url:
        data["downloadUrl"] = download_url
    if publish_date:
        data["publishDate"] = publish_date
    data.update(kwargs)
    result = await client.post("/api/v3/release/push", data=data)
    return result if isinstance(result, dict) else {"success": True}


@mcp.tool()
async def arr_plan_grab(
    releases: list[dict],
    release_group: str | None = None,
    preferred_protocol: str = "usenet",
    spread_indexers: bool = True,
    indexer_priority: list[str] | None = None,
) -> dict:
    """Plan an optimal grab strategy from search results. No API calls made — pure planning tool.

    Filters releases by release group (if specified), prefers the preferred protocol
    (usenet over torrent by default), and optionally distributes episode grabs
    round-robin across available indexers to balance load.

    Fallback chains are ordered so that a different indexer is tried before another
    copy from the same indexer — because if one NZB on an indexer returns NNTP 451
    (article expired), all other NZBs for the same release on that indexer will too.
    Within each indexer tier, releases are sorted youngest-first (smallest age value)
    since newer binary articles are more likely to still be live on usenet servers.

    Use arr_grab_release to execute each item in the returned plan.

    Args:
        releases: List of release dicts from sonarr_search_season_releases,
            sonarr_search_episode_releases, or radarr_search_movie_releases.
            Each dict should have: guid, title, indexerId, indexer, protocol,
            quality (dict with quality.name), size, episodeNumbers (Sonarr) or
            movieId (Radarr), fullSeason (Sonarr), releaseGroup.
        release_group: If set, only consider releases whose releaseGroup contains
            this string (case-insensitive partial match).
        preferred_protocol: Prefer "usenet" or "torrent". Falls back to the other
            protocol only when no preferred option is available for a given episode.
        spread_indexers: When True, distribute episode grab assignments round-robin
            across unique indexers to balance load. When False, use the best
            release per episode without indexer spreading.
        indexer_priority: Optional ordered list of indexer name substrings to prefer
            when selecting the primary and ordering fallbacks (case-insensitive).
            E.g. ["nzb.life", "drunkenslug"] tries nzb.life copies before drunkenslug.
            Indexers not in the list are ranked last but still used as fallbacks.

    Returns:
        Dict with "plan" list and "summary" statistics.
    """
    # Build indexer rank function from priority list
    priority_lower = [p.lower() for p in (indexer_priority or [])]

    def _indexer_rank(r: dict) -> int:
        """Lower is better. Unranked indexers get len(priority_lower)."""
        name = (r.get("indexer") or "").lower()
        for i, p in enumerate(priority_lower):
            if p in name:
                return i
        return len(priority_lower)

    # Filter by release group if specified
    filtered = releases
    if release_group:
        rg_lower = release_group.lower()
        filtered = [
            r for r in filtered
            if rg_lower in (r.get("releaseGroup") or "").lower()
        ]

    # Separate season packs from individual episodes
    season_packs = [r for r in filtered if r.get("fullSeason", False)]
    episode_releases = [r for r in filtered if not r.get("fullSeason", False)]

    def _protocol_rank(r: dict) -> int:
        """Lower is better. 0 = preferred, 1 = fallback."""
        return 0 if r.get("protocol", "").lower() == preferred_protocol.lower() else 1

    plan: list[dict] = []

    # Handle season packs first — pick best one
    if season_packs:
        preferred_packs = [r for r in season_packs if _protocol_rank(r) == 0]
        candidates = preferred_packs if preferred_packs else season_packs
        best = sorted(candidates, key=lambda r: r.get("seeders", 0) if r.get("protocol") == "torrent" else 0, reverse=True)[0]
        plan.append({
            "episode_numbers": [],
            "full_season": True,
            "title": best.get("title", ""),
            "release_group": best.get("releaseGroup"),
            "protocol": best.get("protocol", ""),
            "indexer": best.get("indexer", ""),
            "indexer_id": best.get("indexerId"),
            "guid": best.get("guid", ""),
            "size": best.get("size", 0),
            "quality": (best.get("quality") or {}).get("quality", {}).get("name", ""),
            "warning": None if _protocol_rank(best) == 0 else "torrent_fallback",
        })
        # If we have a season pack, no need to plan individual episodes
        ep_numbers_covered = set()
        for r in episode_releases:
            for ep in r.get("episodeNumbers", []):
                ep_numbers_covered.add(ep)
        total_episodes = len(ep_numbers_covered)
        return {
            "plan": plan,
            "summary": {
                "total_episodes": total_episodes,
                "covered": total_episodes,
                "missing": 0,
                "usenet": 1 if plan[0]["protocol"] == "usenet" else 0,
                "torrent_fallback": 1 if plan[0].get("warning") == "torrent_fallback" else 0,
                "indexers_used": list({p["indexer"] for p in plan}),
            },
        }

    # Group individual episode releases by episode number
    by_episode: dict[int, list[dict]] = defaultdict(list)
    for r in episode_releases:
        for ep_num in r.get("episodeNumbers", []):
            by_episode[ep_num].append(r)

    all_episode_numbers = sorted(by_episode.keys())
    total_episodes = len(all_episode_numbers)

    if not all_episode_numbers:
        return {
            "plan": [],
            "summary": {
                "total_episodes": 0,
                "covered": 0,
                "missing": 0,
                "usenet": 0,
                "torrent_fallback": 0,
                "indexers_used": [],
            },
        }

    # Collect indexers that have at least one episode
    all_indexers: list[str] = []
    seen_indexers: set[str] = set()
    for ep_num in all_episode_numbers:
        for r in by_episode[ep_num]:
            idxr = r.get("indexer", "")
            if idxr and idxr not in seen_indexers:
                all_indexers.append(idxr)
                seen_indexers.add(idxr)

    # Round-robin indexer assignment
    indexer_cycle_pos = 0
    usenet_count = 0
    torrent_fallback_count = 0
    covered = 0

    for ep_num in all_episode_numbers:
        candidates = by_episode[ep_num]
        preferred_candidates = [r for r in candidates if _protocol_rank(r) == 0]
        fallback_candidates = [r for r in candidates if _protocol_rank(r) != 0]

        if not candidates:
            continue

        covered += 1

        # Sort preferred candidates: indexer priority first, then age ascending
        # (younger NZBs are more likely to have live binary articles on usenet)
        preferred_candidates.sort(key=lambda r: (_indexer_rank(r), r.get("age", 999999)))
        fallback_candidates.sort(key=lambda r: (_indexer_rank(r), r.get("age", 999999)))

        if spread_indexers and len(all_indexers) > 1:
            # Try to assign to the next indexer in round-robin order,
            # respecting indexer priority when multiple options exist
            chosen = None
            for attempt in range(len(all_indexers)):
                target_indexer = all_indexers[(indexer_cycle_pos + attempt) % len(all_indexers)]
                # Find a preferred-protocol release from this indexer
                for r in preferred_candidates:
                    if r.get("indexer", "") == target_indexer:
                        chosen = r
                        indexer_cycle_pos = (indexer_cycle_pos + attempt + 1) % len(all_indexers)
                        break
                if chosen:
                    break

            if not chosen:
                # Fall back: any indexer, preferred protocol
                if preferred_candidates:
                    chosen = preferred_candidates[0]
                elif fallback_candidates:
                    chosen = fallback_candidates[0]
                else:
                    chosen = candidates[0]
                indexer_cycle_pos = (indexer_cycle_pos + 1) % len(all_indexers)
        else:
            # No spreading — pick best by indexer priority, then age
            if preferred_candidates:
                chosen = preferred_candidates[0]
            elif fallback_candidates:
                chosen = fallback_candidates[0]
            else:
                chosen = candidates[0]

        is_fallback = _protocol_rank(chosen) != 0
        if is_fallback:
            torrent_fallback_count += 1
        else:
            usenet_count += 1

        # Build fallback list: other indexers first, then same-indexer duplicates last.
        #
        # Rationale: if a NZB returns NNTP 451 (article expired/missing), every other
        # NZB for the same release on that same indexer will also return 451 — they all
        # reference the same binary articles on the usenet server. Trying a different
        # indexer's copy of the same release is the right first move.
        #
        # Within each tier, sort by indexer priority then age ascending (youngest first),
        # since newer binary articles are more likely to still be live.
        other_indexer = sorted(
            [r for r in candidates if r.get("guid") != chosen.get("guid") and r.get("indexer") != chosen.get("indexer")],
            key=lambda r: (_indexer_rank(r), r.get("age", 999999)),
        )
        same_indexer_others = sorted(
            [r for r in candidates if r.get("guid") != chosen.get("guid") and r.get("indexer") == chosen.get("indexer")],
            key=lambda r: r.get("age", 999999),
        )
        fallback_guids = [
            {"guid": r.get("guid"), "indexer_id": r.get("indexerId"), "indexer": r.get("indexer"), "title": r.get("title", "")}
            for r in other_indexer + same_indexer_others
        ]

        plan.append({
            "episode_numbers": [ep_num],
            "full_season": False,
            "title": chosen.get("title", ""),
            "release_group": chosen.get("releaseGroup"),
            "protocol": chosen.get("protocol", ""),
            "indexer": chosen.get("indexer", ""),
            "indexer_id": chosen.get("indexerId"),
            "guid": chosen.get("guid", ""),
            "size": chosen.get("size", 0),
            "quality": (chosen.get("quality") or {}).get("quality", {}).get("name", ""),
            "warning": "torrent_fallback" if is_fallback else None,
            "fallback_guids": fallback_guids,
        })

    return {
        "plan": plan,
        "summary": {
            "total_episodes": total_episodes,
            "covered": covered,
            "missing": total_episodes - covered,
            "usenet": usenet_count,
            "torrent_fallback": torrent_fallback_count,
            "indexers_used": list({p["indexer"] for p in plan if p["indexer"]}),
        },
    }
