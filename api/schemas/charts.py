from pydantic import BaseModel
import datetime

from api.common.enumerations import ChartType, Filter


class ChartData(BaseModel):
    from_dt: datetime.datetime
    to_dt: datetime.datetime
    dates: list[datetime.datetime]
    data: list[float]
    type: ChartType


class ChartValues(BaseModel):
    values: list[float]
    dts: list[str]


class ChartSchema(BaseModel):
    filter: Filter
    chart_type: ChartType
    from_dt: datetime.datetime
    to_dt: datetime.datetime
    data: ChartValues
