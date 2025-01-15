import asyncio
import uuid

from api.services.database import PostgreSQLController, SyncPostgreSQLController
from api.models import *
import random
from api.services.authorization import AuthorizationService

import pprint

roles = ["admin", "write", "read_only"]
async def test():
    c = PostgreSQLController(echo=True)
    await c.drop_db()
    await c.init_db()


def get_data():
    id_ = '44573348-2cb6-47bc-9893-c7a42a230a16'
    c = SyncPostgreSQLController()
    with c() as session:
        p = session.get(NDVIResult, id_)
    pprint.pprint(p.reports)

def create_organizations(user_id: str, users: list[User]):
    organizations: list[Organization] = []
    cr_items: list[CrOrganizationsUsers] = []

    names = ["Хуй", "Маму ебал", "Шлюхи", "Пидоры", "Калдыри", "Писькотрясы", "Бляди", "Пизда"]
    for i in range(len(names)):
        this_iter = bool(random.randint(0, 1))
        is_public = bool(random.randint(0, 1))
        org = Organization(
                id=uuid.uuid4().hex,
                name=names[i],
                is_public=is_public,
                owner_id=random.choice(users).id,
            )
        organizations.append(org)
        if this_iter:
            cr_items.append(
                CrOrganizationsUsers(
                    organization_id=org.id,
                    user_id=user_id,
                    role=random.choice(roles)
                )
            )
    return organizations, cr_items

def create_requests(count):
    pass

def create_other_users(count: int = 10):
    users: list[User] = []
    for i in range(count):
        users.append(
            User(
                id=uuid.uuid4().hex,
                email=uuid.uuid4().hex,
                password=AuthorizationService.hash_password(''.join([str(random.randint(0, 100)) for i in range(10)])),
                type="user"
            )
        )
    return users

def insert_field():
    c = SyncPostgreSQLController()
    user = User(
        email="hui@mail.com",
        password="$2b$12$5VQ8jdut4ZGDCsZUFy1ZuOTGQfQ9vY.p8GragUL3Fwc7w1nPnAUcS", # 1234
        type="user"
    )
    users = create_other_users()
    with c() as session:
        session.add(user)
        session.add_all(users)
        session.commit()
        session.flush()
    organization = Organization(
        name="ОАО Огурцы и помидоры",
        is_public=True,
        owner_id=user.id
    )
    organizations, crs = create_organizations(user.id, users)
    with c() as session:
        session.add(organization)
        session.add_all(organizations)
        session.add_all(crs)
        session.commit()
        session.flush()
    fields = [
        Field(
            name='Тестовое поле',
            color='#088',
            coordinates=[
                {"latitude": 55.773097205876795, "longitude": 37.53753662109376},
                {"latitude": 55.7309766355099, "longitude": 37.53753662109376},
                {"latitude": 55.73484280305744, "longitude": 37.770309448242195},
                {"latitude": 55.80205284218845, "longitude": 37.76893615722656}
            ],
            area=224,
            owner_id=user.id
        ),
        Field(
            name='Тестовое поле 2',
            color='#088',
            coordinates=[
                {"latitude": 55.873097205876795, "longitude": 37.63753662109376},
                {"latitude": 55.8309766355099, "longitude": 37.63753662109376},
                {"latitude": 55.83484280305744, "longitude": 37.870309448242195},
                {"latitude": 55.90205284218845, "longitude": 37.86893615722656}
            ],
            area=224,
            owner_id=user.id
        )
    ]
    with c() as session:
        session.add_all(fields)
        session.commit()


if __name__ == "__main__":
    asyncio.run(test())
    insert_field()
    # get_data()
