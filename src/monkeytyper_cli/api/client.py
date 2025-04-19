import httpx
from typing import Any, Dict, Optional, List
import sys
from pydantic import ValidationError

from monkeytyper_cli.config.settings import settings # Main settings with ApeKey
from monkeytyper_cli import __version__
from .models import UserStatsResponse, PersonalBestsResponse, LeaderboardResponse

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

class ApiClientError(Exception):
    pass

class APIClient:
    """Handles communication with the Monkeytype API."""

    def __init__(
        self,
        base_url: str = settings.api_base_url,
        api_key: Optional[str] = settings.monkeytype_ape_key,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Returns an httpx AsyncClient instance, creating it if necessary."""
        if self._client is None:
            headers = {
                "User-Agent": f"MonkeyTyper-CLI/{__version__}",
                "Accept": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"ApeKey {self.api_key}"
            
            self._client = httpx.AsyncClient(
                base_url=self.base_url, 
                headers=headers, 
                timeout=DEFAULT_TIMEOUT
            )
        return self._client

    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Makes an async API request and handles common errors."""
        client = await self._get_client()
        try:
            response = await client.request(method, endpoint, params=params, json=json_data)
            response.raise_for_status() 
            
            if not response.content:
                 return {} 
            
            try:
                 return response.json()
            except ValueError: 
                 raise ApiClientError("Invalid JSON response from server", response.status_code)

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            raise
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            raise

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Performs an asynchronous GET request."""
        response = await self._request("GET", endpoint, params=params)
        return response

    async def close(self) -> None:
        """Closes the underlying httpx AsyncClient."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_personal_bests(self) -> PersonalBestsResponse:
        """Fetches personal bests. Requires ApeKey."""
        endpoint = "/users/personalBests" 
        if not self.api_key:
            raise ApiClientError("ApeKey is required to fetch personal bests.")
        try:
            raw_data = await self._request("GET", endpoint)
            return PersonalBestsResponse(**raw_data)
        except ValidationError as e:
             raise ApiClientError(f"Failed to parse personal bests response: {e}")
        except ApiClientError as e:
            raise

    async def get_user_stats(self) -> UserStatsResponse:
        """Fetches general user stats. Requires ApeKey."""
        endpoint = "/users/stats" 
        if not self.api_key:
            raise ApiClientError("ApeKey is required to fetch user stats.")
        try:
            raw_data = await self._request("GET", endpoint)
            return UserStatsResponse(**raw_data)
        except ValidationError as e:
            raise ApiClientError(f"Failed to parse user stats response: {e}")
        except ApiClientError as e:
            raise

    async def get_leaderboard(self, mode: str, language: str) -> LeaderboardResponse:
        """Fetches public leaderboards."""
        endpoint = "/leaderboards" 
        params = {"mode": mode, "language": language}
        try:
            raw_data = await self._request("GET", endpoint, params=params)
            return LeaderboardResponse(**raw_data)
        except ValidationError as e:
            raise ApiClientError(f"Failed to parse leaderboard response: {e}")
        except ApiClientError as e:
            raise
