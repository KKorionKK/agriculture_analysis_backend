from pydantic import BaseModel
from .users import UserSchemaWithRole


class UsersOrganizationItem(BaseModel):
    id: str
    name: str
    users: list[UserSchemaWithRole]


class RestrictionsSchema(BaseModel):
    edit: bool
    delete: bool


class OrganizationDetailsSchema(BaseModel):
    id: str
    name: str
    fields: int
    mean_ndvi: float

    users: list[UserSchemaWithRole]
    restrictions: RestrictionsSchema | None = None
