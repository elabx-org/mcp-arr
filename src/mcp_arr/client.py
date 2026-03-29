"""Sonarr/Radarr API HTTP client."""

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Release searches query live indexers and can take 60-120s.
# Override with ARR_SEARCH_TIMEOUT env var (seconds).
_DEFAULT_TIMEOUT = float(os.environ.get("ARR_TIMEOUT", "30"))
_SEARCH_TIMEOUT = float(os.environ.get("ARR_SEARCH_TIMEOUT", "120"))

# Minimum delay between requests to the same instance (seconds).
# Prevents API hammering when making many sequential calls.
# Override with ARR_REQUEST_DELAY env var (e.g. "0.5").
_REQUEST_DELAY = float(os.environ.get("ARR_REQUEST_DELAY", "0.25"))


class ArrError(Exception):
    """Exception raised when a Sonarr/Radarr API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ArrClient:
    """Base async HTTP client for Sonarr/Radarr v3 API."""

    instance_type: str = "arr"

    def __init__(self, url: str, api_key: str, instance_name: str):
        """Initialize the client.

        Args:
            url: Base URL for the arr instance (e.g., http://sonarr:8989)
            api_key: X-Api-Key for the instance
            instance_name: Human-readable name for logging/error messages
        """
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.instance_name = instance_name
        self.headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }
        self.timeout = httpx.Timeout(_DEFAULT_TIMEOUT, connect=10.0)
        self.search_timeout = httpx.Timeout(_SEARCH_TIMEOUT, connect=10.0)
        self._last_request: float = 0.0

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> Any:
        """Make an HTTP request to the arr API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., /api/v3/series)
            params: Query string parameters
            data: Request body as dict (JSON)

        Returns:
            Parsed JSON response

        Raises:
            ArrError: If the request fails
        """
        # Rate limiting: enforce minimum delay between requests per instance
        if _REQUEST_DELAY > 0:
            import time
            elapsed = time.monotonic() - self._last_request
            if elapsed < _REQUEST_DELAY:
                await asyncio.sleep(_REQUEST_DELAY - elapsed)
            self._last_request = time.monotonic()

        url = f"{self.url}{path}"
        logger.debug("%s %s %s", method, url, params or data)

        async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
            )

            if not response.is_success:
                error_msg = f"{method} {path} failed"
                try:
                    error_body = response.json()
                    if isinstance(error_body, list) and error_body:
                        # Sonarr/Radarr often returns a list of error objects
                        first = error_body[0]
                        if isinstance(first, dict):
                            error_msg = first.get("errorMessage") or first.get("message") or str(first)
                        else:
                            error_msg = str(first)
                    elif isinstance(error_body, dict):
                        error_msg = (
                            error_body.get("message")
                            or error_body.get("error")
                            or str(error_body)
                        )
                    else:
                        error_msg = str(error_body)
                except Exception:
                    error_msg = (
                        f"{method} {path} failed: "
                        f"{response.status_code} {response.reason_phrase}"
                    )

                logger.error(
                    "[%s] API error: %s (status %d)",
                    self.instance_name,
                    error_msg,
                    response.status_code,
                )
                raise ArrError(error_msg, response.status_code)

            # Some endpoints return empty body on success (e.g., DELETE)
            if not response.content:
                return {}

            result = response.json()
            logger.debug("Response: %s", result)
            return result

    async def search_get(self, path: str, params: dict | None = None) -> Any:
        """GET with the extended search timeout (default 120s).

        Use for /api/v3/release endpoints that query live indexers.
        """
        return await self._request("GET", path, params=params, timeout=self.search_timeout)

    async def get(self, path: str, params: dict | None = None) -> Any:
        """Make a GET request.

        Args:
            path: API path
            params: Query string parameters

        Returns:
            Parsed JSON response
        """
        return await self._request("GET", path, params=params)

    async def post(self, path: str, data: dict | None = None) -> Any:
        """Make a POST request.

        Args:
            path: API path
            data: Request body

        Returns:
            Parsed JSON response
        """
        return await self._request("POST", path, data=data or {})

    async def put(self, path: str, data: dict | None = None) -> Any:
        """Make a PUT request.

        Args:
            path: API path
            data: Request body

        Returns:
            Parsed JSON response
        """
        return await self._request("PUT", path, data=data or {})

    async def delete(self, path: str, params: dict | None = None) -> Any:
        """Make a DELETE request.

        Args:
            path: API path
            params: Query string parameters

        Returns:
            Parsed JSON response (or empty dict)
        """
        return await self._request("DELETE", path, params=params)


class SonarrClient(ArrClient):
    """Sonarr-specific client."""

    instance_type = "sonarr"


class RadarrClient(ArrClient):
    """Radarr-specific client."""

    instance_type = "radarr"
