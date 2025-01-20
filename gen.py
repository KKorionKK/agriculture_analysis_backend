import asyncio
from api.mocks.generator import DataGenerator
import pickle


def test_dump():
    with open(
        "/Users/kkorionkk/PycharmProjects/agriculture_analysis/api/mocks/dump.pickle",
        "wb",
    ) as f:
        dump = pickle.dumps(
            {"users": [1, 2, 3], "main_user": 4, "organizations": ["a", "b", "c"]}
        )
        f.write(dump)


if __name__ == "__main__":
    gen = DataGenerator()
    asyncio.run(gen.create_mock_database())
    # test_dump()
