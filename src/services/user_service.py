import requests
from src.config import settings


class UserService:
    @staticmethod
    def get_user(user_id: str) -> dict:
        """Retorna os dados de um usuário específico."""
        user = requests.get(
            settings.POCKETBASE_URL + f"/api/collections/auth_users/records/{user_id}",
            headers={"Content-Type": "application/json"},
            verify=False,
        ).json()
        return user

    @staticmethod
    def get_users(page: int = 1, per_page: int = 30) -> dict:
        """Retorna lista paginada de usuários."""
        users = requests.get(
            settings.POCKETBASE_URL
            + f"/api/collections/auth_users/records?page={page}&perPage={per_page}",
            headers={"Content-Type": "application/json"},
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

    @staticmethod
    def create_user(
        username: str, email: str, password: str, password_confirm: str, role: str
    ) -> dict:
        """Cria um novo usuário."""
        if password != password_confirm:
            return {"error": "Password and password confirmation do not match"}

        user = requests.post(
            settings.POCKETBASE_URL + "/api/collections/auth_users/records",
            headers={"Content-Type": "application/json"},
            json={
                "username": username,
                "email": email,
                "password": password,
                "passwordConfirm": password_confirm,
                "role": role,
                "emailVisibility": True,
                "verify": True,
            },
            verify=False,
        ).json()

        return user

    @staticmethod
    def update_user(user_id: str, update_data: dict) -> dict:
        """Atualiza os dados de um usuário."""
        user = requests.patch(
            settings.POCKETBASE_URL + f"/api/collections/auth_users/records/{user_id}",
            headers={"Content-Type": "application/json"},
            json=update_data,
            verify=False,
        ).json()

        return user

    @staticmethod
    def delete_user(user_id: str) -> dict:
        """Deleta um usuário."""
        response = requests.delete(
            settings.POCKETBASE_URL + f"/api/collections/auth_users/records/{user_id}",
            headers={"Content-Type": "application/json"},
            verify=False,
        )

        if response.status_code == 204:
            return {"message": "User deleted successfully"}
        else:
            return {"error": "Failed to delete user"}

    @staticmethod
    def get_user_groups(user_id: str) -> dict:
        """Retorna todos os grupos em que o usuário pertence."""
        user_groups = requests.get(
            settings.POCKETBASE_URL
            + f"/api/collections/groups_users/records?filter=(user_id='{user_id}')",
            headers={"Content-Type": "application/json"},
            verify=False,
        ).json()

        groups = []
        for user_group in user_groups["items"]:
            group_record = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/groups/records/{user_group['group_id']}",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "id" not in group_record:
                continue

            groups.append(
                {
                    "id": group_record["id"],
                    "name": group_record.get("name", ""),
                    "description": group_record.get("description", ""),
                    "active": group_record.get("active", True),
                    "created": group_record.get("created", ""),
                    "updated": group_record.get("updated", ""),
                }
            )

        return {"groups": groups, "total": len(groups)}
