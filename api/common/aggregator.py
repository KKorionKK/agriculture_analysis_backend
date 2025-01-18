from datetime import datetime, timezone, timedelta
from api.common.enumerations import ChartType, Filter
from api.common.dto import FilterDTO, ChartRawData, ChartFormattedData
from api.services.pg_manager import PGManager
from common.models import AnalyzeRequest, NDVIResult
from api.schemas.charts import ChartSchema

from sqlalchemy import func, text, select, and_, Float, literal_column


class GraphAggregatorM:
    def __init__(self, filters: FilterDTO, pg: PGManager):
        self.from_dt = filters.from_dt
        self.to_dt = filters.to_dt
        self.chart_type = filters.chart_type
        self.filter = filters.filter_
        self.pg = pg

        if not self.from_dt:
            self.from_dt = datetime.now(timezone.utc) - timedelta(weeks=4)
            self.to_dt = datetime.now(timezone.utc)
        if not self.filter:
            self.filter = Filter.day.value
        if not self.chart_type:
            self.chart_type = ChartType.ndvi.value

    async def aggregate(self, field_id: str) -> ChartSchema:
        query = text(f"""
                WITH daily_results AS (
                    SELECT 
                        DATE_TRUNC('{self.filter}', ar.created_at) as {self.filter},
                        ar.field_id,
                        nr.reports,
                        ROW_NUMBER() OVER (
                            PARTITION BY DATE_TRUNC('{self.filter}', ar.created_at), ar.field_id 
                            ORDER BY nr.created_at DESC
                        ) as rn
                    FROM analyze_requests ar
                    JOIN ndvi_results nr ON ar.ndvi_result_id = nr.id
                    WHERE 
                        ar.field_id = '{field_id}'
                        AND ar.created_at BETWEEN '{self.from_dt}' AND '{self.to_dt}'
                )
                SELECT 
                    day,
                    AVG((report->>'affected_percentage')::float) as avg_{self.filter}ly_ndvi
                FROM daily_results, unnest(reports) as report
                WHERE rn = 1
                GROUP BY {self.filter}, field_id
                ORDER BY {self.filter}
            """)

        async with self.pg.client() as session:
            results = await session.execute(query)
            data = [ChartRawData(value=item[1], dt=item[0]).as_humanreadable().as_schema() for item in results.all()]

            return ChartSchema(
                from_dt=self.from_dt,
                to_dt=self.to_dt,
                values=data,
                filter=self.filter,
                chart_type=self.chart_type
            )



class GraphAggregator:
    def __init__(self, filters) -> None:
        self.from_dt: datetime | None = filters.from_dt
        self.to_dt: datetime | None = filters.to_dt
        self.group = filters.group
        self.data = {}
        self.step: timedelta = None

        if self.from_dt:
            self.from_dt = self.from_dt.replace(tzinfo=timezone.utc)
            self.to_dt = self.to_dt.replace(tzinfo=timezone.utc)


    def define_step(self):
        match self.group:
            case Group.hour:
                self.step = timedelta(hours=1)
            case Group.week:
                self.step = timedelta(weeks=1)
            case Group.day:
                self.step = timedelta(days=1)
            case Group.month:
                self.step = timedelta(weeks=4)


    def fill_array(self) -> list[datetime]:
        self.define_step()
        if self.from_dt is None:
            if len(list(self.data.keys())) == 0:
                return []
            from_dt = list(self.data.keys())[0]
            to_dt = list(self.data.keys())[-1]
            start_date = from_dt
            array: list[datetime] = []
            while start_date <= to_dt:
                array.append(start_date)
                start_date = start_date + self.step
        else:
            if len(list(self.data.keys())) == 0:
                return []
            start_date = list(self.data.keys())[0]
            array: list[datetime] = []
            while start_date <= self.to_dt:
                array.append(start_date)
                start_date = start_date + self.step
        return array


    def query_selector(self, user_id):
        now = datetime.now(timezone.utc)
        if self.from_dt:
            return f"SELECT date_trunc('{self.group.value}', dt) as {self.group.value}, SUM(user_comission) as sum, SUM(sale_budget) as wastes, SUM(shows) FROM operations WHERE dt >= '{self.from_dt}' AND dt <= '{self.to_dt}' AND user_id = {user_id} AND invoke_at <= '{now}' GROUP BY {self.group.value} ORDER BY {self.group.value} ASC;"
        else:
            return f"SELECT date_trunc('{self.group.value}', dt) as {self.group.value}, SUM(user_comission) as sum, SUM(sale_budget) as wastes, SUM(shows) FROM operations WHERE user_id = {user_id} AND invoke_at <= '{now}' GROUP BY {self.group.value} ORDER BY {self.group.value} ASC;"


    async def get_data(self, user_id: int, pg):
        query = self.query_selector(user_id)
        async with pg.client() as session:
            session: AsyncSession
            raw = list((await session.execute(
                text(query)
            )).fetchall())
            for row in raw:
                self.data[row[0]] = {
                    "income": row[1] / 100,
                    "wastes": row[2] / 100,
                    "shows": row[3]
                }
                # print(f"{row[0]} - Income: {row[1]}, wastes: {row[2]}")


    async def get_aggregation(self, user_id: int, pg) -> dict:
        """
        Data must be ordered by dt field by ascending
        """
        await self.get_data(user_id, pg)
        income: list[float] = []
        wastes: list[float] = []
        shows: list[int] = []
        dates: list[datetime] = self.fill_array()
        for date in dates:
            record = self.data.get(date)
            if record:
                shows.append(record['shows'])
                income.append(record['income'])
                wastes.append(record['wastes'])
            else:
                income.append(0)
                wastes.append(0)
        return {
            "income": income,
            "wastes": wastes,
            "dates": dates,
            "shows": shows
        }