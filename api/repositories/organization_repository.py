from .base import Repository

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, func, and_
from sqlalchemy.orm import selectinload

from api.models import User, Organization, CrOrganizationsUsers
from api.schemas.organizations import OrganizationDetailsSchema


class OrganizationsRepository(Repository):
    async def get_organization_by_id(self, id: str) -> Organization | None:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (await session.execute(select(Organization).where(Organization.id == id)))
                .scalars()
                .first()
            )
            return result

    async def get_users_organizations_and_participants_count(self, user_id: str) -> list[Organization]:
        async with self.client() as session:
            session: AsyncSession
            query = (
                select(Organization)
                .join(CrOrganizationsUsers, Organization.id == CrOrganizationsUsers.organization_id)
                .where(CrOrganizationsUsers.user_id == user_id)
                .options(
                    selectinload(Organization.owner),
                    selectinload(Organization.members).selectinload(CrOrganizationsUsers.user)
                )
            )

            result = await session.execute(query)
            organizations = result.unique().scalars().all()
            return organizations

    async def get_users_roles_in_organization(self, user_id: str, organization_id: str) -> str:
        async with self.client() as session:
            session: AsyncSession
            result = (await session.execute(
                select(CrOrganizationsUsers.role)
                .where(and_(CrOrganizationsUsers.organization_id == organization_id, CrOrganizationsUsers.user_id == user_id))
            )).scalars().first()
            return result

    async def get_organization_details_by_id(self, organization_id: str) -> OrganizationDetailsSchema:
        async with self.client() as session:
            session: AsyncSession

            organization_query = (
                select(Organization)
                .join(CrOrganizationsUsers, Organization.id == CrOrganizationsUsers.organization_id)
                .where(CrOrganizationsUsers.organization_id == organization_id)
                .options(
                    selectinload(Organization.owner),
                    selectinload(Organization.members).selectinload(CrOrganizationsUsers.user)
                )
            )

            result = (await session.execute(organization_query)).scalars().first()

            mean_ndvi = await self.manager.analrequests.get_requests_mean_ndvi_by_organization_fields(organization_id)
            # mean_ndvi = 0
            fields = await self.manager.fields.count_fields_by_organization_id(organization_id)

            return OrganizationDetailsSchema(
                id=result.id,
                name=result.name,
                fields=fields,
                mean_ndvi=mean_ndvi,
                users=[cr.user.as_schema_with_role(cr.role) for cr in result.members] + [result.owner.as_schema_with_role("owner")]
            )


