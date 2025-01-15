from pydantic import BaseModel
from datetime import datetime

from api.common.enumerations import DataStatus


class AnalyzeRequestCreate(BaseModel):
    origin_ndvi_data: str | None
    origin_plants_data: str | None
    field_id: str


class AnalyzeRequestSchema(BaseModel):
    id: str
    ndvi_status: DataStatus
    plants_status: DataStatus
    fail_info: dict | None
    created_at: datetime
