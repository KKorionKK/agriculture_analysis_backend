from common.models.user import User
from common.models.field import Field
from common.models.analyze_request import AnalyzeRequest
from common.models.plants_result import PlantsResult
from common.models.ndvi_result import NDVIResult
from common.models.organization import Organization
from common.models.cr_organizations_users import CrOrganizationsUsers
from common.models.invitation import Invitation
from common.models.notifications import Notification

__all__ = [
    "User",
    "Field",
    "AnalyzeRequest",
    "PlantsResult",
    "NDVIResult",
    "Organization",
    "CrOrganizationsUsers",
    "Invitation",
    "Notification",
]

"""
The directory with shared models is displayed separately, but nevertheless, 
here you can define aliases and other auxiliary database representations.
"""
