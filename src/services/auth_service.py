import requests
from fastapi import HTTPException
from config import settings


class AuthService:
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifica o token de autenticação do usuário no PocketBase."""
        try:
            response = requests.post(
                settings.POCKETBASE_URL + "/api/collections/auth_users/auth-refresh",
                headers={"Authorization": f"Bearer {token}"},
                verify=False,
            )

            if response.status_code == 200:
                return response.json()
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

    @staticmethod
    def login(email: str, password: str) -> dict:
        """Autentica o usuário com email e senha."""
        user_data = requests.post(
            settings.POCKETBASE_URL + "/api/collections/auth_users/auth-with-password",
            headers={"Content-Type": "application/json"},
            json={"identity": email, "password": password},
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

    @staticmethod
    def register(
        username: str, email: str, password: str, confirm_password: str, role: str
    ) -> dict:
        """Registra um novo usuário."""
        if password != confirm_password:
            raise HTTPException(
                status_code=400, detail="Password and confirm password do not match"
            )

        try:
            response = requests.post(
                settings.POCKETBASE_URL + "/api/collections/auth_users/records",
                headers={"Content-Type": "application/json"},
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "passwordConfirm": confirm_password,
                    "emailVisibility": True,
                    "role": role,
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
