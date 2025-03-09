from pydantic import BaseModel
from .users import UserSchemaWithRole

from api.common.enumerations import Roles


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


class OrganizationCreateSschema(BaseModel):
    name: str
    is_public: bool


class OrganizationInviteSchema(BaseModel):
    email: str
    role: Roles
    message: str
