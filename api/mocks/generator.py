import uuid
import random
import pprint
import os
import copy
import datetime
import pickle

from api.services.database import PostgreSQLController
from api.models import *
from api.services.authorization import AuthorizationService
from api.common.enumerations import Roles, DataStatus

import dataclasses
from typing import Tuple


@dataclasses.dataclass
class NDVIResultDTO:
    affected_percentage: float
    plants_percentage: float
    ndvi_map: str
    problems_map: str
    coordinates: Tuple[float, float] | None

    def as_dict(self):
        return dataclasses.asdict(self)


class DataGenerator:
    main_user_roles = ["admin", "write", "read_only"]
    others_users_roles = [*Roles._member_names_]
    __emails_path = (
        "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/emails.txt"
    )
    __fields_path = (
        "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/fields.txt"
    )
    __organizations_path = "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/organizations.txt"

    FIELDS_PER_ORGANIZATION_ON_USER = 1
    MAIN_USER_IN_ORGANIZATIONS = 3

    def __init__(self):
        self.emails = []
        self.fields = []
        self.organizations = []
        self.__load_data(self.__emails_path, self.emails)
        self.__load_data(self.__fields_path, self.fields)
        self.__load_data(self.__organizations_path, self.organizations)
        self.__log_filepath = (
            "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/log.txt"
        )
        self.__dump_filepath = "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/dump.pickle"
        self.__clear_log_file()

        self.users_in_organizations = None
        self.users_fields = None

    def __clear_log_file(self):
        if os.path.exists(self.__log_filepath):
            os.remove(self.__log_filepath)

    def __log(self, data: list[str]):
        with open(self.__log_filepath, "x+") as f:
            for line in data:
                f.write(line + "\n")
            f.write("\n______________________________\n\n")

    def __dump(self, **kwargs):
        with open(self.__dump_filepath, "wb") as f:
            dump = pickle.dumps({**kwargs})
            f.write(dump)

    def __load_dump(self):
        with open(self.__dump_filepath, "rb") as f:
            buffer = f.read()
            dump = pickle.loads(buffer)
            return dump

    def __load_data(self, path: str, target: list[str]):
        with open(path) as f:
            for line in f.readlines():
                target.append(line.split(". ")[-1].strip())

    def __create_main_test_user(self) -> User:
        return User(
            id=uuid.uuid4().hex,
            email="user@mail.com",
            password="$2b$12$5VQ8jdut4ZGDCsZUFy1ZuOTGQfQ9vY.p8GragUL3Fwc7w1nPnAUcS",  # 1234
            type="user",
        )

    async def commit_to_database(
        self,
        users: list[User],
        organizations: list[Organization],
        crs: list[CrOrganizationsUsers],
        fields: list[Field],
        analrequests: list[AnalyzeRequest],
        ndvis: list[NDVIResult],
        plants: list[PlantsResult],
    ):
        pg = PostgreSQLController(True)
        await pg.drop_db()
        await pg.init_db()
        async with pg() as session:
            session.add_all(users)
            session.add_all(organizations)
            session.add_all(crs)
            session.add_all(fields)
            session.add_all(analrequests)
            session.add_all(ndvis)
            session.add_all(plants)
            await session.flush()
            await session.commit()

    def __add_main_user_fields(self, main_user: User, fields: list[Field]) -> None:
        self.users_fields[main_user.id] = fields

    async def create_mock_database(
        self,
        organizations_count: int = 10,
        users_count: int = 50,
        fields_count: int = 100,
        requests_count: int = 200,
    ) -> None:
        users = await self.create_users(users_count)
        main_user = self.__create_main_test_user()
        main_user_fields = self.create_main_user_fields(main_user)
        organizations, crs = await self.create_organizations(
            main_user, users, organizations_count
        )
        fields = await self.create_fields(users, main_user_fields)

        self.__add_main_user_fields(main_user, main_user_fields)

        analrequests, ndvis, plants = await self.create_requests(users + [main_user])
        self.__dump(
            users=users,
            main_user=main_user,
            organizations=organizations,
            fields=fields,
            analrequests=analrequests,
            ndvis=ndvis,
            plants=plants,
            crs=crs,
            main_user_fields=main_user_fields,
        )
        # d = self.__load_dump()
        # users = d['users']
        # main_user = d['main_user']
        # organizations = d['organizations']
        # fields = d['fields']
        # main_user_fields = d['main_user_fields']
        # analrequests = d['analrequests']
        # ndvis = d['ndvis']
        # plants = d['plants']
        # crs = d['crs']

        await self.commit_to_database(
            users=users + [main_user],
            fields=fields + main_user_fields,
            organizations=organizations,
            crs=crs,
            analrequests=analrequests,
            ndvis=ndvis,
            plants=plants,
        )

    async def create_users(self, count: int) -> list[User]:
        users: list[User] = []
        log_data: list[str] = []
        for i in range(count):
            # pwd = ''.join([str(random.randint(0, 100)) for i in range(10)])
            pwd = "12345"
            users.append(
                User(
                    id=uuid.uuid4().hex,
                    email=self.emails[i],
                    password=AuthorizationService.hash_password(pwd),
                    type="user",
                )
            )
            log_data.append(f"User created: {self.emails[i]} and has password: {pwd}")
        self.__log(log_data)
        return users

    def create_main_user_fields(self, user: User) -> list[Field]:
        return [
            Field(
                id=uuid.uuid4().hex,
                name="Тестовое поле",
                color="#088",
                coordinates=[
                    {"latitude": 55.773097205876795, "longitude": 37.53753662109376},
                    {"latitude": 55.7309766355099, "longitude": 37.53753662109376},
                    {"latitude": 55.73484280305744, "longitude": 37.770309448242195},
                    {"latitude": 55.80205284218845, "longitude": 37.76893615722656},
                ],
                area=224,
                owner_id=user.id,
            ),
            Field(
                id=uuid.uuid4().hex,
                name="Тестовое поле 2",
                color="#088",
                coordinates=[
                    {"latitude": 55.873097205876795, "longitude": 37.63753662109376},
                    {"latitude": 55.8309766355099, "longitude": 37.63753662109376},
                    {"latitude": 55.83484280305744, "longitude": 37.870309448242195},
                    {"latitude": 55.90205284218845, "longitude": 37.86893615722656},
                ],
                area=224,
                owner_id=user.id,
            ),
        ]

    async def __sweet_disposition(
        self, users: list[User], organizations_count: int
    ) -> dict[int, list[str]]:
        result: dict[int, list[str]] = {k: [] for k in range(organizations_count)}
        users_cp = copy.deepcopy(users)

        while users_cp:
            result[random.randint(0, organizations_count - 1)].append(
                users_cp.pop(0).id
            )

        return result

    async def create_organizations(
        self, main_user: User, users: list[User], organizations_count: int
    ):
        organizations: list[Organization] = []
        cr_items: list[CrOrganizationsUsers] = []

        disposition = await self.__sweet_disposition(users, organizations_count)
        main_owner = False

        for i in range(organizations_count):
            is_public = bool(random.randint(0, 1))
            org = Organization(
                id=uuid.uuid4().hex,
                name=self.organizations[i],
                is_public=is_public,
                owner_id=disposition[i].pop(0) if main_owner else main_user.id,
            )
            organizations.append(org)
            main_owner = True

        users_in_organizations = {org.id: [] for org in organizations}
        org_counter = 0
        main_organizations = 0

        while (
            len(cr_items)
            <= len(users) + self.MAIN_USER_IN_ORGANIZATIONS - organizations_count
        ):
            if org_counter == organizations_count:
                org_counter = 0
            if (
                main_organizations < self.MAIN_USER_IN_ORGANIZATIONS
                and organizations[org_counter].owner_id != main_user.id
            ):
                cr_items.append(
                    CrOrganizationsUsers(
                        organization_id=organizations[org_counter].id,
                        user_id=main_user.id,
                        role=random.choice(self.main_user_roles),
                    )
                )
                users_in_organizations[organizations[org_counter].id].append(
                    main_user.id
                )
                org_counter += 1
                main_organizations += 1
            else:
                if len(disposition[org_counter]) > 0:
                    this_user_id = disposition[org_counter].pop(0)
                    cr_items.append(
                        CrOrganizationsUsers(
                            organization_id=organizations[org_counter].id,
                            user_id=this_user_id,
                            role=random.choice(self.main_user_roles),
                        )
                    )
                    users_in_organizations[organizations[org_counter].id].append(
                        this_user_id
                    )
                    org_counter += 1
                else:
                    org_counter += 1

        self.users_in_organizations = users_in_organizations
        self.__optimize()
        return organizations, cr_items

    def __optimize(self):
        for k, v in self.users_in_organizations.items():
            self.users_in_organizations[k] = set(v)

    def __find_organization(self, user_id: str):
        for k, v in self.users_in_organizations.items():
            if user_id in v:
                return k
        return None

    async def create_fields(
        self, users: list[User], main_user_fields: list[Field]
    ) -> list[Field]:
        fields: list[Field] = []
        fc = 0
        users_fields = {user.id: [] for user in users}
        with_org = 0
        for user in users:
            deviation = random.uniform(-0.5, 0.5)
            organization_id = self.__find_organization(user.id)
            if organization_id:
                with_org += 1
            else:
                print(f"User {user.email} has no organization")
            field1 = Field(
                id=uuid.uuid4().hex,
                name=self.fields[fc],
                color="#088",
                coordinates=[
                    {
                        "latitude": 55.573097205876795 + deviation,
                        "longitude": 37.33753662109376 + deviation,
                    },
                    {
                        "latitude": 55.5309766355099 + deviation,
                        "longitude": 37.33753662109376 + deviation,
                    },
                    {
                        "latitude": 55.53484280305744 + deviation,
                        "longitude": 37.570309448242195 + deviation,
                    },
                    {
                        "latitude": 55.60205284218845 + deviation,
                        "longitude": 37.56893615722656 + deviation,
                    },
                ],
                organization_id=organization_id,
                area=224,
                owner_id=user.id,
            )
            fc += 1
            deviation = random.uniform(-0.5, 0.5)
            field2 = Field(
                id=uuid.uuid4().hex,
                name=self.fields[fc],
                color="#088",
                coordinates=[
                    {
                        "latitude": 55.573097205876795 + deviation,
                        "longitude": 37.33753662109376 + deviation,
                    },
                    {
                        "latitude": 55.5309766355099 + deviation,
                        "longitude": 37.33753662109376 + deviation,
                    },
                    {
                        "latitude": 55.53484280305744 + deviation,
                        "longitude": 37.570309448242195 + deviation,
                    },
                    {
                        "latitude": 55.60205284218845 + deviation,
                        "longitude": 37.56893615722656 + deviation,
                    },
                ],
                organization_id=organization_id,
                area=224,
                owner_id=user.id,
            )
            users_fields[user.id].append(field1)
            users_fields[user.id].append(field2)
            fields += [field1, field2]
        users_fields[main_user_fields[0].owner_id] = main_user_fields
        self.users_fields = users_fields
        pprint.pprint(f"Fields with organization id: {with_org}")
        return fields

    def create_reports(self, count: int = 10):
        reports: list[dict] = []

        for i in range(count):
            reports.append(
                NDVIResultDTO(
                    affected_percentage=random.uniform(0, 100),
                    plants_percentage=random.uniform(0, 100),
                    ndvi_map="123",
                    problems_map="123",
                    coordinates=(123, 123),
                ).as_dict()
            )
        return reports

    def __create_ndvi(self, field: Field, created_at: datetime.datetime) -> NDVIResult:
        return NDVIResult(
            id=uuid.uuid4().hex,
            reports=self.create_reports(),
            heatmaps=[],
            issuer_id=field.owner_id,
            created_at=created_at,
            rast=None,
        )

    def __create_plants(
        self, field: Field, created_at: datetime.datetime
    ) -> PlantsResult:
        return PlantsResult(
            id=uuid.uuid4().hex,
            report=NDVIResultDTO(
                affected_percentage=random.uniform(0, 100),
                plants_percentage=random.uniform(0, 100),
                ndvi_map="123",
                problems_map="123",
                coordinates=(123, 123),
            ).as_dict(),
            artifacts=[],
            issuer_id=field.owner_id,
            created_at=created_at,
        )

    async def create_requests(
        self, users: list[User], requests_count_per_field: int = 10
    ):
        analrequests: list[AnalyzeRequest] = []
        ndvis: list[NDVIResult] = []
        plants: list[PlantsResult] = []
        for user in users:
            if not self.users_fields[user.id]:
                continue
            for field in self.users_fields[user.id]:
                for i in range(requests_count_per_field):
                    ndvi = None
                    plant = None
                    this_ndvi = bool(random.randint(0, 1))
                    this_plants = bool(random.randint(0, 1))
                    # this_failed = bool(random.randint(0, 1))

                    created_at = datetime.datetime.now(
                        datetime.timezone.utc
                    ) + random.choice([-1, 1]) * datetime.timedelta(
                        days=random.randint(1, 15)
                    )

                    if this_ndvi:
                        ndvi = self.__create_ndvi(field, created_at)
                        ndvis.append(ndvi)
                    if this_plants:
                        plant = self.__create_plants(field, created_at)
                        plants.append(plant)

                    request = AnalyzeRequest(
                        id=uuid.uuid4().hex,
                        title="Анализ поля 12 марта",
                        origin_ndvi_data="123" if this_ndvi else None,
                        origin_plants_data="123" if this_plants else None,
                        ndvi_status=random.choice([*DataStatus._member_names_]),
                        plants_status=random.choice([*DataStatus._member_names_]),
                        fail_info=None,
                        field_id=field.id,
                        ndvi_result_id=ndvi.id if ndvi else None,
                        plants_result_id=plant.id if plant else None,
                        issuer_id=user.id,
                        created_at=created_at,
                    )
                    analrequests.append(request)
        return analrequests, ndvis, plants
