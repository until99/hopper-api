from fastapi import APIRouter, Depends
from services.powerbi_service import PowerBIService
from services.user_service import UserService
from services.group_service import GroupService
from middlewares.auth import verify_token

router = APIRouter(tags=["Power BI"])


@router.get("/dashboards")
def read_dashboards(current_user: dict = Depends(verify_token)):
    """Retorna lista de dashboards do Power BI filtrados pelos grupos do usuário."""
    user_id = current_user.get("record", {}).get("id")
    
    if not user_id:
        return {"dashboards": []}
    
    # Busca todos os grupos do usuário
    user_groups_response = UserService.get_user_groups(user_id)
    user_groups = user_groups_response.get("groups", [])
    
    if not user_groups:
        return {"dashboards": []}
    
    # Busca todos os dashboards do Power BI
    all_dashboards_response = PowerBIService.get_dashboards()
    all_dashboards = all_dashboards_response.get("dashboards", [])
    
    # Coleta todos os dashboard_ids dos grupos do usuário
    dashboard_ids = set()
    for group in user_groups:
        group_id = group.get("id")
        group_dashboards = GroupService.get_group_dashboards(group_id, all_dashboards)
        for dashboard in group_dashboards:
            dashboard_ids.add(dashboard.get("id"))
    
    # Filtra apenas os dashboards que pertencem aos grupos do usuário
    filtered_dashboards = [
        dashboard for dashboard in all_dashboards 
        if dashboard.get("id") in dashboard_ids
    ]
    
    return {"dashboards": filtered_dashboards}


@router.get("/groups")
def read_groups(current_user: dict = Depends(verify_token)):
    """Retorna a lista de grupos do Power BI."""
    return PowerBIService.get_groups()


@router.get("/groups/{group_id}/reports")
def read_reports(group_id: str, current_user: dict = Depends(verify_token)):
    """Retorna a lista de relatórios em um grupo específico do Power BI."""
    return PowerBIService.get_reports(group_id)


@router.get("/groups/{group_id}/report/{report_id}")
def read_report(
    group_id: str, report_id: str, current_user: dict = Depends(verify_token)
):
    """Retorna um relatório específico de um grupo do Power BI."""
    return PowerBIService.get_report(group_id, report_id)


@router.delete("/groups/{group_id}/report/{report_id}/dataset/{dataset_id}")
def delete_report(
    group_id: str,
    report_id: str,
    dataset_id: str,
    current_user: dict = Depends(verify_token),
):
    """Deleta um relatório específico de um grupo do Power BI."""
    return PowerBIService.delete_report(group_id, report_id, dataset_id)
