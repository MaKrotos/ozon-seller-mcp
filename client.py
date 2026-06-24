"""
Ozon API Client handler.
Responsible for authentication, HTTP session management, and raw request execution.
"""
import os
import httpx
from typing import Any, Dict, Optional

BASE_URL = "https://api-seller.ozon.ru"

class OzonClient:
    """
    Dedicated client for interacting with Ozon Seller API.
    """
    def __init__(self):
        self.client_id = os.environ.get("OZON_CLIENT_ID")
        self.api_key = os.environ.get("OZON_API_KEY")
        
        if not self.client_id or not self.api_key:
            raise ValueError("OZON_CLIENT_ID and OZON_API_KEY environment variables are required")
        
        self._http_client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Singleton pattern for httpx client to reuse connections."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=BASE_URL,
                headers={
                    "Client-Id": self.client_id,
                    "Api-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._http_client

    async def post(self, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic POST request handler with structured error reporting."""
        client = await self.get_client()
        try:
            resp = await client.post(path, json=body or {})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        except Exception as e:
            return {"error": "RequestException", "detail": str(e)}
