import pika
from worker import config
from worker.utils.enumerations import AnalysisType
from worker.controller import InstanceController
from worker.utils.database import SyncPostgreSQLController
from worker.models import AnalyzeRequest
from worker.utils.wrapper import exception_manager

from worker.analysis.ndvi import NDVIAnalyzer

from logging import Logger


class Master:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Master, cls).__new__(cls)
        return cls.__instance

    def __init__(
        self,
        node_name: str,
        workers: int,
        database: SyncPostgreSQLController,
        logger: Logger,
        current_directory: str
    ):
        credentials = pika.PlainCredentials(config.AMQP_USERNAME, config.AMQP_PASSWORD)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.AMQP_HOST,
                port=config.AMQP_PORT,
                virtual_host=config.AMQP_VIRTUALHOST,
                credentials=credentials,
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=config.AMQP_QUEUE)
        self.controller: InstanceController = InstanceController.get_controller(
            node_name, workers, logger, current_directory
        )
        self.database = database

        self.logger: Logger = logger

        self.controller.run()

        Master.__instance = self

    @classmethod
    def get_master(cls) -> "Master":
        return cls.__instance

    def get_task_by_id(self, task_id: str):
        context = self.database()
        with context as session:
            obj = session.get(AnalyzeRequest, task_id)
        return obj

    # @exception_manager
    @staticmethod
    def define_analysis_type(request: AnalyzeRequest):
        if request.origin_ndvi_data and request.origin_plants_data:
            return AnalysisType.both
        elif request.origin_ndvi_data and not request.origin_plants_data:
            return AnalysisType.ndvi
        elif request.origin_plants_data and not request.origin_ndvi_data:
            return AnalysisType.neural
        else:
            raise Exception("Task was not defined what to do")

    def get_instance_by_type(self, ttype: AnalysisType, current_hash: str):
        if ttype == AnalysisType.ndvi:
            return NDVIAnalyzer(self.logger, self.database, current_hash)

    @staticmethod
    def on_message(channel, method, properties, body: bytes):
        print(f"Received {body}")
        task = body.decode()
        print(f"Task id is {task}")
        master = Master.get_master()
        task = master.get_task_by_id(task)
        ttype = master.define_analysis_type(request=task)
        master.controller.send_task(ttype, task)

    def run(self):
        print("Started consuming")
        self.channel.basic_consume(
            queue=config.AMQP_QUEUE,
            on_message_callback=Master.on_message,
            auto_ack=True,
        )
        self.channel.start_consuming()
