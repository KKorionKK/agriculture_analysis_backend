from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Enum
from api.common import tools
from datetime import datetime

from api.services.database import Base
from api.common.enumerations import Roles


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    email: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[str] = mapped_column(
        Enum(*Roles._member_names_, name=Roles.__name__), nullable=False
    )
    msg: Mapped[str] = mapped_column(String)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    deactivated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    issuer_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    issuer: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # type: ignore  # noqa: F821
        primaryjoin="Invitation.issuer_id == User.id",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        remote_side="Organization.id",  # type: ignore  # noqa: F821
        primaryjoin="Invitation.organization_id == Organization.id",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )
