import asyncio
from api.services.pg_manager import PGManager

async def test():
    user_id = '00700244-0077-4ec3-98a1-9eacee046819'
    pg = PGManager()
    res = await pg.organizations.get_users_organizations_and_participants_count(user_id)
    print('')

async def test_roles():
    org_id = '7211aef1332f48a0a48aa8f2d6ee844e'
    user_id = '00700244-0077-4ec3-98a1-9eacee046819'
    pg = PGManager(True)
    res = await pg.organizations.get_users_roles_in_organization(user_id, org_id)
    print('')

asyncio.run(test())