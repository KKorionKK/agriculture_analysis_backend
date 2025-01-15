from api.common.handler import BaseHandler
from api.schemas.fields import FieldCreateSchema

from api.common.exceptions import ExceptionCodes, CustomHTTPException


class FieldHandler(BaseHandler):
    async def get(self):
        # fields = await self.pg.fields.get_fields_by_user(self.current_user.id)
        # fields = [field.as_schema() for field in fields]
        fields = await self.pg.fields.get_extended_fields_data_by_user_with_avg_values(self.current_user.id)
        self.write({"fields": fields})

    async def post(self):
        data = self.get_body()
        print(data)
        schema = FieldCreateSchema(**data)

        field = await self.pg.fields.create_field(schema, self.current_user)

        fields = await self.pg.fields.get_extended_fields_data_by_user(self.current_user.id)

        self.write({"fields": fields})


class OneFieldHandler(BaseHandler):
    async def get(self, field_id):
        fields = await self.pg.fields.get_field_details(field_id, self.current_user.id)
        self.write({"fields": fields})

    async def delete(self, field_id):
        await self.pg.fields.delete_field_by_id(field_id, self.current_user.id)
        self.write({"message": "OK"})

