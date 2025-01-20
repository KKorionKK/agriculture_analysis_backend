import json
from typing import Optional, Awaitable, Union, Any
from datetime import datetime
from api.services.emitter import Emitter
from pydantic import BaseModel
from api.models import User

from api.services.pg_manager import PGManager
from .vigilante import Vigilante
from api.services.authorization import AuthorizationService

from .exceptions.exception_handler import ErrorHandler
from api.common.enumerations import Roles
from tornado.escape import utf8

from api.common.exceptions import CustomHTTPException, ExceptionCodes


class PydanticJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return str(obj)
        return super().default(obj)


class BaseHandler(ErrorHandler):
    unicode_type = str

    def initialize(
        self,
        pg: PGManager,
        vigilante: Vigilante,
        authorization_service: AuthorizationService,
        emitter: Emitter,
        auth_enabled: bool = True,
    ):
        self.pg = pg  # noqa
        self.vigilante = vigilante  # noqa
        self.auth_enabled = auth_enabled  # noqa
        self.auth_service = authorization_service  # noqa
        self.emitter = emitter  # noqa
        self.logger = vigilante.get_logger()
        self.current_user: User = None

    async def check_roles(
        self, role: Roles, organization_id: str, silent: bool = False
    ) -> bool | None:
        actual_role = await self.auth_service.get_user_role(
            organization_id, self.current_user.id
        )
        if actual_role is Roles.read_only:
            if role is Roles.admin or role is Roles.write or role is Roles.owner:
                if silent:
                    return False
                raise CustomHTTPException(
                    ExceptionCodes.NotEnoughPermissions, data=role.value
                )
        elif actual_role is Roles.write:
            if role is Roles.admin or role is Roles.owner:
                if silent:
                    return False
                raise CustomHTTPException(
                    ExceptionCodes.NotEnoughPermissions, data=role.value
                )
        elif actual_role is Roles.admin:
            if role is Roles.owner:
                if silent:
                    return False
                raise CustomHTTPException(
                    ExceptionCodes.NotEnoughPermissions, data=role.value
                )
        if silent:
            return True
        else:
            return None

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE"
        )
        self.set_header(
            "Access-Control-Allow-Headers",
            "access-control-allow-origin,authorization,content-type,x-requested-with",
        )

    def options(self, query=None):
        # Обработка preflight запросов
        self.set_status(204)
        self.finish()

    def get_body(self):
        try:
            body = json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            print(e)
            raise CustomHTTPException(ExceptionCodes.EncoderError)
        return body

    async def prepare(self) -> Optional[Awaitable[None]]:
        if self.request.method == "OPTIONS":
            return
        if self.auth_enabled:
            token = self.request.headers.get("Authorization", None)
            if not token:
                raise CustomHTTPException(ExceptionCodes.TokenNotFound)

            user = await self.auth_service.get_current_user(token)
            if not user:
                raise CustomHTTPException(ExceptionCodes.AccountNotFound)

            self.current_user = user

    def write(self, chunk: Union[str, bytes, dict, BaseModel]) -> None:
        """Writes the given chunk to the output buffer.

        To write the output to the network, use the `flush()` method below.

        If the given chunk is a dictionary, we write it as JSON and set
        the Content-Type of the response to be ``application/json``.
        (if you want to send JSON as a different ``Content-Type``, call
        ``set_header`` *after* calling ``write()``).

        Note that lists are not converted to JSON because of a potential
        cross-site security vulnerability.  All JSON output should be
        wrapped in a dictionary.  More details at
        http://haacked.com/archive/2009/06/25/json-hijacking.aspx/ and
        https://github.com/facebook/tornado/issues/1009
        """
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if not isinstance(chunk, (bytes, self.unicode_type, dict, BaseModel)):
            message = (
                "write() only accepts bytes, unicode, PydanticModel and dict objects"
            )
            if isinstance(chunk, list):
                message += (
                    ". Lists not accepted for security reasons; see "
                    + "http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write"  # noqa: E501
                )
            raise TypeError(message)
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk, cls=PydanticJSONEncoder).replace("</", "<\\/")
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        if isinstance(chunk, BaseModel):
            chunk = chunk.model_dump()
            chunk = json.dumps(chunk, cls=PydanticJSONEncoder).replace("</", "<\\/")
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)
