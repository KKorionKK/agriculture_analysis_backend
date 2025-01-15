from api.common.handler import BaseHandler
from api.schemas.analyze_request import AnalyzeRequestCreate

from api.common.exceptions import ExceptionCodes, CustomHTTPException


class AnalyzeRequestHandler(BaseHandler):
    async def get(self):
        requests = await self.pg.analrequests.get_requests_by_user(self.current_user.id)
        self.write({"requests": [request.as_schema() for request in requests]})

    async def post(self):
        data = self.get_body()
        schema = AnalyzeRequestCreate(**data)
        if schema.origin_ndvi_data is None and schema.origin_plants_data is None:
            raise CustomHTTPException(ExceptionCodes.NeedData)

        request = await self.pg.analrequests.create_request(schema, self.current_user)

        await self.emitter.send_task(request.id)

        self.write(request.as_schema())
