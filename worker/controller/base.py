import multiprocessing
import queue
import os
from pathlib import Path
from typing import Callable

from logging import Logger

from worker.utils.extractor import Extractor
from worker.utils.enumerations import AnalysisType
from worker.analysis.ndvi import NDVIAnalyzer

from worker.utils.vigilante import Vigilante
from worker.utils.database import SyncPostgreSQLController

from .model import Task


class InstanceController:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(InstanceController, cls).__new__(cls)
        return cls.__instance

    def __init__(self, node_name: str, logger: Logger, workers: int = 1, current_directory: str = None):
        """
        Class that controlls the flow and producing workers. Let them know about tasks.

        :param node_name: The name of this node
        :param workers: Number of workers (processes)
        """
        if not hasattr(self, 'initialized'):
            self.node_name = node_name
            self.workers = workers
            self.logger: Logger = logger
            self.__tasks_queue = multiprocessing.Queue()
            self.__done_queue = multiprocessing.Queue()

            self.__process_pool: list[multiprocessing.Process] = []
            self.current_directory = current_directory

            self._inc = 0
            self.initialized = True

    @staticmethod
    def get_instance_by_type(ttype: AnalysisType, current_hash: str, pid, current_directory):
        if ttype == AnalysisType.ndvi:
            logger = Vigilante(f'ndvi_analyzer_{pid}', True, True, Path(current_directory, current_directory + "/worker_logs/")).get_logger()
            db = SyncPostgreSQLController()
            return NDVIAnalyzer(logger, db, current_hash)

    @staticmethod
    def _worker(tasks_q: multiprocessing.Queue, done_q: multiprocessing.Queue, current_directory: str):
        pid = multiprocessing.current_process().pid
        logger = Vigilante(f'process_{pid}', True, True, Path(current_directory, current_directory + "/worker_logs/")).get_logger()
        print(f"PID: {pid} working...")
        while True:
            try:
                task = tasks_q.get(timeout=5)
                try:
                    ext = Extractor(current_directory)
                    print(f'Got task: {task}')
                    zip_path = ext.download(task.task.origin_ndvi_data, task.task.id)
                    logger.info(f"PID: {pid} downloaded archive...")
                    print('Downloaded archive')
                    extracted = ext.extract(zip_path, task.task.id)
                    logger.info(f"PID: {pid} extracted data...")
                    instance = InstanceController.get_instance_by_type(task.ttype, task.task.id, pid, current_directory)
                    logger.info(f"PID: {pid} started to analyze data...")
                    instance.analyze(extracted, task.task, current_directory)

                    done_q.put((task.task_id, 'OK', None))
                    logger.info(f"Worker {pid} done task {task.task_id}")
                except Exception as e:
                    done_q.put((task.task_id, None, str(e)))
                    print(f"Exception from worker {pid} while executing task {task.task_id}: {e}")
                    logger.error(
                        f"Exception from worker {pid} while executing task {task.task_id}: {e}"
                    )
            except queue.Empty:
                continue

    def run(self):
        print("Creating workers")
        self.__create_processes()
        print("Successfully created workers")

    def __create_processes(self) -> None:
        for i in range(self.workers):
            process = multiprocessing.Process(
                target=self._worker, args=(self.__tasks_queue, self.__done_queue, self.current_directory)
            )
            process.start()
            self.__process_pool.append(process)

    def send_task(self, ttype: AnalysisType, task, *args, **kwargs):
        task = Task(task_id=self._inc, task=task, ttype=ttype, args=args, kwargs=kwargs)
        self.__tasks_queue.put(task)

    @staticmethod
    def get_controller(node_name: str, workers: int, logger: Logger, current_directory: str):
        return InstanceController(node_name, logger, workers, current_directory)
