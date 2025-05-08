from worker.mq.controller import Master
from common.database import SyncPostgreSQLController
import os
from pathlib import Path

from worker.utils.vigilante import Vigilante

if __name__ == "__main__":

    database = SyncPostgreSQLController()
    v = Vigilante(
        "test_worker", True, True, Path(os.getcwd(), os.getcwd() + "/worker_logs/")
    )
    c = Master("test_worker", 1, database, v.get_logger(), os.getcwd() + "/worker")
    c.run()
