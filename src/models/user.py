from pydantic import BaseModel, Field


class IUserAuthLogin(BaseModel):
    email: str = Field(default=..., examples=["user@example.com"])
    password: str = Field(default=..., examples=["securePassword123"])


class IUserAuthRegister(BaseModel):
    username: str = Field(default=..., examples=["user"])
    email: str = Field(default=..., examples=["user@example.com"])
    password: str = Field(default=..., examples=["securePassword123"])
    confirm_password: str = Field(default=..., examples=["securePassword123"])
    role: str = Field(default="user", examples=["user", "admin"])


class IUserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    role: str | None = None
    active: bool | None = None
