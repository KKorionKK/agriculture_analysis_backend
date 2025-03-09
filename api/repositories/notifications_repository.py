from typing import List

from .base import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from api.models import Notification
from common.enumerations import NotificationType, NotificationSubjectType


class NotificationsRepository(Repository):
    async def create_notification(
        self,
        type: NotificationType,
        title: str,
        message: str,
        user_id: str,
        subject_id: str,
        subject_type: NotificationSubjectType,
    ) -> Notification:
        async with self.client() as session:
            session: AsyncSession
            notification = Notification(
                type=type,
                title=title,
                message=message,
                user_id=user_id,
                subject_id=subject_id,
                subject_type=subject_type,
            )
            session.add(notification)
            await session.flush()
            await session.commit()
            return notification

    async def get_notifications(self, user_id: str) -> List[Notification]:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(Notification).where(Notification.user_id == user_id)
                    )
                )
                .scalars()
                .all()
            )
            return result

    async def mark_notification_as_read(self, notification_id: str) -> Notification:
        async with self.client() as session:
            session: AsyncSession
            notification = (
                (
                    await session.execute(
                        update(Notification)
                        .where(Notification.id == notification_id)
                        .values(is_read=True)
                    )
                )
                .scalars()
                .first()
            )
            await session.flush()
            await session.commit()

            return notification

    async def mark_all_notifications_as_read(self, user_id: str) -> List[Notification]:
        async with self.client() as session:
            session: AsyncSession
            notifications = (
                (
                    await session.execute(
                        update(Notification)
                        .where(Notification.user_id == user_id)
                        .values(is_read=True)
                    )
                )
                .scalars()
                .all()
            )
            await session.flush()
            await session.commit()

            return notifications
