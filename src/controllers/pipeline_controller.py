from fastapi import APIRouter, Depends
from src.services.airflow_service import AirflowService
from src.middlewares.auth import verify_token

router = APIRouter(tags=["Pipelines"])


@router.get("/pipelines")
def get_pipelines(current_user: dict = Depends(verify_token)):
    """Retorna lista de pipelines (DAGs) do Airflow."""
    return AirflowService.get_pipelines()


@router.get("/app/dashboards/pipelines")
def get_all_pipeline_associations(current_user: dict = Depends(verify_token)):
    """Retorna todas as associações entre pipelines e dashboards."""
    return AirflowService.get_all_pipeline_associations()


@router.get("/app/dashboards/{dashboard_id}/pipeline")
def get_dashboard_pipeline_association(
    dashboard_id: str, current_user: dict = Depends(verify_token)
):
    """Retorna a associação de pipeline para um dashboard específico."""
    return AirflowService.get_dashboard_pipeline_association(dashboard_id)


@router.get("/app/dashboards/{pipeline_id}/pipeline")
def get_pipeline_association(
    pipeline_id: str, current_user: dict = Depends(verify_token)
):
    """Retorna a associação de dashboard para uma pipeline específica."""
    return AirflowService.get_pipeline_association(pipeline_id)


@router.post("/app/pipelines/{pipeline_id}/dashboard/{dashboard_id}")
def create_pipeline_association(
    pipeline_id: str, dashboard_id: str, current_user: dict = Depends(verify_token)
):
    """Cria uma associação entre pipeline e dashboard."""
    return AirflowService.create_pipeline_association(dashboard_id, pipeline_id)


@router.delete("/app/dashboards/{dashboard_id}/pipeline")
def delete_pipeline_association(
    dashboard_id: str, current_user: dict = Depends(verify_token)
):
    """Deleta a associação de pipeline para um dashboard."""
    return AirflowService.delete_pipeline_association(dashboard_id)


@router.post("/app/pipeline/{pipeline_id}/refresh")
def refresh_pipeline_association(
    pipeline_id: str, current_user: dict = Depends(verify_token)
):
    """Executa (refresh) uma pipeline específica."""
    return AirflowService.refresh_pipeline(pipeline_id)
