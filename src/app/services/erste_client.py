import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.services.token_service import TokenService


class ErsteApiClient:
    """Client for Česká spořitelna / Erste Group API."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.token_service = TokenService(db)
        self.base_url = settings.erste_api_base_url.rstrip("/")

    async def _get_headers(self) -> dict:
        token = await self.token_service.get_valid_token()
        if not token:
            raise RuntimeError("No valid OAuth token available. Please authenticate first.")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "WEB-API-key": settings.erste_client_id,
        }

    async def get_accounts(self) -> dict:
        """Fetch list of accounts from Erste API."""
        headers = await self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/netbanking/my/accounts",
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_transactions(self, account_id: str, date_from: str | None = None, date_to: str | None = None) -> dict:
        """Fetch transactions for a specific account."""
        headers = await self._get_headers()
        params = {}
        if date_from:
            params["dateStart"] = date_from
        if date_to:
            params["dateEnd"] = date_to

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/netbanking/my/accounts/{account_id}/transactions",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()
