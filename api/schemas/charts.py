from pydantic import BaseModel
import datetime

from api.common.enumerations import ChartType, Filter


class ChartData(BaseModel):
    from_dt: datetime.datetime
    to_dt: datetime.datetime
    dates: list[datetime.datetime]
    data: list[float]
    type: ChartType


class ChartValue(BaseModel):
    value: float
    dt: str


class ChartSchema(BaseModel):
    filter: Filter
    chart_type: ChartType
    from_dt: datetime.datetime
    to_dt: datetime.datetime
    values: list[ChartValue]
