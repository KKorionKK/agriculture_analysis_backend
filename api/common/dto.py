from dataclasses import dataclass
from datetime import datetime
from api.common.enumerations import ChartType, Filter

from api.schemas.charts import ChartValue

MONTHS = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
]


@dataclass
class FilterDTO:
    chart_type: ChartType | None = None
    filter_: Filter | None = None
    from_dt: datetime | None = None
    to_dt: datetime | None = None


@dataclass
class ChartFormattedData:
    value: float
    dt: str

    def as_schema(self) -> ChartValue:
        return ChartValue(
            value=self.value,
            dt=self.dt
        )


@dataclass
class ChartRawData:
    value: float
    dt: datetime

    def as_humanreadable(self) -> ChartFormattedData:
        month = MONTHS[self.dt.month]
        day = self.dt.day

        dt = f"{day} {month}"

        return ChartFormattedData(value=round(self.value, 2), dt=dt)
