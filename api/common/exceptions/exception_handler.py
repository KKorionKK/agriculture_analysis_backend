import tornado.web
from .exceptions import CustomHTTPException, ExceptionCodes
import traceback

from pydantic import ValidationError


class ErrorHandler(tornado.web.RequestHandler):
    logger = None

    def write_error(self, status_code, **kwargs):
        self.set_status(200)

        err = kwargs.get("exc_info")
        if isinstance(err[1], CustomHTTPException):
            self.write(err[1].as_dict())
        elif isinstance(err[1], ValidationError):
            errs = err[1].errors(
                include_url=True, include_input=True, include_context=True
            )
            self.write(
                CustomHTTPException(ExceptionCodes.ValidationError, data=errs).as_dict()
            )
        else:
            self.write(CustomHTTPException(ExceptionCodes.UnexpectedError).as_dict())
        self.logger.error(f"Got error: {traceback.format_exc()}")
