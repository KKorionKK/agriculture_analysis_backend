from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, ARRAY, JSON, ForeignKey
from api.common import tools
from datetime import datetime
from common.database import Base

from api.schemas.analyze_request import PlantsAnalysisSchema, PlantsArtifactSchema


class PlantsResult(Base):
    __tablename__ = "plants_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    report: Mapped[dict] = mapped_column(JSON, nullable=False)

    artifacts: Mapped[list[dict]] = mapped_column(ARRAY(JSON), nullable=False)
    gis_file: Mapped[str] = mapped_column(String, default=None, nullable=True)
    worker: Mapped[dict] = mapped_column(JSON, default=None, nullable=True)

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
        primaryjoin="PlantsResult.issuer_id == User.id",
    )

    def as_detail_schema(self) -> PlantsAnalysisSchema:
        return PlantsAnalysisSchema(
            id=self.id,
            artifacts=[
                PlantsArtifactSchema(href=item.get("href", ""))
                for item in self.artifacts
            ],
            gis_file=self.gis_file,
            created_at=self.created_at,
        )
