from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from api.common import tools
from datetime import datetime

from common.database import Base

from api.schemas.organizations import UsersOrganizationItem


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    name: Mapped[str] = mapped_column(String, unique=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False)

    owner_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # type: ignore  # noqa: F821
        primaryjoin="Organization.owner_id == User.id",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )

    members: Mapped[list["CrOrganizationsUsers"]] = relationship(
        "CrOrganizationsUsers",
        primaryjoin="Organization.id == CrOrganizationsUsers.organization_id",
        lazy="selectin",
    )

    def as_items_schema(self) -> UsersOrganizationItem:
        return UsersOrganizationItem(
            id=self.id,
            name=self.name,
            users=[cr.user.as_schema_with_role(cr.role) for cr in self.members]
            + [self.owner.as_schema_with_role("owner")],
        )
