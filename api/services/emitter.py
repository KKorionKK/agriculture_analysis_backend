import aio_pika
from api import config
from api.common.vigilante import Vigilante


class Emitter:
    def __init__(self, vigilante: Vigilante):
        self.logger = vigilante.get_logger()

    async def send_task(self, request_id: str):
        self.logger.info("Initiating connection")
        connection = await aio_pika.connect_robust(
            f"amqp://{config.AMQP_USERNAME}:{config.AMQP_PASSWORD}@{config.AMQP_HOST}:{config.AMQP_PORT}{config.AMQP_VIRTUALHOST}",
        )
        async with connection:
            channel = await connection.channel()
            self.logger.info(f"Publishing task: {request_id}")
            await channel.default_exchange.publish(
                aio_pika.Message(body=request_id.encode()),
                routing_key=config.AMQP_QUEUE,
            )
            self.logger.info(f"Sent task: {request_id}")
