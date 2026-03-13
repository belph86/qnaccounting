import urllib.parse
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.core.database import get_db
from src.app.services.token_service import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login():
    """Redirect user to Erste OAuth consent screen."""
    params = {
        "client_id": settings.erste_client_id,
        "redirect_uri": settings.erste_redirect_uri,
        "response_type": "code",
        "scope": "AISP",
    }
    auth_url = f"{settings.erste_auth_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle OAuth callback and exchange code for tokens."""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.erste_token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.erste_client_id,
                "client_secret": settings.erste_client_secret,
                "redirect_uri": settings.erste_redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Token exchange failed: {response.text}",
        )

    data = response.json()
    token_service = TokenService(db)
    await token_service.store_token(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in", 3600),
        scope=data.get("scope"),
        token_type=data.get("token_type", "Bearer"),
    )

    return {"message": "Authentication successful", "scope": data.get("scope")}


@router.get("/status")
async def auth_status(db: AsyncSession = Depends(get_db)):
    """Check if we have a valid token."""
    token_service = TokenService(db)
    token = await token_service.get_valid_token()
    return {"authenticated": token is not None}
