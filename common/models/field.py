from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (
    String,
    DateTime,
    Integer,
    ARRAY,
    JSON,
    ForeignKey,
)
from api.common import tools
from datetime import datetime
from common.database import Base

from api.schemas.fields import FieldSchema


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False, default="#FFFFF")
    coordinates: Mapped[list[dict]] = mapped_column(
        ARRAY(JSON), nullable=False, default=None
    )
    area: Mapped[int] = mapped_column(Integer, nullable=False)

    last_analysed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=tools.get_dt
    )

    organization_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        default=None,
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        remote_side="Organization.id",  # type: ignore  # noqa: F821
        primaryjoin="Field.organization_id == Organization.id",
    )

    owner_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # type: ignore  # noqa: F821
        primaryjoin="Field.owner_id == User.id",
    )

    def as_schema(self):
        return FieldSchema(
            id=self.id,
            color=self.color,
            coordinates=self.coordinates,
            area=self.area,
            name=self.name,
            last_analyzed=self.last_analysed,
            created_at=self.created_at,
        )
