from .authorization import AuthorizationHandler, AuthorizationStatusHandler
from .upload import UploadHandler
from .fields import FieldHandler, OneFieldHandler, FieldChartHandler
from .analyze_request import AnalyzeRequestHandler, OneAnalyzeRequestHandler
from .organizations import (
    OrganizationsHandler,
    OneOrganizationHandler,
    OrganizationFieldsHandler,
)
from api.common.handler import BaseHandler


def get_routes(data: dict) -> list[str, BaseHandler, dict]:
    auth_data_dict = data.copy()
    auth_data_dict["auth_enabled"] = False
    return [
        (r"/authorization", AuthorizationHandler, auth_data_dict),
        (r"/authorization/status", AuthorizationStatusHandler, data),
        (r"/upload", UploadHandler, data),
        (r"/field", FieldHandler, data),
        (r"/field/([^/]+)", OneFieldHandler, data),
        (r"/field/([^/]+)/chart", FieldChartHandler, data),
        (r"/analyze", AnalyzeRequestHandler, data),
        (r"/analyze/([^/]+)", OneAnalyzeRequestHandler, data),
        (r"/organization", OrganizationsHandler, data),
        (r"/organization/([^/]+)", OneOrganizationHandler, data),
        (r"/organization/([^/]+)/field", OrganizationFieldsHandler, data),
    ]


__all__ = [
    "AuthorizationHandler",
    "UploadHandler",
    "AnalyzeRequestHandler",
    "OrganizationsHandler",
    "get_routes",
]
