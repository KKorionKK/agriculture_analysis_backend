from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, ARRAY, JSON, ForeignKey, LargeBinary
from api.common import tools
from datetime import datetime
from api.services.database import Base

from common.dto import NDVIResult as DTOResult
from api.schemas.analyze_request import NDVIAnalysisSchema, NDVIReportSchema


class NDVIResult(Base):
    __tablename__ = "ndvi_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    reports: Mapped[list[dict]] = mapped_column(ARRAY(JSON), nullable=False)

    heatmaps: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    gis_file: Mapped[str] = mapped_column(String, default=None, nullable=True)
    worker: Mapped[dict] = mapped_column(JSON, default=None, nullable=True)

    rast: Mapped[bytes] = mapped_column(LargeBinary, nullable=True, default=None)

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
        primaryjoin="NDVIResult.issuer_id == User.id",
    )

    @staticmethod
    def as_db_instances(array: list[DTOResult], request):
        return NDVIResult(
            issuer_id=request.issuer_id,
            reports=[report.as_dict() for report in array],
            heatmaps=[report.problems_map for report in array],
        )

    def as_detail_schema(self) -> NDVIAnalysisSchema:
        return NDVIAnalysisSchema(
            id=self.id,
            gis_file=self.gis_file,
            reports=[
                NDVIReportSchema(
                    affected_percentage=item.get("affected_percentage", 0),
                    plants_percentage=item.get("plants_percentage", 0),
                    ndvi=item.get("ndvi", 0),
                    ndvi_map=item.get("ndvi_map", ""),
                    problems_map=item.get("problems_map", ""),
                    latitude=item.get("latitude", None),
                    longitude=item.get("longitude", None),
                )
                for item in self.reports
            ],
            created_at=self.created_at,
        )
