from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Erste / ČS API
    erste_client_id: str = ""
    erste_client_secret: str = ""
    erste_redirect_uri: str = "http://localhost:8000/auth/callback"
    erste_sandbox: bool = True
    erste_api_base_url: str = "https://webapi.developers.erstegroup.com/api/csas/public/sandbox/v3"

    # Database
    database_url: str = "sqlite+aiosqlite:///./banking.db"

    # Agent API
    agent_api_key: str = ""

    # Synchronization
    sync_interval_minutes: int = 15

    # Token encryption key (Fernet key)
    token_encryption_key: str = ""

    @property
    def erste_auth_url(self) -> str:
        return "https://webapi.developers.erstegroup.com/api/csas/public/sandbox/v3/sandbox-idp/authorize"

    @property
    def erste_token_url(self) -> str:
        return "https://webapi.developers.erstegroup.com/api/csas/public/sandbox/v3/sandbox-idp/token"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
