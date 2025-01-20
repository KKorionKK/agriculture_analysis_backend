from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime
from api.common import tools
from datetime import datetime

from api.services.database import Base
from api.schemas.users import UserSchemaWithRole
from api.common.enumerations import Roles


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, default="client")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )
    last_online: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )

    def as_schema_with_role(self, role: str):
        return UserSchemaWithRole(
            id=self.id, email=self.email, last_online=self.last_online, role=Roles(role)
        )
