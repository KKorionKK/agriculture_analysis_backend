from .base import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update, and_
from sqlalchemy.orm import selectinload
from api.models import AnalyzeRequest, User, NDVIResult, Field
from api.common.enumerations import DataStatus

from api.schemas.analyze_request import AnalyzeRequestCreate, AnalyzeRequestUpdate


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

    async def get_request_info_by_id(self, request_id: str):
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(AnalyzeRequest)
                        .where(AnalyzeRequest.id == request_id)
                        .options(
                            selectinload(AnalyzeRequest.ndvi_result),
                            selectinload(AnalyzeRequest.plants_result),
                        )
                    )
                )
                .scalars()
                .first()
            )
            return result.as_detail_schema()

    async def get_requests_by_field(self, field_id: str) -> list[AnalyzeRequest] | list:
        async with self.client() as session:
            session: AsyncSession
            result = list(
                (
                    (
                        await session.execute(
                            select(AnalyzeRequest)
                            .where(AnalyzeRequest.field_id == field_id)
                            .order_by(desc(AnalyzeRequest.created_at))
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            return result

    async def get_requests_mean_ndvi_by_organization_fields(
        self, organization_id: str
    ) -> float:
        async with self.client() as session:
            session: AsyncSession
            result: list[dict] = list(
                (
                    (
                        await session.execute(
                            select(NDVIResult.reports)
                            .join(
                                AnalyzeRequest,
                                AnalyzeRequest.ndvi_result_id == NDVIResult.id,
                            )
                            .join(Field, Field.id == AnalyzeRequest.field_id)
                            .where(
                                Field.organization_id == organization_id
                            )  # TODO: смотреть по последним анализам
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            determinant = len(result)
            numerator = sum(
                [
                    sum([report["affected_percentage"] for report in item])
                    for item in result
                ]
            )
            return round(numerator / determinant / 1000, 2)

    async def get_last_request_by_field(self, field_id: str) -> AnalyzeRequest | None:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(AnalyzeRequest)
                        .where(AnalyzeRequest.field_id == field_id)
                        .order_by(desc(AnalyzeRequest.created_at))
                        .options(
                            selectinload(AnalyzeRequest.plants_result),
                            selectinload(AnalyzeRequest.ndvi_result),
                        )
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
                title=data.title,
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

    async def update_request(
        self, data: AnalyzeRequestUpdate, user: User
    ) -> AnalyzeRequest | None:
        async with self.client() as session:
            session: AsyncSession
            # update origin_ndvi_data and origin_plants_data on data.analyze_id
            request = (
                (
                    await session.execute(
                        select(AnalyzeRequest).where(
                            and_(
                                AnalyzeRequest.id == data.analyze_id,
                                AnalyzeRequest.issuer_id == user.id,
                            )
                        )
                    )
                )
                .scalars()
                .first()
            )

            if not request:
                return None

            new_ndvi = request.origin_ndvi_data
            new_plants = request.origin_plants_data
            new_ndvi_status = DataStatus(request.ndvi_status)
            new_plants_status = DataStatus(request.plants_status)

            if request.origin_ndvi_data != data.origin_ndvi_data:
                new_ndvi = data.origin_ndvi_data
                new_ndvi_status = DataStatus.waiting

            if request.origin_plants_data != data.origin_plants_data:
                new_plants = data.origin_plants_data
                new_plants_status = DataStatus.waiting

            await session.execute(
                update(AnalyzeRequest)
                .where(AnalyzeRequest.id == data.analyze_id)
                .values(
                    origin_ndvi_data=new_ndvi,
                    origin_plants_data=new_plants,
                    ndvi_status=new_ndvi_status.value,
                    plants_status=new_plants_status.value,
                    title=data.title,
                )
            )
            await session.flush([request])
            await session.commit()
            return request
