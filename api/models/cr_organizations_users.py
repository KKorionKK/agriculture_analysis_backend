from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Boolean, Enum, ForeignKey
from api.common import tools
from datetime import datetime

from api.common.enumerations import Roles

from api.services.database import Base


class CrOrganizationsUsers(Base):
    __tablename__ = "cr_organizations_users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(Enum(*Roles._member_names_, name=Roles.__name__), nullable=False)

    user: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # type: ignore  # noqa: F821
        primaryjoin="CrOrganizationsUsers.user_id == User.id",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        remote_side="Organization.id",  # type: ignore  # noqa: F821
        primaryjoin="Organization.id == CrOrganizationsUsers.organization_id",
    )



