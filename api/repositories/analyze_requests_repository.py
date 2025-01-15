from .base import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload
from api.models import AnalyzeRequest, User, NDVIResult, Field
from sqlalchemy.orm import selectinload
from api.common.enumerations import DataStatus

from api.schemas.analyze_request import AnalyzeRequestCreate


class AnalyzeRequestsRepository(Repository):
    async def get_requests_by_user(self, user_id: str) -> list[AnalyzeRequest] | list:
        async with self.client() as session:
            session: AsyncSession
            result = list(
                (
                    (
                        await session.execute(
                            select(AnalyzeRequest).where(
                                AnalyzeRequest.issuer_id == user_id
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            return result

    async def get_requests_by_field(self, field_id: str) -> list[AnalyzeRequest] | list:
        async with self.client() as session:
            session: AsyncSession
            result = list(
                (
                    (
                        await session.execute(
                            select(AnalyzeRequest).where(
                                AnalyzeRequest.field_id == field_id
                            )
                            .order_by(desc(AnalyzeRequest.created_at))
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            return result

    async def get_requests_mean_ndvi_by_organization_fields(self, organization_id: str) -> float:
        async with self.client() as session:
            session: AsyncSession
            result: list[dict] = list(
                (
                    (
                        await session.execute(
                            select(NDVIResult.reports)
                            .join(AnalyzeRequest, AnalyzeRequest.ndvi_result_id == NDVIResult.id)
                            .join(Field, Field.id == AnalyzeRequest.field_id)
                            .where(Field.organization_id == organization_id)  # TODO: смотреть по последним анализам
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            determinant = len(result)
            numerator = sum([sum([report['affected_percentage'] for report in item]) for item in result])
            return round(numerator / determinant / 1000, 2)

    async def get_last_request_by_field(self, field_id: str) -> AnalyzeRequest | None:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(AnalyzeRequest).where(
                            AnalyzeRequest.field_id == field_id
                        )
                        .order_by(desc(AnalyzeRequest.created_at))
                        .options(selectinload(AnalyzeRequest.plants_result), selectinload(AnalyzeRequest.ndvi_result))
                    )
                )
                .scalars()
                .first()
            )
            return result

    async def create_request(
        self, data: AnalyzeRequestCreate, user: User
    ) -> AnalyzeRequest:
        ndvi_status = DataStatus.declined
        plants_status = DataStatus.declined
        if data.origin_plants_data:
            plants_status = DataStatus.waiting
        if data.origin_ndvi_data:
            ndvi_status = DataStatus.waiting
        async with self.client() as session:
            session: AsyncSession
            request = AnalyzeRequest(
                origin_ndvi_data=data.origin_ndvi_data,
                origin_plants_data=data.origin_plants_data,
                ndvi_status=ndvi_status.value,
                plants_status=plants_status.value,
                field_id=data.field_id,
                issuer_id=user.id,
            )
            session.add(request)
            await session.flush()
            await session.commit()
            return request
