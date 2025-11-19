from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.auth_service import AuthService

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifica o token de autenticação do usuário no PocketBase.
    Retorna os dados do usuário autenticado.
    """
    token = credentials.credentials
    return AuthService.verify_token(token)
