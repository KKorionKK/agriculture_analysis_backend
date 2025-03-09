from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Enum
from api.common import tools
from datetime import datetime

from api.services.database import Base
from api.common.enumerations import NotificationType, NotificationSubjectType
from api.schemas.notifications import NotificationSchema


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(
        Enum(*NotificationType._member_names_, name=NotificationType.__name__),
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    subject_type: Mapped[str] = mapped_column(
        Enum(
            *NotificationSubjectType._member_names_,
            name=NotificationSubjectType.__name__
        ),
        nullable=False,
    )
    subject_id: Mapped[str] = mapped_column(String, nullable=False)

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # type: ignore  # noqa: F821
        primaryjoin="Notification.user_id == User.id",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )

    def as_schema(self) -> NotificationSchema:
        return NotificationSchema(
            id=self.id,
            title=self.title,
            message=self.message,
            type=self.type,
            is_read=self.is_read,
            subject_type=self.subject_type,
            subject_id=self.subject_id,
            created_at=self.created_at,
        )
