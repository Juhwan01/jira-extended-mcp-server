"""Async Jira REST API client with rate-limit retry."""

from __future__ import annotations

import asyncio
import base64
import os
from typing import Any

import httpx


class JiraClient:
    """Lightweight async Jira Cloud REST API client."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

        self.base_url = os.environ.get("JIRA_URL", "").rstrip("/")
        email = os.environ.get("JIRA_EMAIL", "")
        token = os.environ.get("JIRA_API_TOKEN", "")

        if not all([self.base_url, email, token]):
            raise RuntimeError(
                "Missing required env vars: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN"
            )

        creds = base64.b64encode(f"{email}:{token}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.start_date_field = os.environ.get(
            "JIRA_START_DATE_FIELD", "customfield_10015"
        )

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._headers,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any] | list[Any] | None:
        """Make an API request with automatic rate-limit retry."""
        for attempt in range(max_retries + 1):
            resp = await self.client.request(
                method, path, json=json, params=params
            )

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "2"))
                if attempt < max_retries:
                    await asyncio.sleep(retry_after)
                    continue
                return {
                    "error": "Rate limited",
                    "status": 429,
                    "retry_after": retry_after,
                }

            if resp.status_code == 204:
                return {"success": True}

            if resp.status_code >= 400:
                try:
                    body = resp.json()
                except Exception:
                    body = resp.text
                return {
                    "error": body,
                    "status": resp.status_code,
                }

            if not resp.content:
                return {"success": True}

            return resp.json()

        return {"error": "Max retries exceeded", "status": 429}

    # Convenience methods

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, json: Any = None) -> Any:
        return await self.request("POST", path, json=json)

    async def put(self, path: str, json: Any = None) -> Any:
        return await self.request("PUT", path, json=json)

    async def delete(
        self, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        return await self.request("DELETE", path, params=params)
