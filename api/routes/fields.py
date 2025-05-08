from api.common.handler import BaseHandler
from api.schemas.fields import FieldCreateSchema

from api.common.aggregator import GraphAggregatorM


class FieldHandler(BaseHandler):
    async def get(self):
        # fields = await self.pg.fields.get_fields_by_user(self.current_user.id)
        # fields = [field.as_schema() for field in fields]
        fields = await self.pg.fields.get_extended_fields_data_by_user_with_avg_values(
            self.current_user.id
        )
        self.write({"fields": fields})

    async def post(self):
        data = self.get_body()
        schema = FieldCreateSchema(**data)

        field = await self.pg.fields.create_field(schema, self.current_user)

        fields = await self.pg.fields.get_extended_fields_data_by_user(
            self.current_user.id
        )

        self.write({"fields": fields})


class OneFieldHandler(BaseHandler):
    async def get(self, field_id):
        query_params = {
            key: self.get_query_arguments(key) for key in self.request.query_arguments
        }
        graphs = GraphAggregatorM(query_params, self.pg)
        chart = await graphs.aggregate(field_id)
        field = await self.pg.fields.get_field_details(field_id, self.current_user.id)
        field.chart = chart
        self.write({"fields": field})

    async def delete(self, field_id):
        await self.pg.fields.delete_field_by_id(field_id, self.current_user.id)
        self.write({"message": "OK"})


class FieldChartHandler(BaseHandler):
    async def get(self, field_id):
        query_params = {
            key: self.get_query_arguments(key) for key in self.request.query_arguments
        }
        graphs = GraphAggregatorM(query_params, self.pg)
        chart = await graphs.aggregate(field_id)
        self.write({"chart": chart})


class FieldGeoJsonHandler(BaseHandler):
    async def get(self, field_id):
        results = session.query(NDVIResult).filter_by(issuer_id=user_id).all()

        features = []
        for result in results:
            if result.gis_file:  # Проверяем, есть ли файл с результатами
                features.append(
                    {
                        "type": "Feature",
                        "geometry": json.loads(
                            result.gis_file
                        ),  # Данные хранятся в формате GeoJSON
                        "properties": {
                            "id": result.id,
                            "created_at": result.created_at.isoformat(),
                            "ndvi_map": result.heatmaps,  # Можешь добавить другие свойства
                        },
                    }
                )

        geojson_data = {"type": "FeatureCollection", "features": features}

        resp.media = geojson_data
        resp.status = 200
