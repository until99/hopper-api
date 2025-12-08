from fastapi import APIRouter, Depends
from models.group import IGroupUpdate
from services.group_service import GroupService
from services.user_service import UserService
from services.powerbi_service import PowerBIService
from middlewares.auth import verify_token

router = APIRouter(prefix="/app", tags=["Groups"])


@router.get("/groups/{group_id}")
def read_hopper_group(group_id: str, current_user: dict = Depends(verify_token)):
    """Retorna os dados de um grupo específico."""
    return GroupService.get_group(group_id)


@router.get("/groups")
def read_hopper_groups(current_user: dict = Depends(verify_token)):
    """Retorna lista de grupos."""
    return GroupService.get_groups()


@router.post("/groups")
def create_hopper_group(
    name: str,
    description: str,
    active: bool = True,
    current_user: dict = Depends(verify_token),
):
    """Cria um novo grupo."""
    return GroupService.create_group(name, description, active)


@router.patch("/groups/{group_id}")
def update_hopper_group(
    group_id: str,
    group_data: IGroupUpdate,
    current_user: dict = Depends(verify_token),
):
    """Atualiza os dados de um grupo."""
    update_data = group_data.model_dump(exclude_none=True)
    return GroupService.update_group(group_id, update_data)


@router.put("/groups/{group_id}")
def update_hopper_group_put(
    group_id: str,
    group_data: IGroupUpdate,
    current_user: dict = Depends(verify_token),
):
    """Atualiza os dados de um grupo (PUT)."""
    update_data = group_data.model_dump(exclude_none=True)
    return GroupService.update_group(group_id, update_data)


@router.delete("/groups/{group_id}")
def delete_hopper_group(group_id: str, current_user: dict = Depends(verify_token)):
    """Deleta um grupo."""
    return GroupService.delete_group(group_id)


@router.get("/groups/{group_id}/users")
def read_hopper_group_users(group_id: str, current_user: dict = Depends(verify_token)):
    """Retorna lista de usuários de um grupo."""
    return GroupService.get_group_users(group_id)


@router.get("/users/{user_id}/groups")
def read_user_groups(user_id: str, current_user: dict = Depends(verify_token)):
    """Retorna todos os grupos em que o usuário pertence."""
    return UserService.get_user_groups(user_id)


@router.get("/groups/{group_id}/dashboards")
def read_hopper_group_dashboards(
    group_id: str, current_user: dict = Depends(verify_token)
):
    """Retorna lista de dashboards de um grupo."""
    all_dashboards_response = PowerBIService.get_dashboards()
    all_dashboards_list = all_dashboards_response.get("dashboards", [])
    return GroupService.get_group_dashboards(group_id, all_dashboards_list)


@router.post("/groups/{group_id}/users/{user_id}")
def add_user_to_group(
    group_id: str, user_id: str, current_user: dict = Depends(verify_token)
):
    """Adiciona um usuário a um grupo."""
    return GroupService.add_user_to_group(group_id, user_id)


@router.delete("/groups/{group_id}/users/{user_id}")
def remove_user_from_group(
    group_id: str, user_id: str, current_user: dict = Depends(verify_token)
):
    """Remove um usuário de um grupo."""
    return GroupService.remove_user_from_group(group_id, user_id)


@router.post("/groups/{group_id}/dashboards/{dashboard_id}")
def add_dashboard_to_group(
    group_id: str, dashboard_id: str, current_user: dict = Depends(verify_token)
):
    """Adiciona um dashboard a um grupo."""
    return GroupService.add_dashboard_to_group(group_id, dashboard_id)


@router.delete("/groups/{group_id}/dashboards/{dashboard_id}")
def remove_dashboard_from_group(
    group_id: str, dashboard_id: str, current_user: dict = Depends(verify_token)
):
    """Remove um dashboard de um grupo."""
    return GroupService.remove_dashboard_from_group(group_id, dashboard_id)
