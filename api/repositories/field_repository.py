from .base import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, func, update
from api.models import (
    Field,
    User,
    AnalyzeRequest,
    NDVIResult,
    PlantsResult,
    Organization,
    CrOrganizationsUsers,
)

from api.common.enumerations import DataUploadedStatus, HealthStatus, DataStatus

from api.schemas.fields import (
    FieldCreateSchema,
    FieldExtendedSchema,
    FieldDetailSchema,
    AnalysisRequest,
    NDVIAnalysisSchema,
    PlantsAnalysisSchema,
    NDVIReport,
    FieldExtendedWithMeanValuesSchema,
)

from api.common.exceptions import ExceptionCodes, CustomHTTPException


class FieldsRepository(Repository):
    async def get_fields_by_user(self, user_id: str) -> list[Field] | list:
        async with self.client() as session:
            session: AsyncSession
            result = list(
                (
                    (
                        await session.execute(
                            select(Field).where(Field.owner_id == user_id)
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            return result

    async def count_fields_by_user_id(self, user_id: str) -> int:
        async with self.client() as session:
            session: AsyncSession
            result = list(
                (
                    (
                        await session.execute(
                            select(Field.id, func.count()).where(
                                Field.owner_id == user_id
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
            )
            return result

    async def count_fields_by_organization_id(self, organization_id: str) -> int:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(Field.id, func.count())
                        .where(Field.organization_id == organization_id)
                        .group_by(Field.id)
                    )
                )
                .scalars()
                .all()
            )
            return len(result) if result else 0

    async def __construct_data(
        self, fields: list[Field], requests: list[AnalyzeRequest]
    ) -> list[FieldExtendedSchema] | list:
        schemas = []
        for i in range(len(fields)):
            if not requests[i]:
                schemas.append(
                    FieldExtendedSchema(
                        id=fields[i].id,
                        name=fields[i].name,
                        analysis_dt=fields[i].last_analysed,
                        health_status="Нет данных",
                        data_status=DataUploadedStatus.missing,
                        color=fields[i].color,
                        coordinates=fields[i].coordinates,
                    )
                )
                continue
            health_status = HealthStatus.optimal
            data_status = None

            if requests[i].origin_ndvi_data and requests[i].origin_plants_data:
                data_status = DataUploadedStatus.complete
            elif requests[i].origin_ndvi_data or requests[i].origin_plants_data:
                data_status = DataUploadedStatus.partial
            else:
                data_status = DataUploadedStatus.missing

            # if requests[i].plants_result: # TODO: сделать анализ с нейронкой
            #     for report in requests[i].plants_result.reports:
            #         if report['affected_percentage'] > 50:
            #             health_status = HealthStatus.critical
            #         if report['affected_percentage'] > 25:
            #             health_status = HealthStatus.need_attention

            if requests[i].ndvi_result:
                for report in requests[i].ndvi_result.reports:
                    if report["affected_percentage"] >= 50:
                        health_status = HealthStatus.critical
                    if report["affected_percentage"] >= 25:
                        health_status = HealthStatus.need_attention

            schemas.append(
                FieldExtendedSchema(
                    id=fields[i].id,
                    name=fields[i].name,
                    analysis_dt=fields[i].last_analysed,
                    health_status=health_status,
                    data_status=data_status,
                )
            )
        return schemas

    async def get_extended_fields_data_by_user(
        self, user_id: str
    ) -> list[FieldExtendedSchema] | list:
        async with self.client() as session:
            session: AsyncSession
            fields = list(
                (
                    (
                        await session.execute(
                            select(Field).where(Field.owner_id == user_id)
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

            return await self.__construct_data(fields, requests)

    async def get_extended_fields_data_by_user_with_avg_values(
        self, user_id: str
    ) -> list[FieldExtendedWithMeanValuesSchema] | list:
        async with self.client() as session:
            session: AsyncSession
            fields = list(
                (
                    (
                        await session.execute(
                            select(Field).where(Field.owner_id == user_id)
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

            return await self.construct_avg_data(fields, requests)

    async def construct_avg_data(
        self, fields: list[Field], requests: list[AnalyzeRequest]
    ) -> list[FieldExtendedWithMeanValuesSchema]:
        schemas: list[FieldExtendedWithMeanValuesSchema] = []
        for i in range(len(fields)):
            if not requests[i]:
                schemas.append(
                    FieldExtendedWithMeanValuesSchema(
                        id=fields[i].id,
                        name=fields[i].name,
                        color=fields[i].color,
                        coordinates=fields[i].coordinates,
                        mean_ndvi=0,
                        mean_health=0,
                        mean_disease=0,
                        area=fields[i].area,
                    )
                )
                continue
            mean_ndvi = 0
            mean_health = 0
            mean_disease = 0
            if requests[i].ndvi_result:
                mean_ndvi = round(
                    sum(
                        [
                            report["affected_percentage"]
                            for report in requests[i].ndvi_result.reports
                        ]
                    )
                    / len(requests[i].ndvi_result.reports),
                    2,
                )
                mean_health = round(
                    sum(
                        [
                            report["plants_percentage"]
                            for report in requests[i].ndvi_result.reports
                        ]
                    )
                    / len(requests[i].ndvi_result.reports),
                    2,
                )
                mean_disease = round(
                    sum(
                        [
                            report["affected_percentage"]
                            for report in requests[i].ndvi_result.reports
                        ]
                    )
                    / len(requests[i].ndvi_result.reports),
                    2,
                )

            schemas.append(
                FieldExtendedWithMeanValuesSchema(
                    id=fields[i].id,
                    name=fields[i].name,
                    color=fields[i].color,
                    coordinates=fields[i].coordinates,
                    mean_ndvi=mean_ndvi,
                    mean_health=mean_health,
                    mean_disease=mean_disease,
                    area=fields[i].area,
                )
            )
        return schemas

    async def create_field(self, data: FieldCreateSchema, user: User) -> Field:
        async with self.client() as session:
            session: AsyncSession
            field = Field(
                color=data.color,
                coordinates=[crd.model_dump() for crd in data.coordinates],
                area=data.area,
                name=data.name,
                owner_id=user.id,
            )
            session.add(field)
            await session.flush()
            await session.commit()
            return field

    async def _define_disease_focus(self, ndvi_reports: list[NDVIReport]) -> tuple:
        mx = 0
        mx_i = 0
        for i in range(len(ndvi_reports)):
            if ndvi_reports[i].affected_percentage > mx:
                mx = ndvi_reports[i].affected_percentage
                mx_i = i

        return ndvi_reports[mx_i].longitude, ndvi_reports[mx_i].latitude

    async def _collect_additional_data(self, field_id: str) -> list[AnalysisRequest]:
        requests: list[AnalyzeRequest] = (
            await self.manager.analrequests.get_requests_by_field(field_id)
        )
        schemas: list[AnalysisRequest] = []
        async with self.client() as session:
            session: AsyncSession
            for request in requests:
                ndvi: NDVIResult = (
                    (
                        await session.execute(
                            select(NDVIResult).where(
                                NDVIResult.id == request.ndvi_result_id
                            )
                        )
                    )
                    .scalars()
                    .first()
                )
                ndvi_schema = None
                plants: PlantsResult = (
                    (
                        await session.execute(
                            select(PlantsResult).where(
                                PlantsResult.id == request.plants_result_id
                            )
                        )
                    )
                    .scalars()
                    .first()
                )
                plants_schema = None
                if ndvi:
                    ndvi_schema = NDVIAnalysisSchema(
                        id=ndvi.id,
                        gis_file=ndvi.gis_file,
                        reports=[NDVIReport.from_dict(item) for item in ndvi.reports],
                    )
                if plants:  # TODO: переделать
                    plants_schema = PlantsAnalysisSchema(
                        id=plants.id, gis_file=plants.gis_file, reports=plants.report
                    )

                schemas.append(
                    AnalysisRequest(
                        request_id=request.id,
                        title=request.title,
                        requested_dt=request.created_at,
                        ndvi_analyze_status=request.ndvi_status,
                        plants_analyze_status=request.plants_status,
                        fail_info=request.fail_info,
                        disease_focus=(
                            await self._define_disease_focus(ndvi_schema.reports)
                            if ndvi
                            else None
                        ),
                        ndvi=ndvi_schema,
                        plant=plants_schema,
                    )
                )
        return schemas

    async def _calc_last_avg_data(self, data: list[AnalysisRequest]):
        avg_ndvi = 0
        avg_vegetation = 0
        avg_decease = 0

        last_completed = None
        for item in data:
            if item.ndvi_analyze_status == DataStatus.ready:
                last_completed = item
                break
        if not last_completed:
            return avg_ndvi, avg_vegetation, avg_decease

        ndvi_reports_count = 1

        if last_completed.ndvi:
            ndvi_reports_count = len(last_completed.ndvi.reports)
            for item in last_completed.ndvi.reports:
                if item.ndvi:
                    avg_ndvi += item.ndvi
                    avg_vegetation += item.plants_percentage
                    avg_decease += item.affected_percentage

        avg_ndvi /= round(ndvi_reports_count, 2)
        avg_vegetation /= round(ndvi_reports_count, 2)
        avg_decease /= round(ndvi_reports_count, 2)

        return avg_ndvi, avg_vegetation, avg_decease

    async def get_field_details(
        self, field_id: str, user_id: str
    ) -> FieldDetailSchema | None:
        async with self.client() as session:
            session: AsyncSession
            field: Field | None = (
                (
                    await session.execute(
                        select(Field).where(
                            and_(Field.id == field_id, Field.owner_id == user_id)
                        )
                    )
                )
                .scalars()
                .first()
            )

            if not field:
                return None

            analysis = await self._collect_additional_data(field_id)
            avg_ndvi, avg_vegetation, avg_decease = await self._calc_last_avg_data(
                analysis
            )

            return FieldDetailSchema(
                id=field.id,
                name=field.name,
                area=str(field.area),
                last_analyzed=field.last_analysed,
                avg_ndvi=avg_ndvi,
                avg_vegetation=avg_vegetation,
                avg_decease=avg_decease,
                analrequests=analysis,
            )

    async def delete_field_by_id(self, field_id: str, user_id: str):
        async with self.client() as session:
            session: AsyncSession
            await session.execute(
                delete(Field).where(
                    and_(Field.id == field_id, Field.owner_id == user_id)
                )
            )
            await session.commit()

    async def append_field_to_organization(
        self, field_id: str, organization_id: str, user: User
    ) -> Field:
        async with self.client() as session:
            session: AsyncSession
            field = await session.execute(select(Field).where(Field.id == field_id))
            field = field.scalars().first()
            if not field:
                raise CustomHTTPException(ExceptionCodes.ObjectNotFound)
            if field.owner_id != user.id:
                raise CustomHTTPException(ExceptionCodes.NotEnoughPermissions)
            # check if organization exists
            organization = await session.execute(
                select(Organization).where(Organization.id == organization_id)
            )
            organization = organization.scalars().first()
            if not organization:
                raise CustomHTTPException(ExceptionCodes.ObjectNotFound)

            # check if user in organization
            cr = await session.execute(
                select(CrOrganizationsUsers).where(
                    CrOrganizationsUsers.user_id == user.id,
                    CrOrganizationsUsers.organization_id == organization_id,
                )
            )
            cr = cr.scalars().first()
            if not cr:
                raise CustomHTTPException(ExceptionCodes.NotEnoughPermissions)

            await session.execute(
                update(Field)
                .where(Field.id == field_id)
                .values(organization_id=organization_id)
            )
            await session.commit()

            return await self.get_field_details(field_id, user.id)
