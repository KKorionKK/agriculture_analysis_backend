from datetime import datetime, timezone, timedelta
from api.common.enumerations import ChartType, Filter
from api.common.dto import FilterDTO, ChartRawData
from api.services.pg_manager import PGManager
from api.schemas.charts import ChartSchema, ChartValues

from sqlalchemy import text


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
        query = text(
            f"""
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
            """
        )

        async with self.pg.client() as session:
            results = await session.execute(query)
            data = [
                ChartRawData(value=item[1], dt=item[0]).as_humanreadable()
                for item in results.all()
            ]
            values = [item.value for item in data]
            dts = [item.dt for item in data]

            return ChartSchema(
                from_dt=self.from_dt,
                to_dt=self.to_dt,
                data=ChartValues(values=values, dts=dts),
                filter=self.filter,
                chart_type=self.chart_type,
            )
