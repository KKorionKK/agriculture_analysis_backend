from datetime import datetime, timezone, timedelta
from api.common.enumerations import ChartType, Filter
from api.common.dto import FilterDTO, ChartRawData
from api.services.pg_manager import PGManager
from api.schemas.charts import ChartSchema, ChartValues

from api.common.exceptions import ExceptionCodes, CustomHTTPException

from sqlalchemy import text


class GraphAggregatorM:

    def __init__(self, filters: dict, pg: PGManager):
        filters = self.__get_filters(filters)
        self.from_dt = filters.from_dt
        self.to_dt = filters.to_dt
        self.chart_type = filters.chart_type.value
        self.filter = filters.filter_.value
        self.pg = pg

        if not self.from_dt:
            self.from_dt = datetime.now(timezone.utc) - timedelta(weeks=4)
            self.to_dt = datetime.now(timezone.utc)
        if not self.filter:
            self.filter = Filter.day.value
        if not self.chart_type:
            self.chart_type = ChartType.ndvi.value

    def __get_filters(self, data: dict, raise_exc: bool = True) -> FilterDTO:
        filter_ = data.get("filter", [None])[0]
        chart_type = data.get("chart_type", [None])[0]
        from_dt = None
        to_dt = None

        try:
            filter_ = Filter(filter_)
        except ValueError:
            if raise_exc:
                raise CustomHTTPException(ExceptionCodes.FilterUnexpected, data=filter_)

        try:
            chart_type = ChartType(chart_type)
        except ValueError:
            if raise_exc:
                raise CustomHTTPException(
                    ExceptionCodes.ChartTypeUnexpected,
                    data=f"Entered: {chart_type}. "
                    f"Expected one of: {ChartType.as_list()}",
                )

        try:
            from_dt = datetime.fromtimestamp(float(data.get("from")))
            to_dt = datetime.fromtimestamp(float(data.get("to")))
        except Exception as e:
            print(e)
            pass

        return FilterDTO(chart_type, filter_, from_dt, to_dt)

    def __get_report_field_name_by_chart_type(self) -> str:
        if self.chart_type == ChartType.ndvi:
            return "mean_ndvi"
        elif self.chart_type == ChartType.disease:
            return "affected_percentage"
        else:
            return "plants_percentage"

    async def aggregate(self, field_id: str) -> ChartSchema:
        _report_field_name = self.__get_report_field_name_by_chart_type()
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
                    AVG((report->>'{_report_field_name}')::float) as avg_{self.filter}ly_ndvi
                FROM daily_results, unnest(reports) as report
                WHERE rn = 1
                GROUP BY {self.filter}, field_id
                ORDER BY {self.filter}
            """
        )

        async with self.pg.client() as session:
            results = await session.execute(query)
            res = results.all()
            data = [
                ChartRawData(value=item[1], dt=item[0]).as_humanreadable()
                for item in res
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
