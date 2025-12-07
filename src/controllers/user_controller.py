from fastapi import APIRouter, Depends
from models.user import IUserUpdate
from services.user_service import UserService
from middlewares.auth import verify_token

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/{user_id}")
def read_user(user_id: str, current_user: dict = Depends(verify_token)):
    """Retorna os dados de um usuário específico."""
    return UserService.get_user(user_id)


@router.get("s")
def read_users(
    page: int = 1, perPage: int = 30, current_user: dict = Depends(verify_token)
):
    """Retorna lista paginada de usuários."""
    return UserService.get_users(page, perPage)


@router.post("")
def create_user(
    username: str,
    email: str,
    password: str,
    passwordConfirm: str,
    role: str,
    current_user: dict = Depends(verify_token),
):
    """Cria um novo usuário."""
    return UserService.create_user(username, email, password, passwordConfirm, role)


@router.patch("/{user_id}")
def update_user(
    user_id: str,
    user_data: IUserUpdate,
    current_user: dict = Depends(verify_token),
):
    """Atualiza os dados de um usuário."""
    update_data = user_data.model_dump(exclude_none=True)
    return UserService.update_user(user_id, update_data)


@router.delete("/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(verify_token)):
    """Deleta um usuário."""
    return UserService.delete_user(user_id)
