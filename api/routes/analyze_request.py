from api.common.handler import BaseHandler
from api.schemas.analyze_request import AnalyzeRequestCreate, AnalyzeRequestUpdate

from api.common.exceptions import ExceptionCodes, CustomHTTPException


class OneAnalyzeRequestHandler(BaseHandler):

    async def get(self, request_id):
        request = await self.pg.analrequests.get_request_info_by_id(request_id)
        self.write({"request": request})


class AnalyzeRequestHandler(BaseHandler):
    async def get(self):
        requests = await self.pg.analrequests.get_requests_by_user(self.current_user.id)
        self.write({"requests": [request.as_schema() for request in requests]})

    async def post(self):
        data = self.get_body()
        schema = AnalyzeRequestCreate(**data)
        # if schema.origin_ndvi_data is None and schema.origin_plants_data is None:
        #     raise CustomHTTPException(ExceptionCodes.NeedData)

        request = await self.pg.analrequests.create_request(schema, self.current_user)
        # if request.origin_plants_data or request.origin_ndvi_data:
        #     await self.emitter.send_task(request.id)

        self.write(request.as_schema())

    async def put(self):
        data = self.get_body()
        schema = AnalyzeRequestUpdate(**data)
        request = await self.pg.analrequests.update_request(schema, self.current_user)
        if not request:
            raise CustomHTTPException(ExceptionCodes.ObjectNotFound)

        # if request.origin_plants_data or request.origin_ndvi_data:
        #     await self.emitter.send_task(request.id)
        print(f"updated analyze request with: {data}")
        self.write(request.as_schema())
