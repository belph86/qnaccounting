from cryptography.fernet import Fernet

from src.app.core.config import settings


def get_fernet() -> Fernet:
    if not settings.token_encryption_key:
        raise ValueError(
            "TOKEN_ENCRYPTION_KEY not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(settings.token_encryption_key.encode())


def encrypt_token(token: str) -> str:
    return get_fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return get_fernet().decrypt(encrypted_token.encode()).decode()
