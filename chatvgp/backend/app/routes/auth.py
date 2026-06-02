from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.config import settings
from app.utils.security import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    senha: str

@router.post("/login")
def login(request: LoginRequest):
    """
    Endpoint de login para gerar JWT token.
    Senha: ADMIN_SECRET (configurar em env var).
    """
    admin_secret = settings.SECRET_KEY  # Usar SECRET_KEY como senha admin

    if request.senha != admin_secret:
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
