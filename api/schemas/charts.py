from pydantic import BaseModel
import datetime

from api.common.enumerations import ChartType


class ChartData(BaseModel):
    from_dt: datetime.datetime
    to_dt: datetime.datetime
    dates: list[datetime.datetime]
    data: list[float]
    type: ChartType

