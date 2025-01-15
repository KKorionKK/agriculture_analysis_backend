from api.common.handler import BaseHandler
from api.schemas.authorization import AuthorizationType, AuthenticationData


class AuthorizationHandler(BaseHandler):
    async def post(self):
        data = self.get_body()
        schema = AuthenticationData(**data)
        if schema.type == AuthorizationType.login:
            token = await self.auth_service.login_user(schema.data)
        else:
            token = await self.auth_service.register_user(schema.data)
        print(token)
        self.write(token)
