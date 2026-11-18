import hmac
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    senha: str


@router.post("/login")
def login(request: LoginRequest):
    """
    Endpoint de login para gerar JWT token.
    Senha: variável de ambiente ADMIN_PASSWORD.
    """
    admin_password = settings.ADMIN_PASSWORD

    # Sem ADMIN_PASSWORD configurada, ninguém consegue logar
    if not admin_password or not hmac.compare_digest(
        request.senha.encode(), admin_password.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta",
        )

    # Gerar token válido por 7 dias
    access_token = create_access_token(
        data={"role": "admin"},
        expires_delta=timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_days": 7
    }
