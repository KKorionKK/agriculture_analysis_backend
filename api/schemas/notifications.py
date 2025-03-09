from pydantic import BaseModel
from api.common.enumerations import NotificationType, NotificationSubjectType


class NotificationSchema(BaseModel):
    id: str
    title: str
    message: str
    type: NotificationType
    is_read: bool
    subject_type: NotificationSubjectType
    subject_id: str
    created_at: str
