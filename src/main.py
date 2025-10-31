from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import msal
import requests
from datetime import datetime, timezone

load_dotenv()

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "https://hopper-app-gamma.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pocketbase_url = os.getenv("POCKETBASE_URL", "")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifica o token de autenticação do usuário no PocketBase.
    Retorna os dados do usuário autenticado.
    """
    token = credentials.credentials

    try:
        response = requests.post(
            pocketbase_url + "/api/collections/auth_users/auth-refresh",
            headers={
                "Authorization": f"Bearer {token}",
            },
            verify=False,
        )

        if response.status_code == 200:
            user_data = response.json()
            return user_data
        else:
            raise HTTPException(
                status_code=401,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Falha na autenticação",
            headers={"WWW-Authenticate": "Bearer"},
        )


class IUserAuthLogin(BaseModel):
    email: str = Field(default=..., examples=["user@example.com"])
    password: str = Field(default=..., examples=["securePassword123"])


class IUserAuthRegister(BaseModel):
    username: str = Field(default=..., examples=["user"])
    email: str = Field(default=..., examples=["user@example.com"])
    password: str = Field(default=..., examples=["securePassword123"])
    confirm_password: str = Field(default=..., examples=["securePassword123"])
    role: str = Field(default="user", examples=["user", "admin"])


def acquire_bearer_token() -> str | None:
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    app_msal = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )

    token_result = app_msal.acquire_token_for_client(
        scopes=["https://analysis.windows.net/powerbi/api/.default"]
    )

    if not token_result:
        return None

    if "access_token" in token_result:
        return token_result["access_token"]


@app.get("/")
def read_root():
    return {"Hello": "World"}


# User Endpoints
@app.get("/user/{user_id}")
def read_user(
    user_id: str,
    current_user: dict = Depends(verify_token),
):
    user = requests.get(
        pocketbase_url + f"/api/collections/auth_users/records/{user_id}",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    ).json()

    return user


@app.get("/users")
def read_users(
    page: int = 1, perPage: int = 30, current_user: dict = Depends(verify_token)
):
    users = requests.get(
        pocketbase_url
        + f"/api/collections/auth_users/records?page={page}&perPage={perPage}",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    ).json()

    result = []
    for user in users["items"]:
        result.append(
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "active": user["active"],
                "created": user["created"],
                "updated": user["updated"],
            }
        )

    return {
        "page": users["page"],
        "perPage": users["perPage"],
        "totalItems": users["totalItems"],
        "totalPages": users["totalPages"],
        "users": result,
    }


@app.post("/user")
def create_user(
    username: str,
    email: str,
    password: str,
    passwordConfirm: str,
    role: str,
    current_user: dict = Depends(verify_token),
):
    if password != passwordConfirm:
        return {"error": "Password and password confirmation do not match"}

    user = requests.post(
        pocketbase_url + "/api/collections/auth_users/records",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "username": username,
            "email": email,
            "password": password,
            "passwordConfirm": passwordConfirm,
            "role": role,
            "emailVisibility": True,
            "verify": True,
        },
        verify=False,
    ).json()

    return user


class IUserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    role: str | None = None
    active: bool | None = None


@app.patch("/user/{user_id}")
def update_user(
    user_id: str,
    user_data: IUserUpdate,
    current_user: dict = Depends(verify_token),
):
    update_data = user_data.model_dump(exclude_none=True)

    user = requests.patch(
        pocketbase_url + f"/api/collections/auth_users/records/{user_id}",
        headers={
            "Content-Type": "application/json",
        },
        json=update_data,
        verify=False,
    ).json()

    return user


@app.delete("/user/{user_id}")
def delete_user(
    user_id: str,
    current_user: dict = Depends(verify_token),
):
    response = requests.delete(
        pocketbase_url + f"/api/collections/auth_users/records/{user_id}",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    )

    if response.status_code == 204:
        return {"message": "User deleted successfully"}
    else:
        return {"error": "Failed to delete user"}


# User Auth Endpoints
@app.post("/user/auth")
def auth(user: IUserAuthLogin):
    user_data = requests.post(
        pocketbase_url + "/api/collections/auth_users/auth-with-password",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "identity": user.email,
            "password": user.password,
        },
        verify=False,
    ).json()

    if "token" in user_data and "record" in user_data:
        return {
            "token": user_data["token"],
            "record": {
                "id": user_data["record"]["id"],
                "username": user_data["record"]["username"],
                "email": user_data["record"]["email"],
                "role": user_data["record"].get("role"),
                "created": user_data["record"]["created"],
                "updated": user_data["record"]["updated"],
            },
        }

    return {"error": "Invalid credentials"}


@app.post("/user/register")
def register(user: IUserAuthRegister):
    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=400, detail="Password and confirm password do not match"
        )

    try:
        response = requests.post(
            pocketbase_url + "/api/collections/auth_users/records",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "username": user.username,
                "email": user.email,
                "password": user.password,
                "passwordConfirm": user.confirm_password,
                "emailVisibility": True,
                "role": user.role,
            },
            verify=False,
        )

        if response.status_code == 200:
            user_data = response.json()
            return {"message": "User registered", "user_id": user_data["id"]}
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to register user")


@app.post("/user/logout")
def logout(
    current_user: dict = Depends(verify_token),
):
    # O logout pode ser gerenciado no cliente removendo o token
    # No servidor, podemos apenas retornar sucesso
    return {"message": "Logged out"}


# Powerbi Endpoints
@app.get("/dashboards")
def read_dashboards(
    current_user: dict = Depends(verify_token),
):
    groups = requests.get(
        "https://api.powerbi.com/v1.0/myorg/groups",
        headers={
            "Authorization": f"Bearer {acquire_bearer_token()}",
        },
        verify=False,
    )

    dashboards = []
    if groups.status_code == 200:
        for group in groups.json().get("value", []):
            dashboards_response = requests.get(
                f"https://api.powerbi.com/v1.0/myorg/groups/{group['id']}/reports",
                headers={
                    "Authorization": f"Bearer {acquire_bearer_token()}",
                },
                verify=False,
            )
            if dashboards_response.status_code == 200:
                for report in dashboards_response.json().get("value", []):
                    dashboards.append(
                        {
                            "id": report.get("id"),
                            "name": report.get("name"),
                            "datasetId": report.get("datasetId"),
                            "description": report.get("description"),
                            "groupId": group.get("id"),
                            "groupName": group.get("name"),
                        }
                    )
            else:
                return {"error": "Failed to retrieve dashboards"}

    return {"dashboards": dashboards}


@app.get("/groups")
def read_groups(
    current_user: dict = Depends(verify_token),
):
    """Retorna a lista de grupos do Power BI."""
    groups = requests.get(
        "https://api.powerbi.com/v1.0/myorg/groups",
        headers={
            "Authorization": f"Bearer {acquire_bearer_token()}",
        },
        verify=False,
    )

    if groups.status_code == 200:
        return {"groups": groups.json().get("value", [])}
    else:
        return {"error": "Failed to retrieve groups"}


@app.get("/groups/{group_id}/reports")
def read_reports(
    group_id: str,
    current_user: dict = Depends(verify_token),
):
    """Retorna a lista de relatórios em um grupo específico do Power BI."""
    reports = requests.get(
        f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports",
        headers={
            "Authorization": f"Bearer {acquire_bearer_token()}",
        },
        verify=False,
    )

    if reports.status_code == 200:
        return {"reports": reports.json().get("value", [])}
    else:
        return {"error": "Failed to retrieve reports"}


@app.get("/groups/{group_id}/report/{report_id}")
def read_report(
    group_id: str,
    report_id: str,
    current_user: dict = Depends(
        verify_token,
    ),
):
    """Retorna um relatório específico de um grupo do Power BI."""
    report = requests.get(
        f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}",
        headers={
            "Authorization": f"Bearer {acquire_bearer_token()}",
        },
        verify=False,
    )

    # if report.status_code == 200:
    #     return {"report": report.json()}
    # else:
    #     return {"error": "Failed to retrieve report"}

    return report.json()


@app.delete("/groups/{group_id}/report/{report_id}/dataset/{dataset_id}")
def delete_report(
    group_id: str,
    report_id: str,
    dataset_id: str,
    current_user: dict = Depends(
        verify_token,
    ),
):
    """Deleta um relatório específico de um grupo do Power BI."""
    report = requests.delete(
        f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}",
        headers={
            "Authorization": f"Bearer {acquire_bearer_token()}",
        },
        verify=False,
    )

    dataset = requests.delete(
        f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}",
        headers={
            "Authorization": f"Bearer {acquire_bearer_token()}",
        },
        verify=False,
    )

    if dataset.status_code != 200:
        return {"error": "Failed to delete dataset"}

    if report.status_code == 200:
        return {"message": "Report deleted successfully"}

    else:
        return {"error": "Failed to delete report"}


# Hopper Endpoints
# Groups
@app.get("/app/groups/{group_id}")
def read_hopper_group(
    group_id: str,
    current_user: dict = Depends(verify_token),
):
    group = requests.get(
        pocketbase_url + f"/api/collections/groups/records/{group_id}",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    ).json()

    return group


@app.get("/app/groups")
def read_hopper_groups(current_user: dict = Depends(verify_token)):
    groups = requests.get(
        pocketbase_url + "/api/collections/groups/records",
        verify=False,
    )

    return groups.json()


@app.post("/app/groups")
def create_hopper_group(
    name: str,
    description: str,
    active: bool = True,
    current_user: dict = Depends(verify_token),
):
    group = requests.post(
        pocketbase_url + "/api/collections/groups/records",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "name": name,
            "description": description,
            "active": active,
        },
        verify=False,
    ).json()

    return group


class IGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None


@app.patch("/app/groups/{group_id}")
def update_hopper_group(
    group_id: str,
    group_data: IGroupUpdate,
    current_user: dict = Depends(verify_token),
):
    update_data = group_data.model_dump(exclude_none=True)

    group = requests.patch(
        pocketbase_url + f"/api/collections/groups/records/{group_id}",
        headers={
            "Content-Type": "application/json",
        },
        json=update_data,
        verify=False,
    ).json()

    return group


@app.delete("/app/groups/{group_id}")
def delete_hopper_group(
    group_id: str,
    current_user: dict = Depends(verify_token),
):
    response = requests.delete(
        pocketbase_url + f"/api/collections/groups/records/{group_id}",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    )

    if response.status_code == 204:
        return {"message": "Group deleted successfully"}
    else:
        return {"error": "Failed to delete group"}


## Users in Group
@app.get("/app/groups/{group_id}/users")
def read_hopper_group_users(
    group_id: str,
    current_user: dict = Depends(verify_token),
):
    group_users = requests.get(
        pocketbase_url
        + f"/api/collections/groups_users/records?filter=(group_id='{group_id}')",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    ).json()

    users = []
    for user in group_users["items"]:
        user_record = requests.get(
            pocketbase_url + f"/api/collections/auth_users/records/{user['user_id']}",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        users.append(
            {
                "id": user["id"],
                "user_id": user_record["id"],
                "username": user_record["username"],
                "email": user_record["email"],
                "role": user_record["role"],
                "active": user_record["active"],
                "created": user_record["created"],
                "updated": user_record["updated"],
            }
        )

    return users


@app.get("/app/users/{user_id}/groups")
def read_user_groups(
    user_id: str,
    current_user: dict = Depends(verify_token),
):
    """
    Retorna todos os grupos em que o usuário pertence.
    """
    user_groups = requests.get(
        pocketbase_url
        + f"/api/collections/groups_users/records?filter=(user_id='{user_id}')",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    ).json()

    groups = []
    for user_group in user_groups["items"]:
        group_record = requests.get(
            pocketbase_url
            + f"/api/collections/groups/records/{user_group['group_id']}",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        groups.append(
            {
                "id": group_record["id"],
                "name": group_record["name"],
                "description": group_record.get("description", ""),
                "active": group_record.get("active", True),
                "created": group_record["created"],
                "updated": group_record["updated"],
            }
        )

    return {"groups": groups, "total": len(groups)}


## Dashboards in Group
@app.get("/app/groups/{group_id}/dashboards")
def read_hopper_group_dashboards(
    group_id: str,
    current_user: dict = Depends(verify_token),
):
    group_dashboards = requests.get(
        pocketbase_url
        + f"/api/collections/groups_dashboards/records?filter=(group_id='{group_id}')",
        headers={
            "Content-Type": "application/json",
        },
        verify=False,
    ).json()

    all_dashboards_response = read_dashboards(current_user=current_user)
    all_dashboards_list: list[dict] = all_dashboards_response.get("dashboards", [])  # type: ignore

    dashboards: list[dict] = []
    for group_dashboard in group_dashboards["items"]:
        dashboard_id = group_dashboard.get("dashboard_id")

        for dashboard in all_dashboards_list:
            if dashboard.get("id") == dashboard_id:
                dashboards.append(dashboard)
                break

    return dashboards


## Associate Users/Dashboards to Group
@app.post("/app/groups/{group_id}/users/{user_id}")
def add_user_to_group(
    group_id: str,
    user_id: str,
    current_user: dict = Depends(verify_token),
):
    association = requests.post(
        pocketbase_url + "/api/collections/groups_users/records",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "group_id": group_id,
            "user_id": user_id,
        },
        verify=False,
    ).json()

    return association


@app.delete("/app/groups/{group_id}/users/{user_id}")
def remove_user_from_group(
    user_id: str,
    group_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        group_users = requests.get(
            pocketbase_url
            + f"/api/collections/groups_users/records?filter=(group_id='{group_id}')",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        for group_user in group_users["items"]:
            if group_user["user_id"] == user_id:
                response = requests.delete(
                    pocketbase_url
                    + f"/api/collections/groups_users/records/{group_user['id']}",
                    headers={
                        "Content-Type": "application/json",
                    },
                    verify=False,
                ).json()

                return response

        return group_users

    except Exception as e:
        return {"error": str(e)}


@app.post("/app/groups/{group_id}/dashboards/{dashboard_id}")
def add_dashboard_to_group(
    group_id: str,
    dashboard_id: str,
    current_user: dict = Depends(verify_token),
):
    association = requests.post(
        pocketbase_url + "/api/collections/groups_dashboards/records",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "group_id": group_id,
            "dashboard_id": dashboard_id,
        },
        verify=False,
    ).json()

    return association


@app.delete("/app/groups/{group_id}/dashboards/{dashboard_id}")
def remove_dashboard_from_group(
    group_id: str,
    dashboard_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        group_dashboards = requests.get(
            pocketbase_url
            + f"/api/collections/groups_dashboards/records?filter=(group_id='{group_id}')",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        if "items" not in group_dashboards:
            raise HTTPException(
                status_code=404, detail="No dashboards found for this group"
            )

        for group_dashboard in group_dashboards["items"]:
            if group_dashboard.get("dashboard_id") == dashboard_id:
                response = requests.delete(
                    pocketbase_url
                    + f"/api/collections/groups_dashboards/records/{group_dashboard['id']}",
                    headers={
                        "Content-Type": "application/json",
                    },
                    verify=False,
                )

                if response.status_code == 204:
                    return {"message": "Dashboard removed from group successfully"}
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to remove dashboard",
                    )

        raise HTTPException(status_code=404, detail="Dashboard not found in this group")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


## Associate Pipeline to Dashboard/Group
@app.get("/app/dashboards/pipelines")
def get_all_pipeline_associations(
    current_user: dict = Depends(verify_token),
):
    try:
        response = requests.get(
            pocketbase_url + "/api/collections/pipelines_dashboards/records",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        if "items" not in response:
            raise HTTPException(
                status_code=404, detail="No pipeline associations found"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/app/dashboards/{dashboard_id}/pipeline")
def get_dashboard_pipeline_association(
    dashboard_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        response = requests.get(
            pocketbase_url
            + f"/api/collections/pipelines_dashboards/records?filter=dashboard_id='{dashboard_id}'",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        if "items" not in response:
            raise HTTPException(
                status_code=404, detail="No pipeline found for this dashboard"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/app/dashboards/{pipeline_id}/pipeline")
def get_pipeline_association(
    pipeline_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        response = requests.get(
            pocketbase_url
            + f"/api/collections/pipelines_dashboards/records?filter=pipeline_id='{pipeline_id}'",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        ).json()

        if "items" not in response:
            raise HTTPException(
                status_code=404, detail="No dashboard found for this pipeline"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/app/pipelines/{pipeline_id}/dashboard/{dashboard_id}")
def create_pipeline_association(
    dashboard_id: str,
    pipeline_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        response = requests.post(
            pocketbase_url + "/api/collections/pipelines_dashboards/records",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "dashboard_id": dashboard_id,
                "pipeline_id": pipeline_id,
            },
            verify=False,
        ).json()

        if "error" in response:
            raise HTTPException(status_code=400, detail=f"Error: {response['error']}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.delete("/app/dashboards/{dashboard_id}/pipeline")
def delete_pipeline_association(
    dashboard_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        response = requests.delete(
            pocketbase_url
            + f"/api/collections/pipelines_dashboards/records?filter=dashboard_id='{dashboard_id}'",
            headers={
                "Content-Type": "application/json",
            },
            verify=False,
        )

        if response.status_code == 204:
            return {"message": "Pipeline association removed successfully"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to remove pipeline association",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def acquire_bearer_airflow_token():
    airflow_url = os.getenv("AIRFLOW_URL")
    airflow_username = os.getenv("AIRFLOW_USERNAME")
    airflow_password = os.getenv("AIRFLOW_PASSWORD")

    if not airflow_url or not airflow_username or not airflow_password:
        return {"error": "Failed to retrieve Airflow credentials"}

    token_url = f"{airflow_url}/auth/token"
    payload = {"username": airflow_username, "password": airflow_password}
    response = requests.post(token_url, json=payload, verify=False)

    if response.status_code in [200, 201]:
        try:
            return response.json()
        except Exception:
            return {
                "error": "Failed to parse Airflow token response",
                "details": response.text,
            }
    else:
        return {
            "error": "Failed to acquire Airflow token",
            "status_code": response.status_code,
            "response": response.text,
        }


@app.post("/app/pipeline/{pipeline_id}/refresh")
def refresh_pipeline_association(
    pipeline_id: str,
    current_user: dict = Depends(verify_token),
):
    try:
        airflow_url = os.getenv("AIRFLOW_URL")
        airflow_token_response = acquire_bearer_airflow_token()
        access_token = airflow_token_response.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="Failed to acquire Airflow token",
            )

        endpoint = f"{airflow_url}/api/v2/dags/{pipeline_id}/dagRuns"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        payload = {
            "logical_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            verify=False,
        )
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to refresh pipeline: {response.text}",
            )
        return {"message": "Pipeline refreshed successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error refreshing pipeline")


@app.get("/pipelines")
def get_pipelines(current_user: dict = Depends(verify_token)):
    airflow_url = os.getenv("AIRFLOW_URL")
    endpoint = f"{airflow_url}/api/v2/dags"
    airflow_token_response = acquire_bearer_airflow_token()
    access_token = airflow_token_response.get("access_token")
    if not access_token:
        return {
            "error": "Failed to acquire Airflow token",
            "details": airflow_token_response,
        }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(
        endpoint,
        headers=headers,
        verify=False,
    )
    if response.status_code == 200:
        dags = []

        for dag in response.json().get("dags", []):
            dags.append(
                {
                    "id": dag.get("dag_id"),
                    "description": dag.get("description"),
                    "timetable_description": dag.get("timetable_description"),
                }
            )

        return {"dags": dags}
    else:
        return {
            "error": "Failed to retrieve DAGs",
            "status_code": response.status_code,
            "response": response.text,
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
