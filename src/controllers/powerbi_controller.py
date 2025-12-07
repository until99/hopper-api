from fastapi import APIRouter, Depends
from services.powerbi_service import PowerBIService
from middlewares.auth import verify_token

router = APIRouter(tags=["Power BI"])


@router.get("/dashboards")
def read_dashboards(current_user: dict = Depends(verify_token)):
    """Retorna lista de dashboards do Power BI."""
    return PowerBIService.get_dashboards()


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
