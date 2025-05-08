from .base import Repository

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, or_
from sqlalchemy.orm import selectinload

from api.models import Organization, CrOrganizationsUsers, Field, User
from api.schemas.organizations import (
    OrganizationDetailsSchema,
    OrganizationCreateSschema,
)
from api.schemas.fields import FieldExtendedWithMeanValuesSchema

from api.common.exceptions import ExceptionCodes, CustomHTTPException


class OrganizationsRepository(Repository):
    async def get_organization_by_id(self, id: str) -> Organization | None:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(Organization).where(Organization.id == id)
                    )
                )
                .scalars()
                .first()
            )
            return result

    async def get_users_organizations_and_participants_count(
        self, user_id: str
    ) -> list[Organization]:
        print(user_id)
        async with self.client() as session:
            session: AsyncSession
            query = (
                select(Organization)
                .join(
                    CrOrganizationsUsers,
                    Organization.id == CrOrganizationsUsers.organization_id,
                    full=True,
                )
                .where(or_(CrOrganizationsUsers.user_id == user_id, Organization.owner_id == user_id))
                .options(
                    selectinload(Organization.owner),
                    selectinload(Organization.members).selectinload(
                        CrOrganizationsUsers.user
                    ),
                )
            )

            result = await session.execute(query)
            organizations = result.unique().scalars().all()
            return organizations

    async def get_users_roles_in_organization(
        self, user_id: str, organization_id: str
    ) -> str:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(CrOrganizationsUsers.role).where(
                            and_(
                                CrOrganizationsUsers.organization_id == organization_id,
                                CrOrganizationsUsers.user_id == user_id,
                            )
                        )
                    )
                )
                .scalars()
                .first()
            )
            return result

    async def get_organization_details_by_id(
        self, organization_id: str
    ) -> OrganizationDetailsSchema:
        async with self.client() as session:
            session: AsyncSession

            organization_query = (
                select(Organization)
                .join(
                    CrOrganizationsUsers,
                    Organization.id == CrOrganizationsUsers.organization_id,
                )
                .where(CrOrganizationsUsers.organization_id == organization_id)
                .options(
                    selectinload(Organization.owner),
                    selectinload(Organization.members).selectinload(
                        CrOrganizationsUsers.user
                    ),
                )
            )

            result = (await session.execute(organization_query)).scalars().first()

            mean_ndvi = await self.manager.analrequests.get_requests_mean_ndvi_by_organization_fields(
                organization_id
            )
            # mean_ndvi = 0
            fields = await self.manager.fields.count_fields_by_organization_id(
                organization_id
            )

            return OrganizationDetailsSchema(
                id=result.id,
                name=result.name,
                fields=fields,
                mean_ndvi=mean_ndvi,
                users=[cr.user.as_schema_with_role(cr.role) for cr in result.members]
                + [result.owner.as_schema_with_role("owner")],
            )

    async def get_field_by_organization_id(
        self, organization_id: str
    ) -> list[FieldExtendedWithMeanValuesSchema] | list:
        async with self.client() as session:
            session: AsyncSession
            fields = list(
                (
                    (
                        await session.execute(
                            select(Field).where(
                                Field.organization_id == organization_id
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            requests = [
                await self.manager.analrequests.get_last_request_by_field(field.id)
                for field in fields
            ]

            return await self.manager.fields.construct_avg_data(fields, requests)

    async def create_organization(
        self, schema: OrganizationCreateSschema, user: User
    ) -> Organization:
        async with self.client() as session:
            session: AsyncSession
            organization = Organization(
                name=schema.name,
                is_public=schema.is_public,
                owner_id=user.id,
            )
            session.add(organization)
            await session.flush()
            await session.commit()
            return await self.get_users_organizations_and_participants_count(user.id)

    async def disband_organization(
        self, organization_id: str, user: User
    ) -> Organization:
        async with self.client() as session:
            session: AsyncSession
            organization = await session.execute(
                select(Organization).where(Organization.id == organization_id)
            )
            organization = organization.scalars().first()
            if not organization:
                raise CustomHTTPException(ExceptionCodes.ObjectNotFound)
            if organization.owner_id != user.id:
                raise CustomHTTPException(ExceptionCodes.NotEnoughPermissions)

            await session.execute(
                delete(Organization).where(Organization.id == organization_id)
            )
            await session.commit()

            return await self.get_users_organizations_and_participants_count(user.id)
