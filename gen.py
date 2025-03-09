import asyncio
from api.mocks.generator import DataGenerator
import pickle

from api.services.database import PostgreSQLController


def test_dump():
    with open(
        "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/dump.pickle",
        "wb",
    ) as f:
        dump = pickle.dumps(
            {"users": [1, 2, 3], "main_user": 4, "organizations": ["a", "b", "c"]}
        )
        f.write(dump)


async def init():
    c = PostgreSQLController(echo=True)
    await c.drop_db()
    await c.init_db()
    gen = DataGenerator()
    await gen.create_mock_database()


if __name__ == "__main__":
    asyncio.run(init())
    # test_dump()
