import datetime
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.core.encryption import encrypt_token, decrypt_token
from src.app.models.token import OAuthToken


class TokenService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_valid_token(self) -> str | None:
        """Get a valid access token, refreshing if needed."""
        result = await self.db.execute(
            select(OAuthToken).order_by(OAuthToken.id.desc()).limit(1)
        )
        token = result.scalar_one_or_none()
        if token is None:
            return None

        # Check if token is expired (with 60s buffer)
        if token.expires_at <= datetime.datetime.utcnow() + datetime.timedelta(seconds=60):
            if token.refresh_token_encrypted:
                refreshed = await self._refresh_token(token)
                if refreshed:
                    return decrypt_token(refreshed.access_token_encrypted)
            return None

        return decrypt_token(token.access_token_encrypted)

    async def store_token(
        self,
        access_token: str,
        refresh_token: str | None,
        expires_in: int,
        scope: str | None = None,
        token_type: str = "Bearer",
    ) -> OAuthToken:
        """Store a new OAuth token (encrypted)."""
        oauth_token = OAuthToken(
            access_token_encrypted=encrypt_token(access_token),
            refresh_token_encrypted=encrypt_token(refresh_token) if refresh_token else None,
            token_type=token_type,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
            scope=scope,
        )
        self.db.add(oauth_token)
        await self.db.commit()
        await self.db.refresh(oauth_token)
        return oauth_token

    async def _refresh_token(self, token: OAuthToken) -> OAuthToken | None:
        """Refresh an expired token using the refresh token."""
        refresh_tok = decrypt_token(token.refresh_token_encrypted)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.erste_token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_tok,
                    "client_id": settings.erste_client_id,
                    "client_secret": settings.erste_client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code != 200:
            return None

        data = response.json()
        return await self.store_token(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", refresh_tok),
            expires_in=data.get("expires_in", 3600),
            scope=data.get("scope"),
            token_type=data.get("token_type", "Bearer"),
        )
