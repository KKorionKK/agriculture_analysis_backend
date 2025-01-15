from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Integer, ARRAY, Enum, JSON, ForeignKey, Boolean
from common import tools
from datetime import datetime
from api.services.database import Base

from api.common import DataStatus
from api.schemas.analyze_request import AnalyzeRequestSchema


class AnalyzeRequest(Base):
    __tablename__ = "analyze_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    origin_ndvi_data: Mapped[str] = mapped_column(String, default=None, nullable=True)
    origin_plants_data: Mapped[str] = mapped_column(String, default=None, nullable=True)

    ndvi_status: Mapped[DataStatus] = mapped_column(
        Enum(*DataStatus._member_names_, name=DataStatus.__name__), nullable=False
    )  # noqa
    plants_status: Mapped[DataStatus] = mapped_column(
        Enum(*DataStatus._member_names_, name=DataStatus.__name__), nullable=False
    )  # noqa

    fail_info: Mapped[dict] = mapped_column(JSON, default=None, nullable=True)

    ndvi_result_id: Mapped[str] = mapped_column(
        String, ForeignKey("ndvi_results.id"), nullable=True
    )
    plants_result_id: Mapped[str] = mapped_column(
        String, ForeignKey("plants_results.id"), nullable=True
    )
    field_id: Mapped[str] = mapped_column(
        String, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )

    field: Mapped["Field"] = relationship(
        "Field",
        remote_side="Field.id",  # type: ignore  # noqa: F821
        primaryjoin="AnalyzeRequest.field_id == Field.id",
    )

    plants_result: Mapped["PlantsResult"] = relationship(
        "PlantsResult",
        remote_side="PlantsResult.id",  # type: ignore  # noqa: F821
        primaryjoin="AnalyzeRequest.plants_result_id == PlantsResult.id",
    )
    ndvi_result: Mapped["NDVIResult"] = relationship(
        "NDVIResult",
        remote_side="NDVIResult.id",  # type: ignore  # noqa: F821
        primaryjoin="AnalyzeRequest.ndvi_result_id == NDVIResult.id",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=tools.get_dt
    )

    issuer_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    issuer: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # type: ignore  # noqa: F821
        primaryjoin="AnalyzeRequest.issuer_id == User.id",
    )

    def as_schema(self):
        return AnalyzeRequestSchema(
            id=self.id,
            ndvi_status=self.ndvi_status,
            plants_status=self.plants_status,
            fail_info=self.fail_info,
            created_at=self.created_at,
        )
