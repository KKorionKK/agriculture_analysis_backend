from pydantic import BaseModel
from datetime import datetime

from api.common.enumerations import DataStatus


class AnalyzeRequestCreate(BaseModel):
    title: str
    origin_ndvi_data: str | None = None
    origin_plants_data: str | None = None
    field_id: str


class AnalyzeRequestUpdate(BaseModel):
    title: str
    origin_ndvi_data: str | None = None
    origin_plants_data: str | None = None
    analyze_id: str


class AnalyzeRequestSchema(BaseModel):
    id: str
    title: str
    ndvi_status: DataStatus
    plants_status: DataStatus
    fail_info: dict | None
    created_at: datetime


class NDVIReportSchema(BaseModel):
    affected_percentage: float
    plants_percentage: float
    ndvi: float | None = None
    ndvi_map: str
    problems_map: str

    latitude: float | None = None
    longitude: float | None = None


class NDVIAnalysisSchema(BaseModel):
    id: str
    gis_file: str | None = None
    reports: list[NDVIReportSchema]
    created_at: datetime


class PlantsArtifactSchema(BaseModel):
    href: str = (
        "https://s3.timeweb.cloud/058ec85b-a033d29f-40af-47a8-b537-af7433b01be1/0000_rgb_problems_overlay.png"
    )


class PlantsAnalysisSchema(BaseModel):
    id: str
    artifacts: list[PlantsArtifactSchema]
    gis_file: str | None = None
    created_at: datetime


class AnalyzeRequestDetailSchema(BaseModel):
    request_id: str
    title: str
    requested_dt: datetime
    ndvi_analyze_status: DataStatus
    plants_analyze_status: DataStatus
    field_id: str

    origin_ndvi_data: str | None = None
    origin_plants_data: str | None = None

    fail_info: str | dict | None = None

    ndvi: NDVIAnalysisSchema | None = None
    plant: PlantsAnalysisSchema | None = None
