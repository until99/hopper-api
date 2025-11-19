from pydantic import BaseModel


class IGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None
