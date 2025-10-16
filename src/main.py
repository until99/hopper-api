from pocketbase import PocketBase
from fastapi import FastAPI
import os
import uvicorn
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI()

http_client = httpx.Client(verify=False)
client = PocketBase(os.getenv("POCKETBASE_URL", ""), http_client=http_client)


class IUserAuthLogin(BaseModel):
    email: str = Field(default=..., examples=["user@example.com"])
    password: str = Field(default=..., examples=["securePassword123"])


class IUserAuthRegister(BaseModel):
    username: str = Field(default=..., examples=["user"])
    email: str = Field(default=..., examples=["user@example.com"])
    password: str = Field(default=..., examples=["securePassword123"])
    confirm_password: str = Field(default=..., examples=["securePassword123"])


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/user/{user_id}")
def read_user(user_id: str):
    user = client.collection("auth_users").get_one(user_id)

    print(user)

    return {
        "id": user.id,
        "username": user.username,  # type: ignore
        "email": user.email,  # type: ignore
        "created": user.created,
        "updated": user.updated,
    }


@app.post("/user/auth")
def auth(user: IUserAuthLogin):
    user_data = client.collection("auth_users").auth_with_password(
        user.email, user.password
    )

    if user_data.is_valid:
        return user_data.token

    return {"error": "Invalid credentials"}


@app.post("/user/register")
def register(user: IUserAuthRegister):
    user_data = client.collection("auth_users").create(
        {
            "username": user.username,
            "email": user.email,
            "password": user.password,  
            "emailVisibility": True,
            "passwordConfirm": user.confirm_password,
        }
    )

    return {"message": "User registered", "user_id": user_data.id}


@app.get("/user/logout")
def logout():
    client.auth_store.clear()
    return {"message": "Logged out"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
