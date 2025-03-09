from api.models import Invitation, CrOrganizationsUsers
from .base import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from api.schemas.organizations import OrganizationInviteSchema
from api.common.exceptions import ExceptionCodes, CustomHTTPException

from api.common.enumerations import NotificationType, NotificationSubjectType


class InvitationsRepository(Repository):
    async def create_invitation(
        self, invitation: OrganizationInviteSchema
    ) -> Invitation:
        async with self.client() as session:
            session: AsyncSession
            invitation = Invitation(
                email=invitation.email,
                role=invitation.role,
                msg=invitation.msg,
                is_used=False,
                is_active=True,
            )
            session.add(invitation)
            await session.flush()
            await session.commit()

            await self.client.notifications.create_notification(
                NotificationType.social,
                "Invitation",
                f"Invitation to join organization {invitation.organization.name} was sent to {invitation.email}",
                invitation.issuer_id,
                invitation.id,
                NotificationSubjectType.invite,
            )

            return invitation

    async def deactivate_invitation(self, invitation_id: str) -> Invitation:
        async with self.client() as client:
            client: AsyncSession
            invitation = (
                (
                    await client.execute(
                        update(Invitation)
                        .where(Invitation.id == invitation_id)
                        .values(is_active=False)
                    )
                )
                .scalars()
                .first()
            )
            await client.flush()
            await client.commit()

            return invitation

    async def get_invitation(self, invitation_id: str) -> Invitation:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(Invitation).where(Invitation.id == invitation_id)
                    )
                )
                .scalars()
                .first()
            )
            return result

    async def use_invitation(self, invitation_id: str) -> Invitation:
        async with self.client() as session:
            session: AsyncSession
            # first check if invitation is active and not used
            invitation = (
                (
                    await session.execute(
                        select(Invitation).where(
                            Invitation.id == invitation_id,
                            Invitation.is_active == True,
                            Invitation.is_used == False,
                        )
                    )
                )
                .scalars()
                .first()
            )

            if not invitation:
                raise CustomHTTPException(ExceptionCodes.ObjectNotFound)

            # add new record to organization in CrOrganizationsUsers Table
            cr = CrOrganizationsUsers(
                organization_id=invitation.organization_id,
                user_id=invitation.issuer_id,
                role=invitation.role,
            )
            session.add(cr)

            invitation.is_used = True
            await session.flush()
            await session.commit()

            return invitation
