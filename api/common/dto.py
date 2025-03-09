from dataclasses import dataclass
from datetime import datetime
from api.common.enumerations import ChartType, Filter


MONTHS = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
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


@dataclass
class ChartRawData:
    value: float
    dt: datetime

    def as_humanreadable(self) -> ChartFormattedData:
        month = MONTHS[self.dt.month]
        day = self.dt.day

        dt = f"{day} {month}"
        value = 0
        if self.value:
            value = self.value

        return ChartFormattedData(value=round(value, 2), dt=dt)
