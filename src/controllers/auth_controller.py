from fastapi import APIRouter, Depends
from src.models.user import IUserAuthLogin, IUserAuthRegister
from src.services.auth_service import AuthService
from src.middlewares.auth import verify_token

router = APIRouter(prefix="/user", tags=["Authentication"])


@router.post("/auth")
def auth(user: IUserAuthLogin):
    """Autentica o usuário com email e senha."""
    return AuthService.login(user.email, user.password)


@router.post("/register")
def register(user: IUserAuthRegister):
    """Registra um novo usuário."""
    return AuthService.register(
        user.username, user.email, user.password, user.confirm_password, user.role
    )


@router.post("/logout")
def logout(current_user: dict = Depends(verify_token)):
    """Logout do usuário (gerenciado no cliente)."""
    return {"message": "Logged out"}
