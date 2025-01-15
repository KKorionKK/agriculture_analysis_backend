from dataclasses import dataclass
from datetime import datetime
from api.common.enumerations import ChartType, Filter


@dataclass
class FilterDTO:
    chart_type: ChartType | None = None
    filter_: Filter | None = None
    from_dt: datetime | None = None
    to_dt: datetime | None = None