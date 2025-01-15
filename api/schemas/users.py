from pydantic import BaseModel
import datetime

from api.common.enumerations import Roles


class UserSchemaWithRole(BaseModel):
    id: str
    email: str
    last_online: datetime.datetime
    role: Roles
