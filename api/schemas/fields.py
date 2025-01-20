from pydantic import BaseModel
from datetime import datetime

from api.common.enumerations import DataStatus

from api.schemas.charts import ChartSchema


class Coordinate(BaseModel):
    latitude: float
    longitude: float


class FieldCreateSchema(BaseModel):
    area: str
    name: str
    color: str
    coordinates: list[Coordinate]


class FieldSchema(FieldCreateSchema):
    id: str
    last_analyzed: datetime | None
    created_at: datetime


class FieldExtendedSchema(BaseModel):
    id: str
    name: str
    color: str | None = None
    coordinates: list[Coordinate] | None = None
    analysis_dt: datetime | None = None
    health_status: str | None
    data_status: str | None


class FieldExtendedWithMeanValuesSchema(BaseModel):
    id: str
    name: str
    color: str | None = None
    coordinates: list[Coordinate] | None = None
    mean_ndvi: float
    mean_health: float
    mean_disease: float
    area: float


class NDVIReport(BaseModel):
    affected_percentage: float
    plants_percentage: float
    ndvi: float | None
    ndvi_map: str
    problems_map: str

    latitude: float | None
    longitude: float | None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            affected_percentage=data.get("affected_percentage", None),
            plants_percentage=data.get("plants_percentage", None),
            ndvi=data.get("ndvi", None),
            ndvi_map=data.get("ndvi_map", None),
            problems_map=data.get("problems_map", None),
            latitude=data.get("latitude", None),
            longitude=data.get("longitude", None),
        )


class NDVIAnalysisSchema(BaseModel):
    id: str
    gis_file: str | None
    reports: list[NDVIReport]


class PlantsAnalysisSchema(BaseModel):
    id: str
    gis_file: str | None
    reports: dict  # TODO: определиться


class AnalysisRequest(BaseModel):
    request_id: str
    requested_dt: datetime
    ndvi_analyze_status: DataStatus
    plants_analyze_status: DataStatus

    fail_info: str | dict | None
    disease_focus: tuple | None

    ndvi: NDVIAnalysisSchema | None
    plant: PlantsAnalysisSchema | None


class FieldDetailSchema(BaseModel):
    id: str
    name: str
    area: str
    last_analyzed: datetime | None

    avg_ndvi: float
    avg_vegetation: float
    avg_decease: float

    analrequests: list[AnalysisRequest]
    chart: ChartSchema | None = None
