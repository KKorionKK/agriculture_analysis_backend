from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric
from worker.utils import tools
from datetime import datetime
from worker.utils.database import Base

from api.schemas.fields import FieldSchema


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    area: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    last_analysed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=tools.get_dt
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
            latitude=self.latitude,
            longitude=self.longitude,
            area=self.area,
            name=self.name,
            last_analyzed=self.last_analysed,
            created_at=self.created_at,
        )
